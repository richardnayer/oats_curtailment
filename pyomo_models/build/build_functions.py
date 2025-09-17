"""Utility helpers for building Pyomo models.

These helpers allow model components to be defined using dataclasses and
``Enum`` members rather than raw strings.  Each dataclass is expected to provide
at least a ``name`` attribute which is used when creating or replacing the
component on a model instance.
"""

from __future__ import annotations

from dataclasses import asdict
from functools import reduce
from operator import mul
from typing import Any, Iterable
from types import SimpleNamespace
import inspect
import logging
import numpy as np
from enum import Enum

from pyomo.environ import *  # noqa: F401,F403 - re-export Pyomo classes
from .names import ComponentName
from .definitions import (
    Sets_Blocks,
    Params_Blocks,
    Variables_Blocks,
    Constraint_Blocks,
)
from data_io import helpers

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)


def _initialize_resolver(defined_initialize: Any) -> Any:
    """Return a value or callable suitable for Pyomo initialisation."""

    if callable(defined_initialize):
        sig = inspect.signature(defined_initialize)
        return defined_initialize() if len(sig.parameters) == 0 else defined_initialize
    return defined_initialize

def _resolve_component(
    instance: Any, source: ComponentName | Enum | str | Any
) -> Any:
    """Return a component from ``instance`` based on ``source``.

    ``source`` may be a :class:`ComponentName`, any other :class:`Enum`
    member, an object with a ``name`` attribute (e.g., a dataclass describing
    a component) or a raw string. Any other object is returned unchanged.
    """

    if isinstance(source, Enum):
        return getattr(instance, source.value)
    if isinstance(source, str):
        return getattr(instance, source)
    if hasattr(source, "name"):
        name = getattr(source, "name")
        if isinstance(name, Enum):
            name = name.value
        try:
            return getattr(instance, name)
        except AttributeError:
            return source
    return source

def _index_resolver(instance: Any, defined_index: Any) -> Any:
    """Resolve index definitions into Pyomo objects."""

    if defined_index is None:
        return None
    if isinstance(defined_index, tuple):
        resolved = [_resolve_component(instance, idx) for idx in defined_index]
        return reduce(mul, resolved)
    return _resolve_component(instance, defined_index)

def _within_resolver(instance: Any, defined_within: Any) -> Any:
    """Resolve within definitions into Pyomo sets."""

    if defined_within is None:
        return None
    if isinstance(defined_within, tuple):
        resolved = [_resolve_component(instance, idx) for idx in defined_within]
        return reduce(mul, resolved)
    return _resolve_component(instance, defined_within)

def _name_to_str(name_obj: Any) -> str:
    """Convert a dataclass or Enum ``name`` attribute to a string."""

    return name_obj.value if isinstance(name_obj, Enum) else str(name_obj)

def add_sets_to_instance(instance: Any, set_defs: Iterable[Any]) -> None:
    """Add sets defined by dataclass objects to a model instance."""

    for set_def in set_defs:
        dimen = getattr(set_def, "dimen", 1)
        index = _index_resolver(instance, getattr(set_def, "index", None))
        within = _within_resolver(instance, getattr(set_def, "within", None))
        initialize = _initialize_resolver(getattr(set_def, "initialize", None))

        if index is not None:
            component = Set(index, within=within, initialize=initialize, dimen=dimen)
        else:
            component = Set(within=within, initialize=initialize, dimen=dimen)

        name_str = _name_to_str(getattr(set_def, "name"))
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(f"Deleted and redefined set component {name_str}")
        instance.add_component(name_str, component)

def add_iteration_sets_to_instance(instance: Any, case: Any, set_list: list[Any], iteration: int) -> None:
    set_functions = {
        ComponentName.L_nonzero: {"dimen": 1,
                                  "index": None,
                                  "within": ComponentName.L,
                                  "initialize": lambda: helpers.get_ts_param_index_list(case, "ts_Lmax", iteration, ">", 0)
                                  },

        ComponentName.TRANSF_nonzero: {"dimen": 1,
                                       "index": None,
                                       "within": ComponentName.TRANSF,
                                       "initialize":lambda: helpers.get_ts_param_index_list(case, "ts_TLmax", iteration, ">", 0)
                                       }
    }

    for sett in set_list:
        if sett in set_functions.keys():
            name = _name_to_str(sett)
            dimen = set_functions.get(sett).get("dimen", 1)
            index = _index_resolver(instance, set_functions.get(sett).get("index", None))
            within = _within_resolver(instance, set_functions.get(sett).get("within", None))
            initialize = _initialize_resolver(set_functions.get(sett).get("initialize", None))

            if index is not None:
                component = Set(index, within=within, initialize=initialize, dimen=dimen)
            else:
                component = Set(within=within, initialize=initialize, dimen=dimen)

            if hasattr(instance, name):
                instance.del_component(getattr(instance, name))
                logger.info(f"Deleted and redefined set component {name}")
            instance.add_component(name, component)


