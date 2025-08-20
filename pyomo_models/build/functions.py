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
from enum import Enum

from pyomo.environ import *  # noqa: F401,F403 - re-export Pyomo classes
from .names import ComponentName
from .definitions import (
    Sets_Blocks,
    Params_Blocks,
    Variables_Blocks,
    Constraint_Blocks,
)

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


def remove_component_from_instance(instance: Any, component_list: Iterable[str]) -> None:
    """Remove components from a model instance."""

    for name in component_list:
        if hasattr(instance, name):
            instance.del_component(getattr(instance, name))
        else:
            raise KeyError(
                f"Set '{name}' cannot be deleted as it does not exist in the instance"
            )


# --- Snapshot DCOPF component groups -------------------------------------

SNAPSHOT_DCOPF_SETS = [
    ComponentName.B,
    ComponentName.b0,
    ComponentName.G,
    ComponentName.generator_mapping,
    ComponentName.G_LIFO,
    ComponentName.G_LIFO_pairs,
    ComponentName.G_prorata,
    ComponentName.G_prorata_map,
    ComponentName.G_prorata_pairs,
    ComponentName.G_individual,
    ComponentName.G_uncontrollable,
    ComponentName.prorata_groups,
    ComponentName.L,
    ComponentName.bus_line_in,
    ComponentName.bus_line_out,
    ComponentName.line_busses,
    ComponentName.TRANSF,
    ComponentName.bus_transformer_in,
    ComponentName.bus_transformer_out,
    ComponentName.transformer_busses,
    ComponentName.D,
    ComponentName.DNeg,
    ComponentName.demand_bus_mapping,
]

SNAPSHOT_DCOPF_PARAMS = [
    ComponentName.line_max_continuous_P,
    ComponentName.line_susceptance,
    ComponentName.line_reactance,
    ComponentName.transformer_max_continuous_P,
    ComponentName.transformer_susceptance,
    ComponentName.transformer_reactance,
    ComponentName.PD,
    ComponentName.VOLL,
    ComponentName.PGmax,
    ComponentName.PGmin,
    ComponentName.c0,
    ComponentName.c1,
    ComponentName.bid,
    ComponentName.baseMVA,
]

SNAPSHOT_DCOPF_VARIABLES = [
    ComponentName.pG,
    ComponentName.pD,
    ComponentName.alpha,
    ComponentName.zeta_cg,
    ComponentName.zeta_wind,
    ComponentName.zeta_bin,
    ComponentName.minimum_zeta,
    ComponentName.gamma,
    ComponentName.beta,
    ComponentName.deltaL,
    ComponentName.deltaLT,
    ComponentName.delta,
    ComponentName.pL,
    ComponentName.pLT,
]

SNAPSHOT_DCOPF_NETWORK_CONSTRAINTS = [
    ComponentName.KCL_networked_realpower_noshunt,
    ComponentName.KVL_DCOPF_lines,
    ComponentName.KVL_DCOPF_transformer,
    ComponentName.demand_real_alpha_controlled,
    ComponentName.demand_alpha_max,
    ComponentName.demand_alpha_fixneg,
    ComponentName.line_cont_realpower_max_pstve,
    ComponentName.line_cont_realpower_max_ngtve,
    ComponentName.volts_line_delta,
    ComponentName.transf_continuous_real_max_pstve,
    ComponentName.transf_continuous_real_max_ngtve,
    ComponentName.volts_transformer_delta,
    ComponentName.volts_reference_bus,
]

SNAPSHOT_DCOPF_LIFO_CONSTRAINTS = [
    ComponentName.gen_LIFO_realpower_max,
    ComponentName.gen_LIFO_realpower_min,
    ComponentName.gen_LIFO_gamma,
    ComponentName.gen_LIFO_beta,
]

SNAPSHOT_DCOPF_PRORATA_CONSTRAINTS = [
    ComponentName.gen_prorata_realpower_max,
    ComponentName.gen_prorata_realpower_min,
    ComponentName.gen_prorata_realpower_min_zeta,
    ComponentName.gen_prorata_zeta_max,
    ComponentName.gen_prorata_zeta_min,
    ComponentName.gen_prorata_zeta_binary,
]

SNAPSHOT_DCOPF_INDIVIDUAL_CONSTRAINTS = [
    ComponentName.gen_individual_realpower_max,
    ComponentName.gen_individual_realpower_min,
]

SNAPSHOT_DCOPF_UNCONTROLLABLE_CONSTRAINTS = [
    ComponentName.gen_uncontrollable_realpower_sp,
]


def build_snapshot_dcopf_sets(instance: Any, case: Any) -> Any:
    """Populate ``instance`` with snapshot DCOPF set components."""

    set_blocks = Sets_Blocks(case).blocks
    set_defs = [SimpleNamespace(name=n, **asdict(set_blocks[n])) for n in SNAPSHOT_DCOPF_SETS]
    add_sets_to_instance(instance, set_defs)
    return instance


def build_snapshot_dcopf_params(instance: Any, case: Any) -> Any:
    """Populate ``instance`` with snapshot DCOPF parameter components."""

    param_blocks = Params_Blocks(case).blocks
    param_defs = [SimpleNamespace(name=n, **asdict(param_blocks[n])) for n in SNAPSHOT_DCOPF_PARAMS]
    add_params_to_instance(instance, param_defs)
    return instance


def build_snapshot_dcopf_variables(instance: Any) -> Any:
    """Populate ``instance`` with snapshot DCOPF variable components."""

    var_blocks = Variables_Blocks(instance).blocks
    var_defs = [SimpleNamespace(name=n, **asdict(var_blocks[n])) for n in SNAPSHOT_DCOPF_VARIABLES]
    add_variables_to_instance(instance, var_defs)
    return instance


def build_snapshot_dcopf_constraints(instance: Any) -> Any:
    """Populate ``instance`` with snapshot DCOPF constraint components."""

    constraints_list = list(SNAPSHOT_DCOPF_NETWORK_CONSTRAINTS)
    if [g for g in instance.G_LIFO] != []:
        constraints_list += SNAPSHOT_DCOPF_LIFO_CONSTRAINTS
    if [g for g in instance.G_prorata] != []:
        constraints_list += SNAPSHOT_DCOPF_PRORATA_CONSTRAINTS
    if [g for g in instance.G_individual] != []:
        constraints_list += SNAPSHOT_DCOPF_INDIVIDUAL_CONSTRAINTS
    if [g for g in instance.G_uncontrollable] != []:
        constraints_list += SNAPSHOT_DCOPF_UNCONTROLLABLE_CONSTRAINTS

    constraint_blocks = Constraint_Blocks(instance).blocks
    constraint_defs = [
        SimpleNamespace(name=n, **asdict(constraint_blocks[n])) for n in constraints_list
    ]
    add_constraints_to_instance(instance, constraint_defs)
    return instance

