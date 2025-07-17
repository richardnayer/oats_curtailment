from typing import List, Dict, Tuple
import pandas as pd
import data_feed.pyomo.helpers as helpers

### KEY DEFINITIONS
component = 'baseMVA'

###
### GENERAL LISTS AND MAPPING
###

#Bus Identifiers (Set B)
def identifiers(case: object) -> List[str]:
    return helpers.get_param_list(case, component, 'name')