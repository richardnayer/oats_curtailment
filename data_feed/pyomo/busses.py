
from typing import List, Dict, Tuple
import pandas as pd
import data_feed.pyomo.helpers as helpers

### KEY DEFINITIONS
component = 'busses'

###
### GENERAL LISTS AND MAPPING
###

#Bus Identifiers (Set B)
def identifiers(case: object) -> List[str]:
    return helpers.get_param_list(case, component, 'name')

#Slack Bus Identifier (Set b0)
def slack_buses(case: object) -> List[str]:
    return helpers.get_param_list(case, component, 'type', '=', 3)

#Bus Base Type
def type(case: object) -> Dict[str, str]:
    return helpers.get_param_dict(case, component, 'name', 'type')

#Bus Zone
def zone(case: object) -> Dict[str, str]:
    return helpers.get_param_dict(case, component, 'name', 'zone')

###
### VOLTAGE MAPPING
###

#Bus Base kV Data
def basekV(case: object) -> Dict[str, float]:
    return helpers.get_param_dict(case, component, 'name', 'basekV')

#Bus Voltage Lower Bound
def voltage_lower_bound(case: object) -> Dict[str, float]:
    return helpers.get_param_dict(case, component, 'name', 'VNLB')

#Bus Voltage Upper Bound
def voltage_upper_bound(case: object) -> Dict[str, float]:
    return helpers.get_param_dict(case, component, 'name', 'VNUB')