def add_params_to_instance(instance: Any, param_defs: Iterable[Any]) -> None:
    """Add parameters defined by dataclass objects to a model instance."""

    for param_def in param_defs:
        index = _index_resolver(instance, getattr(param_def, "index", None))
        within = _within_resolver(instance, getattr(param_def, "within", None))
        initialize = _initialize_resolver(getattr(param_def, "initialize", None))
        mutable = getattr(param_def, "mutable", False)

        if index is not None:
            component = Param(index, within=within, initialize=initialize, mutable=mutable)
        else:
            component = Param(within=within, initialize=initialize, mutable=mutable)

        name_str = _name_to_str(getattr(param_def, "name"))
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(f"Deleted and redefined parameter component {name_str}")
        instance.add_component(name_str, component)

def add_iteration_params_to_instance(instance: Any, case: Any, param_list: list[Any], iteration: int) -> None:
    '''
    Function to update paramaters within an instance for a certain iteration, when an iterative model is being used.
    '''
    param_functions = {
        ComponentName.PD: lambda: helpers.get_ts_param_dict(case, "ts_PD", iteration, baseMVA = case.baseMVA),
        ComponentName.VOLL: lambda: helpers.get_ts_param_dict(case, "ts_VOLL", iteration),
        ComponentName.line_max_continuous_P: lambda: helpers.get_ts_param_dict(case, "ts_Lmax", iteration, baseMVA = case.baseMVA),
        ComponentName.transformer_max_continuous_P: lambda: helpers.get_ts_param_dict(case, "ts_TLmax", iteration, baseMVA = case.baseMVA),
        # ComponentName.PGMINGEN: lambda: helpers.get_ts_param_dict(case, "ts_PGMINGEN", iteration, baseMVA = case.baseMVA),
        ComponentName.PGmin: lambda: helpers.get_ts_param_dict(case, "ts_PGLB", iteration, baseMVA = case.baseMVA),
        ComponentName.PGmax: lambda: helpers.get_ts_param_dict(case, "ts_PGUB", iteration, baseMVA = case.baseMVA),
        ComponentName.c_bid: lambda: helpers.get_ts_param_dict(case, "ts_bid", iteration),
    }


    for param in param_list:
        if param in param_functions.keys():
            getattr(instance, param).store_values(param_functions[param]())
        else:
            raise KeyError(f"{param} is not defined as an iterative parameter. Please ensure it is defined in the add_iteration_params_to_instance() functions internal dict")

def add_variables_to_instance(instance: Any, variable_defs: Iterable[Any]) -> None:
    """Add variables defined by dataclass objects to a model instance."""

    for variable_def in variable_defs:
        index = _index_resolver(instance, getattr(variable_def, "index", None))
        domain = getattr(variable_def, "domain", None)
        bounds = getattr(variable_def, "bounds", None)
        initialize = _initialize_resolver(getattr(variable_def, "initialize", None))

        if index is not None:
            component = Var(index, domain=domain, bounds=bounds, initialize=initialize)
        else:
            component = Var(domain=domain, bounds=bounds, initialize=initialize)

        name_str = _name_to_str(getattr(variable_def, "name"))
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(f"Deleted and redefined variable component {name_str}")
        instance.add_component(name_str, component)

def add_constraints_to_instance(instance: Any, constraint_defs: Iterable[Any]) -> None:
    """Add constraints defined by dataclass objects to a model instance."""

    for constraint_def in constraint_defs:
        index = _index_resolver(instance, getattr(constraint_def, "index", None))
        rule = getattr(constraint_def, "rule")

        if index is not None:
            component = Constraint(index, rule=rule)
        else:
            component = Constraint(rule=rule)

        name_str = _name_to_str(getattr(constraint_def, "name"))
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(f"Deleted and redefined constraint component {name_str}")
        instance.add_component(name_str, component)

def remove_component_from_instance(instance: Any, component_list: Iterable[str], skip_missing = False) -> None:
    """Remove components from a model instance."""

    for name in component_list:
        if hasattr(instance, name):
            instance.del_component(getattr(instance, name))
        elif skip_missing == True:
            continue
        else:
            raise KeyError(
                f"Set '{name}' cannot be deleted as it does not exist in the instance"
            )

def build_sets(instance: Any, case: Any, setlist: Iterable[Any]) -> Any:
    """Populate ``instance`` with listed components."""

    set_blocks = Sets_Blocks(case).blocks
    set_defs = [SimpleNamespace(name=n, **asdict(set_blocks[n])) for n in setlist]
    add_sets_to_instance(instance, set_defs)
    return instance

def build_params(instance: Any, case: Any, paramlist: Iterable[Any]) -> Any:
    """Populate ``instance`` with listed parameter components."""

    param_blocks = Params_Blocks(case).blocks
    param_defs = [SimpleNamespace(name=n, **asdict(param_blocks[n])) for n in paramlist]
    add_params_to_instance(instance, param_defs)
    return instance

def build_variables(instance: Any, varlist: Iterable[Any]) -> Any:
    """Populate ``instance`` with listed variable components."""

    var_blocks = Variables_Blocks(instance).blocks
    var_defs = [SimpleNamespace(name=n, **asdict(var_blocks[n])) for n in varlist]
    add_variables_to_instance(instance, var_defs)
    return instance

def build_constraints(instance: Any, constraintlist: Iterable[Any]) -> Any:
    """Populate ``instance`` with listed constraint components."""

    constraint_blocks = Constraint_Blocks(instance).blocks
    constraint_defs = [SimpleNamespace(name=n, **asdict(constraint_blocks[n])) for n in constraintlist]
    add_constraints_to_instance(instance, constraint_defs)
    return instance

