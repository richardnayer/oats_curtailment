from typing import List, Dict, Tuple, Union

def get_PerUnit_param_dict(case: object, component: str, index:str , param: float, baseMVA: float) -> Dict[str, float]:
    '''Return a dict mapping the index (e.g. generator name) to parameter scaled against baseMVA'''
    df = getattr(case, component)

    if index not in df.columns:
        raise KeyError(f"Column '{index}' not found in {component} data")
    if param not in df.columns:
        raise KeyError(f"Column '{param}' not found in {component} data")
    return df.set_index(index)[param].div(baseMVA).to_dict()

def get_PerUnit_param_list(case: object, component: str, param: float, baseMVA: float) -> List[float]:
    ''' Return a list of parameter param, divided by baseMVA'''
    
    df = getattr(case, component)
    if param not in df.columns:
        raise KeyError(f"Column '{param}' not found in {component} data")
    
    return getattr(case,component)[param].div(baseMVA).to_list()

# def get_filtered_param_list(case: object, component: str, param: str) -> List:
#     df = getattr(case, component)

#     #Check param existins in component
#     if param not in df.columns:
#         raise KeyError(f"Column '{param}' not found in {component} data")
    
#     #Return list of parameter column
#     return df[param].to_list()

def get_param_list(case: object, component: str, param: Union[str,float,int], filter_param: Union[str, float, int] = None, operation: str = None, filter: Union[str, float,int] = None) -> List[str]:
    '''Return list of components, optionally filtered by a parameter'''
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [filter_param, param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Check all filtering is None or Not None
    if None in [filter_param, operation, filter]:
        for input in [filter_param, operation, filter]:
            if input is not None:
                raise Exception(f"Some filter variables to this function are set as None")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise Exception(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    
    #Check filter_param and filter types are numeric if required
    if operation in ['>=', '>', '<=', '<'] and type(filter_param) not in [int,float] and type(filter) not in [int, float]:
        raise Exception(f"To use numerical operation {operation} the filter_param and filter data types must by int or float. Currently filter_param is {type(filter_param)} and filter is {type(filter)}")

    #Perform Operation
    match operation:
        case None:
            return df[param].to_list()

        case '=':
            return df.loc[df[filter_param] == filter, param].tolist()
        
        case '!=':
            return df.loc[df[filter_param] != filter, param].tolist()
        
        case '>=':
            return df.loc[df[filter_param] >= filter, param].tolist()
        
        case '>':
            return df.loc[df[filter_param] > filter, param].tolist()
        
        case '<=':
            return df.loc[df[filter_param] <= filter, param].tolist()

        case '<':
            return df.loc[df[filter_param] < filter, param].tolist()
    
# def get_filtered_param_dict(case: object, component: str, index:str , param: str) -> Dict[str, float]:
#     '''Return a dict mapping the index (e.g. generator name) to parameter'''
#     df = getattr(case, component)

#     if index not in df.columns:
#         raise KeyError(f"Column '{index}' not found in {component} data")
#     if param not in df.columns:
#         raise KeyError(f"Column '{param}' not found in {component} data")
    
#     return df.set_index(index)[param].to_dict()

def get_param_dict(case: object, component: str, index: str, param: Union[str,float,int], filter_param: Union[str, float, int] = None, operation: str = None, filter: Union[str, float,int] = None) -> List[str]:
    '''Return list of components filtered by a parameter'''
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [filter_param, param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Check all filtering is None or Not None
    if None in [filter_param, operation, filter]:
        for input in [filter_param, operation, filter]:
            if input is not None:
                raise Exception(f"Some filter variables to this function are set as None")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise Exception(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    
    #Check filter_param and filter types are numeric
    if operation in ['>=', '>', '<=', '<'] and type(filter_param) not in [int,float] and type(filter) not in [int, float]:
        raise Exception(f"To use numerical operation {operation} the filter_param and filter data types must by int or float. Currently filter_param is {type(filter_param)} and filter is {type(filter)}")

    #Perform Operation
    match operation:
        case None:
            return df.set_index(index)[param].to_dict()

        case '=':
            return df.loc[df[filter_param] == filter, [index, param]].set_index(index)[param].to_dict()
        
        case '!=':
            return df.loc[df[filter_param] != filter, [index, param]].set_index(index)[param].to_dict()
        
        case '>=':
            return df.loc[df[filter_param] >= filter, [index, param]].set_index(index)[param].to_dict()
        
        case '>':
            return df.loc[df[filter_param] > filter, [index, param]].set_index(index)[param].to_dict()
        
        case '<=':
            return df.loc[df[filter_param] <= filter, [index, param]].set_index(index)[param].to_dict()

        case '<':
            return df.loc[df[filter_param] < filter, [index, param]].set_index(index)[param].to_dict()

def component_map_complete_dict(case: object, key_component: str, key_param: str, val_component: str, val_param: str, merge_param: str) -> Dict[str, List[str]]:
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

    #Check if key_components exists
    if not hasattr(case, key_component):
        raise AttributeError(f"Case object has no component '{key_component}'")

    #Check if val_components exists
    if not hasattr(case, val_component):
        raise AttributeError(f"Case object has no component '{val_component}'")

    key_component_map = getattr(case, val_component).groupby(merge_param)[val_param].apply(list).to_dict()
    for component in getattr(case, key_component)[key_param]:
        key_component_map.setdefault(component, [])
    
    return key_component_map

def comma_param_to_list(case: object, component: str, comma_param: str, filter_param: Union[str, float, int] = None, operation: str = None, filter: Union[str, float,int] = None) -> Dict[str, tuple[str,...]]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check all filtering is None or Not None
    if None in [filter_param, operation, filter]:
        for input in [filter_param, operation, filter]:
            if input is not None:
                raise Exception(f"Some filter variables to this function are set as None")

    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in '{component}' data")
    if filter_param not in df.columns and filter_param is not None:
        raise KeyError(f"Parameter '{filter_param}' not found in '{component}' data")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise Exception(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    
    #Check filter_param and filter types are numeric if required
    if operation in ['>=', '>', '<=', '<'] and type(filter_param) not in [int,float] and type(filter) not in [int, float]:
        raise Exception(f"To use numerical operation {operation} the filter_param and filter data types must by int or float. Currently filter_param is {type(filter_param)} and filter is {type(filter)}")
    
    #Perform filtering operations, if None then no filtering is performed.
    match operation:
        case None:
            series = df[comma_param]
        
        case '=':
            series = df.loc[df['export_policy'] == 'Pro-Rata']['prorata_groups']

        case '!=':
            series = df.loc[df['export_policy'] != 'Pro-Rata']['prorata_groups']
        
        case '>=':
            series = df.loc[df['export_policy'] >= 'Pro-Rata']['prorata_groups']
        
        case '>':
            series = df.loc[df['export_policy'] > 'Pro-Rata']['prorata_groups']
        
        case '<=':
            series = df.loc[df['export_policy'] <= 'Pro-Rata']['prorata_groups']

        case '<':
            series = df.loc[df['export_policy'] <= 'Pro-Rata']['prorata_groups']

    #Return Series
    return series\
                .dropna()\
                .str.split(',')\
                .explode()\
                .str.strip()\
                .unique()\
                .tolist()\

def comma_param_to_dict(case: object, component: str, index: str, comma_param: str, filter_param: Union[str, float, int] = None, operation: str = None, filter: Union[str, float,int] = None) -> Dict[str, tuple[str,...]]:
    '''
    Used to split a comma separated parameter into tuples,
    and return a dictionary of the component against an index
    '''
    supported_operations = [None, '=', '!=', '>=', '>', '<=', '<']

    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check all filtering is None or Not None
    if None in [filter_param, operation, filter]:
        for input in [filter_param, operation, filter]:
            if input is not None:
                raise Exception(f"Some filter variables to this function are set as None")

    #Check parameters exist in df
    if comma_param not in df.columns:
        raise KeyError(f"Parameter '{comma_param}' not found in '{component}' data")
    if filter_param not in df.columns and filter_param is not None:
        raise KeyError(f"Parameter '{filter_param}' not found in '{component}' data")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise Exception(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    
    #Check filter_param and filter types are numeric if required
    if operation in ['>=', '>', '<=', '<'] and type(filter_param) not in [int,float] and type(filter) not in [int, float]:
        raise Exception(f"To use numerical operation {operation} the filter_param and filter data types must by int or float. Currently filter_param is {type(filter_param)} and filter is {type(filter)}")

    #Perform operations, if None then no filtering is performed.
    match operation:
        case None:
            filtered_df = df.loc[:, [index, comma_param]]
       
        case '=':
            filtered_df =  df.loc[df[filter_param] == filter, [index, comma_param]]

        case '!=':
            filtered_df =  df.loc[df[filter_param] != filter, [index, comma_param]]
        
        case '>=':
            filtered_df =  df.loc[df[filter_param] >= filter, [index, comma_param]]
        
        case '>':
            filtered_df =  df.loc[df[filter_param] > filter, [index, comma_param]]
        
        case '<=':
            filtered_df =  df.loc[df[filter_param] <= filter, [index, comma_param]]

        case '<':
            filtered_df =  df.loc[df[filter_param] < filter, [index, comma_param]]
        
    return filtered_df\
                    .set_index(index)[comma_param]\
                    .dropna()\
                    .apply(lambda x: tuple(groups.strip() for groups in x.split(',')))\
                    .to_dict()

def get_filtered_df(case: object, component: str, filter_param: Union[str, float, int], operation: str, filter: Union[str, float,int],  return_param: Union[str,float,int]) -> List[str]:
    '''Return list of components filtered by a parameter'''
    supported_operations = ['=', '!=', '>=', '>', '<=', '<']

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in df
    for param in [filter_param, return_param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Check selected operator is a supported operation
    if operation not in supported_operations:
        raise Exception(f"The operator {operation} is not defined for this function. Please use one of {supported_operations}")
    
    #Check filter_param and filter types are numeric
    if operation in ['>=', '>', '<=', '<'] and type(filter_param) not in [int,float] and type(filter) not in [int, float]:
        raise Exception(f"To use numerical operation {operation} the filter_param and filter data types must by int or float. Currently filter_param is {type(filter_param)} and filter is {type(filter)}")

    #Perform Operation
    match operation:
        case '=':
            return df.loc[df[filter_param] == filter]
        
        case '!=':
            return df.loc[df[filter_param] != filter]
        
        case '>=':
            return df.loc[df[filter_param] >= filter]
        
        case '>':
            return df.loc[df[filter_param] > filter]
        
        case '<=':
            return df.loc[df[filter_param] <= filter]

        case '<':
            return df.loc[df[filter_param] < filter]
        