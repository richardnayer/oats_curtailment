from typing import List, Dict, Tuple, Union
import pandas as pd
import itertools as it
import numpy as np

def get_filtered_df(case: object, component: str, filter_param: Union[str, float, int], operation: str, filter_value: Union[str, float,int], returned_params: list = None):
    '''
    Utility to create a filtered dataframe. Supported operations are defined, and checks are made to ensure that parameters
    are included within the component dataset. Existence of the component is not confirmed in this function.

    Uses numpy arrays to create a boolean mask, which is then converted into indices to reduce runtime by using .loc to give df views.
    '''
    
    #Define supported operations
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    #Get Dataframe    
    df = getattr(case,component)

    #Check that all filters are set if one is set.
    if any(param is None for param in [filter_param, operation, filter_value]) and not all(param is None for param in [filter_param, operation, filter_value]):
        raise ValueError("If any of filter_param, operation, or filter_value is set, all must be provided.")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise ValueError(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")

    #Check filter parameters exist in dataframe
    for param in [filter_param] + (returned_params or []):
        if param not in df.columns and param is not None:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data") 

    #Check filter_param and filter types are numeric if required
    if operation in ['>=', '>', '<=', '<']:
        if not pd.api.types.is_numeric_dtype(df[filter_param]):
            raise TypeError(f"The column '{filter_param}' must be numeric for operation '{operation}'")
        if not isinstance(filter_value, (int, float)):
            raise TypeError(f"The filter_value must be int or float for operation '{operation}'")
    
    #If no operation return df (with or without specific columns)
    if operation is None:
        return df if returned_params is None else df.loc[:, returned_params]
    
    #Else define a mask based on a numpy of the filter_param column of the df
    else:
        col = df[filter_param].to_numpy()
        if operation == '=':
            mask = col == filter_value
        elif operation == '!=':
            mask = col != filter_value
        elif operation == '>=':
            mask = col >= filter_value
        elif operation == '>':
            mask = col > filter_value
        elif operation == '<=':
            mask = col <= filter_value
        elif operation == '<':
            mask = col < filter_value
        else:
            raise ValueError(f"Unsupported operation '{operation}'")
        
        #Define indices for filtering rows and return filtered dataframe. Column indices generated if returned_params have been defined.
        filter_indices = np.flatnonzero(mask)
        return df.iloc[filter_indices] if returned_params is None else df.iloc[filter_indices, [df.columns.get_loc(c) for c in returned_params]]

def get_PerUnit_param_dict(case: object, component: str, index:str , param: float, baseMVA: float, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> Dict[str, float]:
    '''Return a dict mapping the index (e.g. generator name) to parameter scaled against baseMVA'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [index,param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filter df and return dictionary
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [index,param])
    return filtered_df.set_index(index)[param].div(baseMVA).to_dict()

def get_PerUnit_param_list(case: object, component: str, param: float, baseMVA: float, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> List[float]:
    '''Return a list mapping the index (e.g. generator name) to parameter scaled against baseMVA'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    if param not in df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    
    #Filter df and return list
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [param])
    return filtered_df[param].div(baseMVA).to_list()

def get_param_list(case: object, component: str, param: Union[str,float,int], filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> List[Union[str, float, int]]:
    '''Return list of components, optionally filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    if param not in df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filter df and return list
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [param])
    return filtered_df[param].to_list()
    
def get_param_dict(case: object, component: str, index: str, param: Union[str,float,int], filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> Dict[List[Union[str, float, int]], Union[str, float, int]]:
    '''Return list of components filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [index, param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filter df and return list
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [index, param])
    return filtered_df.set_index(index)[param].to_dict()
        
def component_map_complete_dict(case: object,
                                key_component: str,
                                key_param: str,
                                val_component: str,
                                val_param: str,
                                merge_param: str,
                                filter_param: Union[str, float, int] = None,
                                operation: str = None,
                                filter_value: Union[str, float,int] = None) \
                                -> Dict[str, List[str]]:
    '''
    Function creates a map of one type of components (val) against another type of component (key). It produces a dict
    with the key_param as the key (e.g. bus), with the value being a list of all val_param (e.g. generators) that have been identified
    as belonging to the key_component by the merge_param (e.g. bus_name in the generators spreadsheet).

    Parameters
    ----------
    case: case object
    key_component: component that should be mapped against
    key_param: key_component parameter that should form keys of the dictionary
    val_component: component that should be mapped against the key_component
    val_param: val_component parameter that will form lists of values in the dictionary
    val_key_param: val_component parameter tat links val_components to key_param (column on which merge is made)
    '''

    #Check if components exists
    for component in [key_component, val_component]:
        if not hasattr(case, component):
            raise AttributeError(f"Case object has no component '{component}'")
    
    val_df = getattr(case, val_component)
    key_df = getattr(case, key_component)

    #Check parameters exist in key_component
    if key_param not in key_df.columns:
        raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    #Check parameters exist in val_component
    for param in [val_param, merge_param]:
        if param not in val_df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filter df and return list
    filtered_val_df = get_filtered_df(case, component, filter_param, operation, filter_value, [val_param, merge_param])

    key_component_map = filtered_val_df.groupby(merge_param)[val_param].apply(list).to_dict()
    for component in key_df[key_param]:
        key_component_map.setdefault(component, [])
    
    return key_component_map

def comma_param_to_list(case: object, component: str, comma_param: str, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> List[Union[str, float, int]]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)
    
    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in '{component}' data")

    #Filter df and return list
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value)
    return filtered_df[comma_param]\
                .dropna()\
                .str.split(',')\
                .explode()\
                .str.strip()\
                .unique()\
                .tolist()\

def comma_param_to_dict(case: object, component: str, index: str, comma_param: str, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> Dict[str, tuple]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    df = getattr(case, component)

    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in '{component}' data")

    #Filter df
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [index, comma_param])
           
    return filtered_df\
                    .set_index(index)[comma_param]\
                    .dropna()\
                    .apply(lambda x: tuple(groups.strip() for groups in x.split(',')))\
                    .to_dict()

def get_ordered_groupwise_combinations(case: object, component: str, index: str, group_param: str, ordered_param: str, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None, r: int = 2) -> List[tuple]:
    '''
    Used to create ordered groupwise combinations of a parameter.
    '''
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [group_param, ordered_param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")
    #Filter df
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [index, group_param, ordered_param])
        
    sorted_groups = filtered_df.sort_values([group_param, ordered_param])
    grouped_combo_lists = sorted_groups.groupby('lifo_group')['name'].apply(lambda x: list(it.combinations(x,r))).to_list()
    flat_combo_list = [combo for sublist in grouped_combo_lists for combo in sublist]
        
    return flat_combo_list

def get_zipped_param_list(case: object, component: str, index: str, zip_params: list, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None) -> Dict[str,tuple]:
    '''Return list of components filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    df = getattr(case, component)

    #Check parameters exist in df
    for param in zip_params:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Filtered df
    filtered_df = get_filtered_df(case, component, filter_param, operation, filter_value, [index]+zip_params)

    return dict(zip(filtered_df[index] , zip(*(filtered_df[param] for param in zip_params))))

def get_paired_params_list(case, component, param_1, param_2, param_2_comma = False, filter_param: Union[str, float, int] = None, operation: str = None, filter_value: Union[str, float,int] = None):
    '''Return list of components filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [param_1, param_2]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")   
    
    #Get Dictionary
    if param_2_comma == True:
        dictionary = comma_param_to_dict(case, component, param_1, param_2, filter_param, operation, filter_value)
    else:
        dictionary = get_param_dict(case, component, param_1, param_2, filter_param, operation, filter_value)
    
    #Flatten List
    return [(param_1, param_2_item) for param_1, param_2 in dictionary.items() for param_2_item in param_2]