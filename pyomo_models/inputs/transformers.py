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
component = 'transformers'

##TRANSFORMER PYOMO DICTIONARY DEFINITIONS
#Transformer Identifiers (for Set TRANSF)
def identifiers(case):
    return helpers.get_param_list(case, component, 'name')

#Transformer Originating Bus
def from_bus(case):
    return helpers.get_param_dict(case, component, 'name' , 'from_busname')

#Transformer Destination Bus
def to_bus(case):
    return helpers.get_param_dict(case, component, 'name' , 'to_busname')
#Transformer Type
def type(case):
    return helpers.get_param_dict(case, component, 'name' , 'type')

###Creates a dictionary with the bus as the key, and transformers that feed to the bus as dictionary values
def bus_transformer_in(case):
    return helpers.component_map_complete_dict(case,
                                               'busses',
                                               'name',
                                               component,
                                               'name',
                                               'to_busname') 

#Creates a dictionary with the bus as the key, with transformers fed from the bus as the dictionary values
def bus_transformer_out(case):
    return helpers.component_map_complete_dict(case,
                                               'busses',
                                               'name',
                                               component,
                                               'name',
                                               'from_busname')

##Create a dictionary with transformer as the key, and a tuple of from_bus name and to_busname as the value
def transformer_buses(case):
    return dict(zip(case.transformer['name'], zip(case.transformer['from_busname'], case.transformer['to_busname'])))

#Transformer Resistance (R)
def resistance(case):
    return helpers.get_param_dict(case, component, 'name', 'to_r')

#Transformer Reactance (X)
def reactance(case):
    return helpers.get_param_dict(case, component, 'name', 'x')

#Transformer Susceptance (B) (for Set BLT)
def susceptance(case):
    return helpers.get_param_dict(case, component, 'name', 'b')

#Transformer Short Term Voltage Rating
def short_term_rating(case):
    return helpers.get_PerUnit_param_dict(case, component, 'name', 'ShortTermRating', case.baseMVA)

#Transformer Continuous Voltage Rating (for Set SLmaxT)
def continuous_rating(case):
    return helpers.get_PerUnit_param_dict(case, component, 'name', 'ContinousRating', case.baseMVA) 

#Transformer Minimum Voltage Angle (Lower Bound)
def voltage_angle_minimum(case):
    return helpers.get_param_dict(case, component, 'name', 'angLB')

#Transformer Maximum Voltage Angle (Upper Bound)
def voltage_angle_maximum(case):
    return helpers.get_param_dict(case, component, 'name', 'angUB')

#Transformer Phase Shift
def phase_shift(case):
    return helpers.get_param_dict(case, component, 'name', 'PhaseShift')

#Transformer Tap Ratio
def tap_ratio(case):
    return helpers.get_param_dict(case, component, 'name', 'TapRatio')

#Transformer Tap Ratio Minimum (Lower Bound)
def tap_ratio_minimum(case):
    return helpers.get_param_dict(case, component, 'name', 'TapLB')

#Transformer Tap Ratio Maximum (Upper Bound)
def tap_ratio_maximum(case):
    return helpers.get_param_dict(case, component, 'name', 'TapUB')

#Transformer Contingency
def contingency(case):
    return helpers.get_param_dict(case, component, 'name', 'contingency')

#Transformer Failure Rate (1/year)
def probability(case):
    return helpers.get_param_dict(case, component, 'name', 'probability')
