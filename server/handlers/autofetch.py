from cjworkbench.models.userprofile import UserProfile
from cjwstate.models import Workflow, WfModule


def isoformat(dt) -> str:
    return dt.isoformat()[: -len("000+00:00")] + "Z"


def list_autofetches_json(scope):
    """
    List all the scope's user's autofetches.

    This runs a database query. Use @database_sync_to_async around it.
    """
    autofetches = list(
        WfModule.objects.filter(
            auto_update_data=True,
            is_deleted=False,
            tab__is_deleted=False,
            tab__workflow_id__in=Workflow.owned_by_user_session(
                scope["user"], scope["session"]
            ),
        )
        .order_by("update_interval", "tab__workflow__creation_date", "tab__id", "id")
        .values(
            "tab__workflow_id",
            "tab__workflow__name",
            "tab__workflow__creation_date",
            "tab__workflow__last_viewed_at",
            "tab__slug",
            "tab__name",
            "id",
            "order",
            "update_interval",
        )
    )

    default_max_fetches_per_day = UserProfile._meta.get_field(
        "max_fetches_per_day"
    ).default
    if not scope["user"].is_anonymous:
        try:
            max_fetches_per_day = scope["user"].user_profile.max_fetches_per_day
        except UserProfile.DoesNotExist:
            max_fetches_per_day = default_max_fetches_per_day
    else:
        max_fetches_per_day = default_max_fetches_per_day
    n_fetches_per_day = sum([86400.0 / row["update_interval"] for row in autofetches])

    return {
        "maxFetchesPerDay": max_fetches_per_day,
        "nFetchesPerDay": n_fetches_per_day,
        "autofetches": [
            {
                "workflow": {
                    "id": row["tab__workflow_id"],
                    "name": row["tab__workflow__name"],
                    "createdAt": (isoformat(row["tab__workflow__creation_date"])),
                    "lastViewedAt": (isoformat(row["tab__workflow__last_viewed_at"])),
                },
                "tab": {"slug": row["tab__slug"], "name": row["tab__name"]},
                "wfModule": {
                    "id": row["id"],
                    "order": row["order"],
                    "fetchInterval": row["update_interval"],
                },
            }
            for row in autofetches
        ],
    }
