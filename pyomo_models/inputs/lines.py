
from typing import List, Dict, Tuple
import itertools as iter
import data_io.helpers as helpers

### KEY DEFINITIONS
component = 'branches'

###
### GENERAL LISTS AND MAPPING
###

##DEMAND PYOMO DICTIONARY DEFINITIONS
#Demand Identifiers (for Set D)
def identifiers(case):
    return helpers.get_param_list(case, component, 'name')

def bus_line_in(case):
    '''
    Function creates a map of lines feeding into each bus. It returns a dictionary with the buses (name of each bus) 
    as the keys, with a list of lines feeding into each bus as the value.
    '''
    return helpers.component_map_complete_dict(case,
                                               'busses',
                                               'name',
                                               component,
                                               'name',
                                               'to_busname') 

def bus_line_out(case):
    '''
    Function creates a map of lines feeding out of each bus. It returns a dictionary with the buses (name of each bus) 
    as the keys, with a list of lines feeding into out of each bus as the value.
    '''
    return helpers.component_map_complete_dict(case,
                                               'busses',
                                               'name',
                                               component,
                                               'name',
                                               'from_busname') 

def line_buses(self):
    return dict(zip(self.lines['name'], zip(self.lines['from_busname'], self.lines['to_busname'])))

def continuous_rating(case):
    return helpers.get_PerUnit_param_dict(case, component, 'name', 'ContinousRating', case.baseMVA)

def susceptance(case):
    return helpers.get_param_dict(case, component, 'name', 'b')

def reactance(case):
    return helpers.get_param_dict(case, component, 'name', 'x')

