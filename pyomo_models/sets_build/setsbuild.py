import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo.environ import *

class Sets_Dict():
    def __init__(self, case):
        self.sets = {
            # --- SETS FOR BUSSES ---
            'B': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name'),
            },
            'b0': {
                'type': 'flat',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name', 'type', '=', 3)
            },

            # --- SETS FOR GENERATORS ---
            'G': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name')
            },
            'generator_mapping': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'generators', 'name',
                                                                          'busname')
            },
            'G_LIFO': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'LIFO')
            },
            'G_LIFO_pairs': {
                'type': 'flat',
                'within': ('G_LIFO', 'G_LIFO'),
                'dimen': 2,
                'initialize': lambda: helpers.get_ordered_groupwise_combinations(case, 'generators', 'name', 'lifo_group', 'lifo_position')
            },
            'G_prorata': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators','name', 'export_policy', '=', 'Pro-Rata')
            },
            'G_prorata_map': {
                'type': 'indexed',
                'within': 'G_prorata',
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },
            'G_prorata_pairs': {
                'type': 'flat',
                'within': None,
                'dimen': 2,
                'initialize': lambda: helpers.get_paired_params_list(case, 'generators', 'name', 'prorata_groups', True,'export_policy', '=', 'Pro-Rata')
            },
            'G_individual': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Individual')
            },
            'G_uncontrollable': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Uncontrollable')
            },
            'G_s': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'Yes')
            },
            'G_ns': {
                'type': 'flat',
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'No')
            },
            'prorata_groups': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_list(case, 'generators', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },

            # --- SETS FOR POWER LINES ---
            'L': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name')
            },
            'bus_line_in': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'to_busname')
            },
            'bus_line_out': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'from_busname')
            },
            'line_busses': {
                'type': 'flat',
                'within': 'L',
                'dimen': 2,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'branches', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR TRANSFORMERS ---
            'TRANSF': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'transformers', 'name')
            },
            'bus_transformer_in': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'to_busname')
            },
            'bus_transformer_out': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'from_busname')
            },
            'transformer_busses': {
                'type': 'flat',
                'within': 'TRANSF',
                'dimen': 2,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'transformers', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR DEMANDS ---
            'D': {
                'type': 'flat',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands', 'name')
            },
            'DNeg': {
                'type': 'flat',
                'within': 'D',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands','name', 'real', '<', 0)
            },
            'demand_bus_mapping': {
                'type': 'indexed',
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'demands', 'name',
                                                                          'busname')
            }
        }
