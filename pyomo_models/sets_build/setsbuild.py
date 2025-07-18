import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo.environ import *

class Sets_Dict():
    def __init__(self,case):
        self.sets = {
            # --- SETS FOR BUSSES ---     
            #Normal Set of Busses
            'B': {'type': 'flat',
                  'within': None,
                  'dimen' : 1,
                  'initialize': lambda: helpers.get_param_list(case, 'busses', 'name'),
            },
            #Set Containing Slack Bus (Single Item)
            'b0':{'within': 'B',
                  'initialize': lambda: helpers.get_param_list(case, 'busses', 'name', 'type', '=', 3)
            },

            # --- SETS FOR GENERATORS ---  
            #Normal Set of Generators
            'G': {'within': None,
                    'initialize': lambda: helpers.get_param_list(case, 'generators', 'name')
            },
            ##Indexed Set - Index of buses, against a list of all generators attached to the bus
            'generator_mapping': {'within': 'B',
                    'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'generators',
                                                    'name',
                                                    'busname')
            },
            #Normal Set - List of generators with export controlled using a LIFO policy
            'G_LIFO': {'within': 'G',
                    'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'LIFO')
            },
            # Matrix set, set of LIFO positions (x,y), x is curtailed before y
            'G_LIFO_pairs': {
                'within': ('G_LIFO', 'G_LIFO'),
                'initialize': lambda: helpers.get_ordered_groupwise_combinations(case, 'generators', 'name', 'lifo_group', 'lifo_position')
            },
            #Normal Set - List of generators with export controlled using a Pro-Rata policy
            'G_prorata': {
                'within': 'G',
                'initialize': lambda: helpers.get_param_list(case, 'generators','name', 'export_policy', '=', 'Pro-Rata')

            },
            #Indexed Set - Index of generators, with list of all pro-rata constraint groups to which it belongs as values
            'G_prorata_map': {
                'within': 'G_prorata',
                'initialize': lambda: helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },
            #Set of pairs of generator and pro-rata constraint group
            'G_prorata_pairs': {
                'within': None,
                'initialize': lambda m: [
                    (g, grp) for g in m.G_prorata for grp in m.G_prorata_map[g]
                ]
            },
            #Normal Set - List of generators with export controlled using a LIFO policy
            'G_individual': {
                'within': 'G',
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Individual')
            },
            #Normal Set - List of generators which are uncontrollable (i.e. set at max output)
            'G_uncontrollable': {
                'within': 'G',
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Uncontrollable')
            },
            #Normal Set - Synchronous Generators
            'G_s': {
                'within': 'G',
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'Yes')
            },
            #Normal Set - Non-Synchronous Generators
            'G_ns': {
                'within': 'G',
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'No')
            },
            #Set of pro-rata curtailment groups
            'prorata_groups': {
                'within': None,
                'initialize': lambda: helpers.comma_param_to_list(case, 'generators', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },

            # --- SETS FOR POWER LINES ---
            #Normal Set - Power Lines
            'L': {
                'within': None,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name')
            },
            #Indexed Set - Index of buses, against ends of power lines (i.e. power lines into each bus)
            'bus_line_in': {
                'within': 'B',
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'branches',
                                                    'name',
                                                    'to_busname') 
            },
            #Indexed Set - Index of buses, against starts of power lines (i.e. power lines out of each bus)
            'bus_line_out': {
                'within': 'B',
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'branches',
                                                    'name',
                                                    'from_busname') 
            },
            #Indexed Set - Index of lines, against tuples of buses in the form (from, to)
            'line_busses': {
                'within': 'L',
                'initialize': helpers.get_zipped_param_list(case, 'branches', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR TRANSFORMERS ---
            #Normal Set - Power Transformers
            'TRANSF': {
                'within': None,
                'initialize': lambda: helpers.get_param_list(case, 'transformers', 'name')
            },
            #Indexed Set - Index of buses, against ends of power transformers (i.e. power transformer into each bus)
            'bus_transformer_in': {
                'within': 'B',
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'transformers',
                                                    'name',
                                                    'to_busname') 
            },
            #Indexed Set - Index of buses, against starts of power transformers (i.e. power transformers out of each bus)
            'bus_transformer_out': {
                'within': 'B',
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'transformers',
                                                    'name',
                                                    'from_busname')
            },
            #Indexed Set - Index of transformers, against tuples of buses in the form (from, to)
            'transformer_busses': {
                'within': 'TRANSF',
                'initialize': lambda: helpers.get_zipped_param_list(case, 'transformers', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR DEMANDS ---
            #Normal Set - Demands
            'D': {
                'within': None,
                'initialize': lambda: helpers.get_param_list(case, 'demands', 'name')
            },
            #Normal Set - Negative Demands
            'DNeg': {
                'within': 'D',
                'initialize': lambda: helpers.get_param_list(case, 'demands','name', 'real', '<', 0)
            },
            #Indexed Set - Index of buses, against a list of all demands attached to the bus
            'demand_bus_mapping': {
                'within': 'B',
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                    'busses',
                                                    'name',
                                                    'demands',
                                                    'name',
                                                    'busname') 
            }
        }


