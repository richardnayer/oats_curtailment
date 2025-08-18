from pyomo.environ import *
from functools import reduce
from operator import mul
from typing import List, Dict, Tuple, Union
import inspect
import logging

from .definitions import ComponentName, SetDef, VarDef, ConstraintDef, ParamDef
from enum import Enum

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)  # Change to DEBUG for more details
handler = logging.StreamHandler()
formatter = logging.Formatter('%(asctime)s [%(levelname)s] %(message)s')
handler.setFormatter(formatter)
logger.addHandler(handler)


def _initialize_resolver(defined_initialize):
    #Take function or value defined in set_initialize and check if callable.
    #If callable then call using brackets if no parameters, or without if >0 parameters defined
    #If not collable then return as is.
    if callable(defined_initialize):
        sig = inspect.signature(defined_initialize)
        if len(sig.parameters) == 0:
            return defined_initialize()
        else:
            return defined_initialize
    return defined_initialize

def _index_resolver(instance, defined_index):
    """Resolve index definitions into pyomo objects."""
    if defined_index is None:
        return None
    if isinstance(defined_index, ComponentName):
        return getattr(instance, defined_index.value)
    if isinstance(defined_index, str):
        return getattr(instance, defined_index)
    if isinstance(defined_index, tuple):
        resolved = []
        for index_set in defined_index:
            if isinstance(index_set, ComponentName):
                resolved.append(getattr(instance, index_set.value))
            elif isinstance(index_set, str):
                resolved.append(getattr(instance, index_set))
            else:
                resolved.append(index_set)
        return reduce(mul, resolved)
    return defined_index

def _within_resolver(instance, defined_within):
    """Resolve within definitions into pyomo sets."""
    if defined_within is None:
        return None
    if isinstance(defined_within, ComponentName):
        return getattr(instance, defined_within.value)
    if isinstance(defined_within, str):
        return getattr(instance, defined_within)
    if isinstance(defined_within, tuple):
        resolved = []
        for index_set in defined_within:
            if isinstance(index_set, ComponentName):
                resolved.append(getattr(instance, index_set.value))
            elif isinstance(index_set, str):
                resolved.append(getattr(instance, index_set))
            else:
                resolved.append(index_set)
        return reduce(mul, resolved)
    return defined_within

def add_sets_to_instance(
    instance: object, sets_dict_obj: object, set_list: list | None = None
):
    """Add sets defined by :class:`SetDef` objects to a model instance."""
    if set_list is None:
        set_list = list(sets_dict_obj.blocks.keys())

    resolved_names = [
        ComponentName(name) if isinstance(name, str) else name for name in set_list
    ]

    for set_name in resolved_names:
        set_def: SetDef = sets_dict_obj.blocks.get(set_name)
        dimen = set_def.dimen
        index = _index_resolver(instance, set_def.index)
        within = _within_resolver(instance, set_def.within)
        initialize = _initialize_resolver(set_def.initialize)

        if index is not None:
            component = Set(
                index,
                within=within,
                initialize=initialize,
                dimen=dimen,
            )
        else:
            component = Set(
                within=within,
                initialize=initialize,
                dimen=dimen,
            )

        name_str = set_name.value
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(f"Deleted and redefined set component {name_str}")
        instance.add_component(name_str, component)

def add_params_to_instance(
    instance: object, param_dict_obj: object, param_list: list | None = None
):
    all_defined_params = list(param_dict_obj.blocks.keys())

    if param_list is None:
        param_list = all_defined_params

    resolved_names = [
        ComponentName(name) if isinstance(name, str) else name for name in param_list
    ]

    for param_name in resolved_names:
        if param_name not in all_defined_params:
            raise KeyError(
                f"Constraint '{param_name}' not found in block '{all_defined_params}'"
            )

        param_def: ParamDef = param_dict_obj.blocks.get(param_name)
        index = _index_resolver(instance, param_def.index)
        within = _within_resolver(instance, param_def.within)
        initialize = _initialize_resolver(param_def.initialize)
        mutable = param_def.mutable

        if index is not None:
            component = Param(
                index,
                within=within,
                initialize=initialize,
                mutable=mutable,
            )
        else:
            component = Param(
                within=within,
                initialize=initialize,
                mutable=mutable,
            )

        name_str = param_name.value
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(
                f"Deleted and redefined parameter component {name_str}"
            )
        instance.add_component(name_str, component)
    
def add_variables_to_instance(
    instance: object, variable_dict_obj: object, variable_list: list | None = None
):
    all_defined_variables = list(variable_dict_obj.blocks.keys())

    if variable_list is None:
        variable_list = all_defined_variables

    resolved_names = [
        ComponentName(name) if isinstance(name, str) else name for name in variable_list
    ]

    for variable_name in resolved_names:
        if variable_name not in all_defined_variables:
            raise KeyError(
                f"Constraint '{variable_name}' not found in block '{all_defined_variables}'"
            )

        variable_def: VarDef = variable_dict_obj.blocks.get(variable_name)
        index = _index_resolver(instance, variable_def.index)
        domain = variable_def.domain
        bounds = variable_def.bounds
        initialize = _initialize_resolver(variable_def.initialize)

        if index is not None:
            component = Var(
                index,
                domain=domain,
                bounds=bounds,
                initialize=initialize,
            )
        else:
            component = Var(
                domain=domain,
                bounds=bounds,
                initialize=initialize,
            )

        name_str = variable_name.value
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(
                f"Deleted and redefined variable component {name_str}"
            )
        instance.add_component(name_str, component)
    
def add_constraints_to_instance(
    instance: object, constraint_dict_obj: object, constraint_list: list | None = None
):
    all_defined_constraints = list(constraint_dict_obj.blocks.keys())

    if constraint_list is None:
        constraint_list = all_defined_constraints

    resolved_names = [
        ComponentName(name) if isinstance(name, str) else name for name in constraint_list
    ]

    for constraint_name in resolved_names:
        if constraint_name not in all_defined_constraints:
            raise KeyError(
                f"Constraint '{constraint_name}' not found in block '{all_defined_constraints}'"
            )

        constraint_def: ConstraintDef = constraint_dict_obj.blocks.get(constraint_name)
        index = _index_resolver(instance, constraint_def.index)
        rule = constraint_def.rule

        if index is not None:
            component = Constraint(
                index,
                rule=rule,
            )
        else:
            component = Constraint(
                rule=rule,
            )

        name_str = constraint_name.value
        if hasattr(instance, name_str):
            instance.del_component(getattr(instance, name_str))
            logger.info(
                f"Deleted and redefined constraint component {name_str}"
            )
        instance.add_component(name_str, component)

def remove_component_from_instance(instance: object, component_list: list):
    for set_name in component_list:
        if hasattr(instance, set_name):
            instance.del_component(getattr(instance,set_name))
        else:
            raise KeyError(f"Set '{set_name}' cannot be deleted as it does not exist in the instance")
