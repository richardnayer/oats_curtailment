from pyomo.environ import *
from functools import reduce
from operator import mul
from typing import List, Dict, Tuple, Union
import inspect
import logging

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
    #Take index definition from dictionary, and resolve into required input to create the pyomo model
    if defined_index is None:
        return None
    if isinstance(defined_index, str):
        return getattr(instance, defined_index)
    if isinstance(defined_index, tuple):
        return reduce(mul, (getattr(instance,index_set) for index_set in defined_index))
    else:
        return defined_index

def _within_resolver(instance, defined_within):
    if defined_within is None: #If defined as None return none
        return None
    if isinstance(defined_within, str): #If is a string then return instance.str
        return getattr(instance, defined_within)
    if isinstance(defined_within, tuple): #If tuple then return cartesian produce of instance.tuple[1] * instance.tuple[2] etc
        return reduce(mul, (getattr(instance,index_set) for index_set in defined_within))
    else:
        return defined_within

def add_sets_to_instance(instance: object, sets_dict_obj: dict, set_list: list = None):
    '''
    Function to add sets to a pyomo model instance.
    '''
    if set_list is None:
        set_list = sets_dict_obj.blocks.keys()
    
    for set_name in set_list:
        set_def = sets_dict_obj.blocks.get(set_name)
        set_type = set_def.get('type', 'flat')
        dimen = set_def.get('dimen', 1)
        index = _index_resolver(instance, set_def.get('index', None))
        within = _within_resolver(instance, set_def.get('within', None))
        initialize = _initialize_resolver(set_def.get('initialize'))

        print(set_name, set_type, dimen, within, initialize)

        component = None
        if index is not None:
            component = Set(
                index,
                within = within,
                initialize=initialize,
                dimen=dimen,
            )

        else:
            component = Set(
                within = within,
                initialize=initialize,
                dimen=dimen,
            )
        
        #Check if component exists yet, and if it does then replace it
        if hasattr(instance, set_name):
            instance.del_component(getattr(instance, set_name))
            logger.info(f"Deleted and redefined set component {set_name}")
        instance.add_component(set_name, component)

def add_params_to_instance(instance:object, param_dict_obj: dict, param_list: list = None):     
    all_defined_params = list(param_dict_obj.blocks.keys())

    if param_list is None:
        param_list = all_defined_params

    for param_name in param_list:
        if param_name not in all_defined_params:
            raise KeyError(f"Constraint '{param_name}' not found in block '{all_defined_params}'")

        param_def = param_dict_obj.blocks.get(param_name)
        index = _index_resolver(instance, param_def.get('index', None))
        within = _within_resolver(instance, param_def.get('within', None))
        initialize = _initialize_resolver(param_def.get('initialize', None))
        mutable = param_def.get('mutable', False)

        component = None
        if index is not None:
            component = Param(
                index,
                within = within,
                initialize = initialize,
                mutable = mutable
            )

        else:
            component = Param(
                within = within,
                initialize = initialize,
                mutable = mutable
            )

        #Check if component exists yet, and if it does then replace it
        if hasattr(instance, param_name):
            instance.del_component(getattr(instance, param_name))
            logger.info(f"Deleted and redefined parameter component {param_name}")
        instance.add_component(param_name, component)
    
def add_variables_to_instance(instance:object, variable_dict_obj: dict, variable_list: list = None):     
    all_defined_variables = list(variable_dict_obj.blocks.keys())

    if variable_list is None:
        variable_list = all_defined_variables

    for variable_name in variable_list:
        if variable_name not in all_defined_variables:
            raise KeyError(f"Constraint '{variable_name}' not found in block '{all_defined_variables}'")

        variable_def = variable_dict_obj.blocks.get(variable_name)
        index = _index_resolver(instance, variable_def.get('index', None))
        domain = variable_def.get('domain', None)
        bounds = variable_def.get('bounds', None)
        initialize = _initialize_resolver(variable_def.get('initialize', None))

        print(variable_name, index, domain, initialize)

        component = None
        if index is not None:
            component = Var(
                index,
                domain = domain,
                bounds = bounds,
                initialize=initialize,
            )

        else:
            component = Var(
                domain = domain,
                bounds = bounds,
                initialize=initialize,
            )
        
        #Check if component exists yet, and if it does then replace it
        if hasattr(instance, variable_name):
            instance.del_component(getattr(instance, variable_name))
            logger.info(f"Deleted and redefined variable component {variable_name}")
        instance.add_component(variable_name, component)
    
def add_constraints_to_instance(instance: object, constraint_dict_obj: dict, constraint_list: list = None):
    all_defined_constraints = list(constraint_dict_obj.blocks.keys())

    if constraint_list is None:
        constraint_list = all_defined_constraints

    for constraint_name in constraint_list:
        if constraint_name not in all_defined_constraints:
            raise KeyError(f"Constraint '{constraint_name}' not found in block '{all_defined_constraints}'")

        constraint_def = constraint_dict_obj.blocks.get(constraint_name)
        index = _index_resolver(instance, constraint_def.get('index', None))
        rule = constraint_def.get('rule', None)

        print(constraint_name, index, rule)

        component = None
        if index is not None:
            component = Constraint(
                index,
                rule = rule,
            )
        else:
            component = Constraint(
                rule = rule,
            )

        #Check if component exists yet, and if it does then replace it
        if hasattr(instance, constraint_name):
            instance.del_component(getattr(instance, constraint_name))
            logger.info(f"Deleted and redefined constraint component {constraint_name}")
        instance.add_component(constraint_name, component)

def remove_component_from_instance(instance: object, component_list: list):
    for set_name in component_list:
        if hasattr(instance, set_name):
            instance.del_component(getattr(instance,set_name))
        else:
            raise KeyError(f"Set '{set_name}' cannot be deleted as it does not exist in the instance")
