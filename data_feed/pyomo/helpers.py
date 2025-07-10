from typing import List, Dict, Tuple

def get_baseMVA_param(case: object, component: str, index:str , param: str, baseMVA: float) -> Dict[str, float]:
    '''Return a dict mapping the index (e.g. generator name) to parameter scaled against baseMVA'''
    if index not in case.component.columns:
        raise KeyError(f"Column '{index}' not found in {component} data")
    if param not in case.component.columns:
        raise KeyError(f"Column '{param}' not found in {component} data")
    return (case.component.set_index(index)[param] / baseMVA).to_dict()

def get_param(case: object, component: str, index:str , param: str) -> Dict[str, float]:
    '''Return a dict mapping the index (e.g. generator name) to parameter'''
    if index not in case.component.columns:
        raise KeyError(f"Column '{index}' not found in {component} data")
    if param not in case.component.columns:
        raise KeyError(f"Column '{param}' not found in {component} data")
    return case.component.set_index(index)[param].to_dict()

def _map_param_by_user_index(case: object, component: str, index: str, param: str) -> Dict[str, float]:
    """Helper function to map a bus column by bus name."""
    return case.component.set_index(index)[param].to_dict()

def filter_component_by_param(case: object, component: str, filter_param: str, filter: str, return_param: str) -> List[str]:
    '''Return list of components filtered by a parameter'''

    #Check if component exists
    if not hasattr(case, component):
        raise AttributeError(f"Case object has no component '{component}'")
    
    df = getattr(case, component)

    #Check parameters exist in code
    for param in [filter_param, return_param]:
        if param not in df.columns:
            raise KeyError(f"Parameter '{param}' not found in '{component}' data")

    #Return list
    return df.loc[df[filter_param] == filter, return_param].tolist()