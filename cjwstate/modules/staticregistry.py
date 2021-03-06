"""
Built-in Workbench modules.

These modules have the same API as external modules. We bundle each with
Workbench for at least one of these reasons:

    * We feel every Workbench user needs the module.
    * The module uses Workbench-internal APIs.
    * The module uses experimental Workbench APIs, which may change. (We keep
      it internal to pin the module code to the API code.)
    * Legacy reasons.

Defining modules
================

Modules are declared by a ".json" spec file, which must be named after the
module id_name. The ".py" file must have the same name; a ".html" file is
allowed, too.

Each module may define one or both (preferably one) of the following functions:

    def render(table: pd.DataFrame, params: Params, **kwargs):
        # kwargs is optional and may include:
        # - input_columns: Dict of .name/.type values, keyed by table.columns
        return table

    async def fetch(  # async is optional and preferred
        params: Params,
        **kwargs
    ) -> ProcessResult:
        # kwargs is optional and may include:
        # - get_input_dataframe: Callable[[], Awaitable[pd.DataFrame]]
        # - get_stored_dataframe: Callable[[], Awaitable[pd.DataFrame]]
    ) -> ProcessResult:

Looking up modules
==================

This ``registry.py`` imports all the modules automatically, finding them by
their ``.json`` spec files.

>>> import cjwstate.modules
>>> from cjwstate.modules import staticregistry
>>> cjwstate.modules.init_module_system()
>>> staticregistry.Lookup['pythoncode']  # dynamic lookup by id_name
"""
from pathlib import Path
import staticmodules
from .module_loader import ModuleSpec


Lookup = {}
Specs = {}


def _setup(kernel):
    spec_paths = list(Path(staticmodules.__file__).parent.glob("*.yaml"))
    for spec_path in spec_paths:
        spec = ModuleSpec.load_from_path(spec_path)
        assert (
            "parameters_version" in spec.data
        ), "Internal modules require a 'parameters_version'"
        id_name = spec_path.stem
        compiled_module = kernel.compile(spec_path.with_suffix(".py"), id_name)
        Lookup[id_name] = compiled_module
        Specs[id_name] = spec
