"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
from typing import List, Dict, Tuple
import itertools as iter
import data_io.helpers as helpers

### KEY DEFINITIONS
component = 'demands'

###
### GENERAL LISTS AND MAPPING
###

def identifiers(case: object) -> List[str]:
    return helpers.get_param_list(case, component, 'name')

### Negative Demands
def negatives(case:object) -> List[str]:
    return helpers.get_param_list(case, component,'name', 'real', '<', 0)

### Demand Bus Mapping
def bus_mapping(case: object) -> Dict[str, List[str]]:
    '''
    Function creates a map of demands against each bus. It returns a dictionary with the buses (name of each bus) 
    as the keys, with a list of demands assigned to each bus as the value.
    '''
    return helpers.component_map_complete_dict(case,
                                               'busses',
                                               'name',
                                               'demands',
                                               'name',
                                               'busname') 

#Real Power Demand (for Parameter PD, Real Power Demand)
def real_demand(case):
    return helpers.get_PerUnit_param_dict(case, component, 'name', 'real', case.baseMVA)

#Reactive Power Demand
def reactive_demand(case):
    return helpers.get_PerUnit_param_dict(case, component, 'name', 'reactive', case.baseMVA) 

#Demand Value of Lost Load (for Parameter VOLL, Volume of Lost Load)
def VOLL(case):
    return helpers.get_param_dict(case, component, 'name', 'VOLL')
