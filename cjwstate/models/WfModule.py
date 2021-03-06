import json
import logging
import secrets
from typing import Any, Dict, Optional, Union
from django.contrib.postgres.fields import JSONField
from django.db import models
from django.db.models import Q
from cjwkernel.types import I18nMessage, RenderError, TableMetadata
from cjwstate import minio
from .fields import ColumnsField, RenderErrorsField
from .CachedRenderResult import CachedRenderResult
from .module_version import ModuleVersion
from .Tab import Tab
from .workflow import Workflow
from cjwstate import clientside


logger = logging.getLogger(__name__)


class WfModule(models.Model):
    """An instance of a Module in a Workflow."""

    class Meta:
        app_label = "server"
        db_table = "server_wfmodule"
        ordering = ["order"]
        constraints = [
            models.CheckConstraint(
                check=(
                    # No way to negate F expressions. Wow.
                    # https://code.djangoproject.com/ticket/16211
                    #
                    # Instead, use a four-way truth-table approach :)
                    (Q(next_update__isnull=True) & Q(auto_update_data=False))
                    | (Q(next_update__isnull=False) & Q(auto_update_data=True))
                ),
                name="auto_update_consistency_check",
            ),
            models.CheckConstraint(
                check=(
                    (
                        Q(cached_migrated_params__isnull=True)
                        & Q(cached_migrated_params_module_version__isnull=True)
                    )
                    | (
                        Q(cached_migrated_params__isnull=False)
                        & Q(cached_migrated_params_module_version__isnull=False)
                    )
                ),
                name="cached_migrated_params_consistency_check",
            ),
            models.UniqueConstraint(
                # Really, we want WfModule slug to be unique by _workflow_, not
                # by tab. But that's not reasonable with Postgres CHECK constraints.
                # We'll do the heavy lifting in software ... and leave this
                # less-useful check as a constraint as documentation and for the index.
                fields=["tab_id", "slug"],
                name="unique_wf_module_slug",
            ),
        ]
        indexes = [
            models.Index(
                fields=["next_update"],
                name="pending_update_queue",
                condition=Q(next_update__isnull=False, is_deleted=False),
            )
        ]

    slug = models.SlugField(db_index=True)
    """
    Unique ID, generated by the client.

    Within a Workflow, each Step has a different slug. The client randomly
    generates it so that the client can queue up requests that relate to it,
    before the Step is even created in the database (i.e., before it gets an
    ID). When duplicating a Workflow, we duplicate all its Steps' slugs.

    Slugs are unique per Workflow, and non-reusable. Even after deleting a Step,
    the slug cannot be reused. (This requirement lets us use a database UNIQUE
    INDEX and support soft-deleting.)
    """

    tab = models.ForeignKey(Tab, related_name="wf_modules", on_delete=models.CASCADE)

    module_id_name = models.CharField(max_length=200, default="")

    order = models.IntegerField()

    notes = models.TextField(null=True, blank=True)

    stored_data_version = models.DateTimeField(
        null=True, blank=True
    )  # we may not have stored data

    # drives whether the module is expanded or collapsed on the front-end.
    is_collapsed = models.BooleanField(default=False, blank=False, null=False)

    is_deleted = models.BooleanField(default=False, null=False)

    # For modules that fetch data: how often do we check for updates, and do we
    # switch to latest version automatically
    auto_update_data = models.BooleanField(default=False)

    # when should next update run?
    next_update = models.DateTimeField(null=True, blank=True)
    # time in seconds between updates, default of 1 day
    update_interval = models.IntegerField(default=86400)
    last_update_check = models.DateTimeField(null=True, blank=True)

    # true means, 'email owner when output changes'
    notifications = models.BooleanField(default=False)

    # true means user has not acknowledged email
    has_unseen_notification = models.BooleanField(default=False)

    cached_migrated_params = JSONField(null=True, blank=True)
    """
    Non-secret parameter values -- after a call to migrate_params().

    This may not match the current module version. And it may be `None` for
    backwards compatibility with WfModules that did not cache migrated params.

    Why not just overwrite `params`? Because `params` is set by a user and
    `cached_migrated_params` is set by a machine, and let's not confuse our
    sources.
    """

    cached_migrated_params_module_version = models.CharField(
        max_length=200, blank=True, null=True
    )
    """
    Module-version .source_version_hash that generated cached_migrated_params.

    For internal modules (which don't have .source_version_hashes), this is
    `module_version.param_schema_version`.
    """

    cached_render_result_delta_id = models.IntegerField(null=True, blank=True)
    cached_render_result_status = models.CharField(
        null=True,
        blank=True,
        choices=[("ok", "ok"), ("error", "error"), ("unreachable", "unreachable")],
        max_length=20,
    )
    cached_render_result_errors = RenderErrorsField(blank=True, default=list)

    # should be JSONField but we need backwards-compatibility
    cached_render_result_json = models.BinaryField(blank=True)
    cached_render_result_columns = ColumnsField(null=True, blank=True)
    cached_render_result_nrows = models.IntegerField(null=True, blank=True)

    # TODO once we auto-compute stale module outputs, nix is_busy -- it will
    # be implied by the fact that the cached output revision is wrong.
    is_busy = models.BooleanField(default=False, null=False)

    # There's fetch_error and there's cached_render_result_errors.
    fetch_error = models.CharField("fetch_error", max_length=10000, blank=True)

    # Most-recent delta that may possibly affect the output of this module.
    # This isn't a ForeignKey because many deltas have a foreign key pointing
    # to the WfModule, so we'd be left with a chicken-and-egg problem.
    last_relevant_delta_id = models.IntegerField(default=0, null=False)

    params = JSONField(default=dict)
    """
    Non-secret parameter values, valid at time of writing.

    This may not match the current module version: migrate_params() will make
    the params match today's Python and JavaScript.

    These values were set by a human.
    """

    secrets = JSONField(default=dict)
    """
    Dict of {'name': ..., 'secret': ...} values that are private.

    Secret values aren't duplicated, and they're not stored in undo history.
    They have no schema: they're either set, or they're missing.

    Secrets aren't passed to `render()`: they're only passed to `fetch()`.
    """

    file_upload_api_token = models.CharField(
        max_length=100, null=True, blank=True, default=None
    )
    """
    "Authorization" header bearer token for programs to use "uploadfile".

    This may optionally be set on 'uploadfile' modules and no others. Workbench
    will allow HTTP requests with the header
    `Authorization: bearer {file_upload_api_token}` to file-upload APIs.

    Never expose this API token to readers. Only owner and writers may see it.
    """

    def __str__(self):
        # Don't use DB queries here.
        return "wf_module[%d] at position %d" % (self.id, self.order)

    @property
    def workflow(self):
        return Workflow.objects.get(tabs__wf_modules__id=self.id)

    @property
    def workflow_id(self):
        return self.tab.workflow_id

    @property
    def tab_slug(self):
        return self.tab.slug

    @property
    def uploaded_file_prefix(self):
        """
        "Folder" on S3 where uploads go.

        This ends in "/", so it can be used as a prefix in s3 operations.
        """
        return f"wf-{self.workflow_id}/wfm-{self.id}/"

    @classmethod
    def live_in_workflow(cls, workflow: Union[int, Workflow]) -> models.QuerySet:
        """
        QuerySet of not-deleted WfModules in `workflow`.

        You may specify `workflow` by its `pk` or as an object.

        Deleted WfModules and WfModules in deleted Tabs will omitted.
        """
        if isinstance(workflow, int):
            workflow_id = workflow
        else:
            workflow_id = workflow.pk

        return cls.objects.filter(
            tab__workflow_id=workflow_id, tab__is_deleted=False, is_deleted=False
        )

    @property
    def module_version(self):
        if not hasattr(self, "_module_version"):
            try:
                self._module_version = ModuleVersion.objects.latest(self.module_id_name)
            except ModuleVersion.DoesNotExist:
                self._module_version = None

        return self._module_version

    @property
    def output_status(self):
        """
        Return 'ok', 'busy', 'error' or 'unreachable'.

        'busy': render is pending
        'error': render produced an error and no table
        'unreachable': a previous module had 'error' so we will not run this
        'ok': render produced a table
        """
        crr = self.cached_render_result
        if crr is None:
            return "busy"
        else:
            return crr.status

    # ---- Authorization ----
    # User can access wf_module if they can access workflow
    def request_authorized_read(self, request):
        return self.workflow.request_authorized_read(request)

    def request_authorized_write(self, request):
        return self.workflow.request_authorized_write(request)

    def list_fetched_data_versions(self):
        return list(
            self.stored_objects.order_by("-stored_at").values_list("stored_at", "read")
        )

    @property
    def secret_metadata(self) -> Dict[str, Any]:
        """
        Return dict keyed by secret name, with values {'name': '...'}.

        Missing secrets are not included in the returned dict. Secrets are not
        validated against a schema.
        """
        return {k: {"name": v["name"]} for k, v in self.secrets.items() if v}

    # --- Duplicate ---
    # used when duplicating a whole workflow
    def duplicate_into_new_workflow(self, to_tab):
        to_workflow = to_tab.workflow

        # Slug must be unique across the entire workflow; therefore, the
        # duplicate WfModule must be on a different workflow. (If we need
        # to duplicate within the same workflow, we'll need to change the
        # slug -- different method, please.)
        assert to_tab.workflow_id != self.workflow_id
        slug = self.slug

        # to_workflow has exactly one delta, and that's the version of all
        # its modules. This is so we can cache render results. (Cached
        # render results require a delta ID.)
        last_relevant_delta_id = to_workflow.last_delta_id

        return self._duplicate_with_slug_and_delta_id(
            to_tab, slug, last_relevant_delta_id
        )

    def duplicate_into_same_workflow(self, to_tab):
        # Make sure we're calling this correctly
        assert to_tab.workflow_id == self.workflow_id

        # Generate a new slug: 9 bytes, base64-encoded, + and / becoming - and _.
        # Mimics assets/js/utils.js:generateSlug()
        slug = "step-" + secrets.token_urlsafe(9)

        # last_relevant_delta_id is _wrong_, but we need to set it to
        # something. See DuplicateTabCommand to understand the chicken-and-egg
        # dilemma.
        last_relevant_delta_id = self.last_relevant_delta_id

        return self._duplicate_with_slug_and_delta_id(
            to_tab, slug, last_relevant_delta_id
        )

    def _duplicate_with_slug_and_delta_id(self, to_tab, slug, last_relevant_delta_id):
        # Initialize but don't save
        new_step = WfModule(
            tab=to_tab,
            slug=slug,
            module_id_name=self.module_id_name,
            fetch_error=self.fetch_error,
            stored_data_version=self.stored_data_version,
            order=self.order,
            notes=self.notes,
            is_collapsed=self.is_collapsed,
            auto_update_data=False,
            next_update=None,
            update_interval=self.update_interval,
            last_update_check=self.last_update_check,
            last_relevant_delta_id=last_relevant_delta_id,
            params=self.params,
            secrets={},  # DO NOT COPY SECRETS
        )

        # Copy cached render result, if there is one.
        #
        # If we duplicate a Workflow mid-render, the cached render result might
        # not have any useful data. But that's okay: just kick off a new
        # render. The common case (all-rendered Workflow) will produce a
        # fully-rendered duplicate Workflow.
        #
        # We cannot copy the cached result if the destination Tab has a
        # different name than this one: tab_name is passed to render(), so even
        # an exactly-duplicated WfModule can have a different output.
        cached_result = self.cached_render_result
        if cached_result is not None and self.tab.name == to_tab.name:
            # assuming file-copy succeeds, copy cached results.
            new_step.cached_render_result_delta_id = new_step.last_relevant_delta_id
            for attr in ("status", "errors", "json", "columns", "nrows"):
                full_attr = f"cached_render_result_{attr}"
                setattr(new_step, full_attr, getattr(self, full_attr))

            new_step.save()  # so there is a new_step.id for parquet_key

            # Now new_step.cached_render_result will return a
            # CachedRenderResult, because all the DB values are set. It'll have
            # a .parquet_key ... but there won't be a file there (because we
            # never wrote it).
            from cjwstate.rendercache.io import BUCKET, crr_parquet_key

            old_parquet_key = crr_parquet_key(cached_result)
            new_parquet_key = crr_parquet_key(new_step.cached_render_result)

            try:
                minio.copy(
                    minio.CachedRenderResultsBucket,
                    new_parquet_key,
                    "%(Bucket)s/%(Key)s" % {"Bucket": BUCKET, "Key": old_parquet_key},
                )
            except minio.error.NoSuchKey:
                # DB and filesystem are out of sync. CachedRenderResult handles
                # such cases gracefully. So `new_result` will behave exactly
                # like `cached_result`.
                pass
        else:
            new_step.save()

        # Duplicate the current stored data only, not the history
        if self.stored_data_version is not None:
            self.stored_objects.get(stored_at=self.stored_data_version).duplicate(
                new_step
            )

        # Duplicate the "selected" file, if there is one; otherwise, duplicate
        # the most-recently-uploaded file.
        #
        # We special-case the 'upload' module because it's the only one that
        # has 'file' params right now. (If that ever changes, we'll want to
        # change a few things: upload paths should include param name, and this
        # test will need to check module_version to find the param name of the
        # file.)
        if self.module_id_name == "upload":
            uuid = self.params["file"]
            uploaded_file = self.uploaded_files.filter(uuid=uuid).first()
            if uploaded_file is not None:
                new_key = uploaded_file.key.replace(
                    self.uploaded_file_prefix, new_step.uploaded_file_prefix
                )
                assert new_key != uploaded_file.key
                # TODO handle file does not exist
                minio.copy(
                    minio.UserFilesBucket,
                    new_key,
                    f"{uploaded_file.bucket}/{uploaded_file.key}",
                )
                new_step.uploaded_files.create(
                    created_at=uploaded_file.created_at,
                    name=uploaded_file.name,
                    size=uploaded_file.size,
                    uuid=uploaded_file.uuid,
                    bucket=minio.UserFilesBucket,
                    key=new_key,
                )

        return new_step

    @property
    def cached_render_result(self) -> CachedRenderResult:
        """
        Build a CachedRenderResult with this WfModule's rendered output.

        Return `None` if there is a cached result but it is not fresh.

        This does not read the dataframe from disk. If you want a "snapshot in
        time" of the `render()` output, you need a lock, like this:

            # Lock the workflow, making sure we don't overwrite data
            with workflow.cooperative_lock():
                wf_module.refresh_from_db()
                # Read from disk
                with cjwstate.rendercache.io.open_cached_render_result(
                    wf_module.cached_render_result
                ) as result:
                    ...
        """
        result = self._build_cached_render_result_fresh_or_not()
        if result and result.delta_id != self.last_relevant_delta_id:
            return None
        return result

    def get_stale_cached_render_result(self):
        """
        Build a CachedRenderResult with this WfModule's stale rendered output.

        Return `None` if there is a cached result but it is fresh.

        This does not read the dataframe from disk. If you want a "snapshot in
        time" of the `render()` output, you need a lock, like this:

            # Lock the workflow, making sure we don't overwrite data
            with workflow.cooperative_lock():
                wf_module.refresh_from_db()
                # Read from disk
                with cjwstate.rendercache.io.open_cached_render_result(
                    wf_module.get_stale_cached_render_result()
                ) as result:
                    ...
        """
        result = self._build_cached_render_result_fresh_or_not()
        if result and result.delta_id == self.last_relevant_delta_id:
            return None
        return result

    def _build_cached_render_result_fresh_or_not(self) -> Optional[CachedRenderResult]:
        """
        Build a CachedRenderResult with this WfModule's rendered output.

        If the output is stale, return it anyway. (The return value's .delta_id
        will not match this WfModule's .delta_id.)

        This does not read the dataframe from disk. If you want a "snapshot in
        time" of the `render()` output, you need a lock, like this:

            # Lock the workflow, making sure we don't overwrite data
            with workflow.cooperative_lock():
                wf_module.refresh_from_db()
                # Read from disk
                with cjwstate.rendercache.io.open_cached_render_result(
                    wf_module.get_stale_cached_render_result()
                ) as result:
        """
        if self.cached_render_result_delta_id is None:
            return None

        delta_id = self.cached_render_result_delta_id
        status = self.cached_render_result_status
        columns = self.cached_render_result_columns
        errors = self.cached_render_result_errors
        nrows = self.cached_render_result_nrows

        # cached_render_result_json is sometimes a memoryview
        json_bytes = bytes(self.cached_render_result_json)
        if json_bytes:
            json_dict = json.loads(json_bytes)
        else:
            json_dict = {}

        return CachedRenderResult(
            workflow_id=self.workflow_id,
            wf_module_id=self.id,
            delta_id=delta_id,
            status=status,
            errors=errors,
            json=json_dict,
            table_metadata=TableMetadata(nrows, columns),
        )

    def delete(self, *args, **kwargs):
        # TODO make DB _not_ depend upon minio.
        for in_progress_upload in self.in_progress_uploads.all():
            in_progress_upload.delete_s3_data()
        minio.remove_recursive(minio.UserFilesBucket, self.uploaded_file_prefix)
        minio.remove_recursive(
            minio.CachedRenderResultsBucket,
            "wf-%d/wfm-%d/" % (self.workflow_id, self.id),
        )
        super().delete(*args, **kwargs)

    def to_clientside(self) -> clientside.StepUpdate:
        # params
        if self.module_version:
            from cjwstate.params import get_migrated_params

            param_schema = self.module_version.param_schema
            params = get_migrated_params(self)  # raise ModuleError
            try:
                param_schema.validate(params)
            except ValueError:
                logger.exception(
                    "%s.migrate_params() gave invalid output: %r",
                    self.module_id_name,
                    params,
                )
                params = param_schema.coerce(params)
        else:
            params = {}

        crr = self._build_cached_render_result_fresh_or_not()
        if crr is None:
            crr = clientside.Null

        return clientside.StepUpdate(
            id=self.id,
            slug=self.slug,
            module_slug=self.module_id_name,
            tab_slug=self.tab_slug,
            is_busy=self.is_busy,
            render_result=crr,
            files=[
                clientside.UploadedFile(
                    name=name, uuid=uuid, size=size, created_at=created_at
                )
                for name, uuid, size, created_at in self.uploaded_files.order_by(
                    "-created_at"
                ).values_list("name", "uuid", "size", "created_at")
            ],
            params=params,
            secrets=self.secret_metadata,
            is_collapsed=self.is_collapsed,
            notes=self.notes,
            is_auto_fetch=self.auto_update_data,
            fetch_interval=self.update_interval,
            last_fetched_at=self.last_update_check,
            is_notify_on_change=self.notifications,
            has_unseen_notification=self.has_unseen_notification,
            last_relevant_delta_id=self.last_relevant_delta_id,
            versions=clientside.FetchedVersionList(
                versions=[
                    clientside.FetchedVersion(created_at=created_at, is_seen=is_seen)
                    for created_at, is_seen in self.stored_objects.order_by(
                        "-stored_at"
                    ).values_list("stored_at", "read")
                ],
                selected=self.stored_data_version,
            ),
        )
