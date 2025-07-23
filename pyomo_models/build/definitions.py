import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo.environ import *

class Sets_Blocks():
    def __init__(self, case):
        self.blocks = {
            # --- SETS FOR BUSSES ---
            'B': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name'),
            },
            'b0': {
                'type': 'flat',
                'index': None,
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name', 'type', '=', 3)
            },
            
            # --- SETS FOR GENERATORS ---
            'G': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name')
            },
            'generator_mapping': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'generators', 'name',
                                                                          'busname')
            },
            'G_LIFO': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'LIFO')
            },
            'G_LIFO_pairs': {
                'type': 'flat',
                'index': None,
                'within': ('G_LIFO', 'G_LIFO'),
                'dimen': 2,
                'initialize': lambda: helpers.get_ordered_groupwise_combinations(case, 'generators', 'name', 'lifo_group', 'lifo_position')
            },
            'G_prorata': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators','name', 'export_policy', '=', 'Pro-Rata')
            },
            'G_prorata_map': {
                'type': 'indexed',
                'index': 'G_prorata',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },
            'G_prorata_pairs': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 2,
                'initialize': lambda: helpers.get_paired_params_list(case, 'generators', 'name', 'prorata_groups', True,'export_policy', '=', 'Pro-Rata')
            },
            'G_individual': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Individual')
            },
            'G_uncontrollable': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Uncontrollable')
            },
            'G_s': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'Yes')
            },
            'G_ns': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'No')
            },
            'prorata_groups': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_list(case, 'generators', 'prorata_groups', 'export_policy', '=', 'Pro-Rata')
            },

            # --- SETS FOR POWER LINES ---
            'L': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'branches', 'name')
            },
            'bus_line_in': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'to_busname')
            },
            'bus_line_out': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'from_busname')
            },
            'line_busses': {
                'type': 'indexed',
                'index': 'L',
                'within': None,
                'dimen': 2,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'branches', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR TRANSFORMERS ---
            'TRANSF': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'transformers', 'name')
            },
            'bus_transformer_in': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'to_busname')
            },
            'bus_transformer_out': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'from_busname')
            },
            'transformer_busses': {
                'type': 'indexed',
                'index': 'TRANSF',
                'within': None,
                'dimen': 2,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'transformers', 'name', ['from_busname', 'to_busname'])
            },

            # --- SETS FOR DEMANDS ---
            'D': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands', 'name')
            },
            'DNeg': {
                'type': 'flat',
                'index': None,
                'within': 'D',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands','name', 'real', '<', 0)
            },
            'demand_bus_mapping': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'demands', 'name',
                                                                          'busname')
            }
        }

class Constraint_Blocks():
    def __init__(self, instance):
        # --- POWER LINE CONSTRAINTS ---
        self.line_blocks = {
            'cont_realpower_max_pstve': {
                'function': lambda instance, line: instance.pL[line] <= instance.line_max_continuous_P[line],
                'set': instance.L
            },
            'cont_realpower_max_ngtve': {
                'function': lambda instance, line: instance.pL[line] >= -instance.line_max_continuous_P[line],
                'set': instance.L
            }
        }

        # --- DEMAND CONSTRAINTS ---
        self.demand_blocks = {
            
            'real_alpha_controlled': {
                'function': lambda instance, demand: instance.pD[demand] == instance.alpha[demand]*instance.PD[demand],
                'set': instance.D
            },
            'alpha_max': {
                'function': lambda instance, demand: instance.alpha[demand] <= 1,
                'set': instance.D
            },
            'alpha_fixneg': {
                'function': lambda instance, demand: instance.alpha[demand] == 1,
                'set': instance.DNeg
            }
        }

        #--- GENERATION CONSTRAINTS ---
        self.generation_blocks = {
            # --- Uncontrollable EER Poliy ---
              #Constrains output of each generator to equal to the setpoint. \n
              #Should be defined against the set of uncontrollable generators (instance.G_uncontrollable)
              
            'uncontrollable_realpower_sp': {
                'function': lambda instance, generator: instance.pG[generator] == instance.PG[generator],
                'set': instance.G_uncontrollable
            },

            # --- Mingen Requirements ---
            '''
            Constrains output of each generator to less than or equal to the maximum value. \n
            Should be defined against the set of individually curtailed generators (instance.G_individual)
            '''
            'mingen_LB': {
                'function': lambda instance, generator:  instance.pG[generator] >= instance.PGMINGEN[generator],
                'set': instance.G
            },

            # --- Individual EER Policy ---
            '''
            Constrains output of each generator to less than or equal to the maximum value. \n
            Should be defined against the set of individually curtailed generators (instance.G_individual)
            '''
            'individual_realpower_max': {
                'function': lambda instance, generator: instance.pG[generator] <= instance.PGmax[generator],
                'set': instance.G_individual
            },
            'individual_realpower_min': {
                'function': lambda instance, generator: instance.pG[generator] >= instance.PGmin[generator],
                'set': instance.G_individual
            },
            # --- Pro-Rata ERG Curtailment ---
            'prorata_realpower_max': {
                'function': lambda instance, generator: instance.pG[generator] <= instance.PGmax[generator] * instance.zeta_wind[generator],
                'set': instance.G_prorata
            },
            'prorata_realpower_min': {
                'function': lambda instance, generator: instance.pG[generator] >= instance.PGmin[generator],
                'set': instance.G_prorata
            },
            'prorata_realpower_min_zeta': {
                'function': lambda instance, generator: instance.pG[generator] >= instance.PGmax[generator] * instance.zeta_wind[generator],
                'set': instance.G_prorata
            },
            'prorata_zeta_max': {
                'function': lambda instance, generator, cg: instance.zeta_wind[generator] <=  instance.zeta_cg[cg],
                'set': instance.WindCGPairs
            },
            'prorata_zeta_min': {
                'function': lambda instance, generator, cg: instance.zeta_wind[generator] >= instance.zeta_cg[cg] - (1 - 0) * (1-instance.zeta_bin[(generator, cg)]),
                'set': instance.WindCGPairs
            },
            'prorata_zeta_binary': {
                'function': lambda instance, generator, cg: sum(instance.zeta_bin[(generator, cg)] for cg in instance.G_prorata_map[generator]) == 1,
                'set': instance.WIND
            },
            # --- Last-In-First-Out (LIFT) ERG Curtailment ---
            'LIFO_realpower_max': {
                'function': lambda instance, generator: instance.pG[generator] <= (1 - instance.beta[generator]) * instance.PGmax[generator],
                'set': instance.WIND
            },
            'LIFO_realpower_min': {
                'function': lambda instance, generator: instance.pG[generator] >= (1-instance.gamma[generator])*instance.PGmax[generator],
                'set': instance.WIND
            },
            'LIFO_gamma': {
                'function': lambda instance, gen1, gen2: instance.gamma[gen1] <= instance.gamma[gen2],
                'set': instance.LIFOset
            },
            'LIFO_beta': {
                'function': lambda instance, gen1, gen2: instance.gamma[gen1] <= instance.beta[gen2],
                'set': instance.LIFOset
            },
        }

        # --- KCL CONSTRAINTS ---
        self.KCL_blocks = {
            'networked_realpower_noshunt': {
                'function': lambda instance, bus: + sum(instance.pG[generator] for generator in instance.generator_mapping[bus])\
                                                        - sum(instance.pL[line] for line in instance.bus_line_out[bus])\
                                                        + sum(instance.pL[line] for line in instance.bus_line_in[bus])\
                                                        - sum(instance.pLT[transformer] for transformer in instance.bus_transformer_out[bus])\
                                                        +sum(instance.pLT[transformer] for transformer in instance.bus_transformer_in[bus])\
                                                        ==\
                                                        sum(instance.pD[demand] for demand in instance.demand_bus_mapping[bus]),
                'set': instance.B
            },
            'networked_realpower_withshunt': {
                'function': lambda instance, bus: + sum(instance.pG[generator] for generator in instance.generator_mapping[bus])\
                                                    - sum(instance.pL[line] for line in instance.bus_line_out[bus])\
                                                    + sum(instance.pL[line] for line in instance.bus_line_in[bus])\
                                                    - sum(instance.pLT[transformer] for transformer in instance.bus_transformer_out[bus])\
                                                    +sum(instance.pLT[transformer] for transformer in instance.bus_transformer_in[bus])\
                                                    ==\
                                                    sum(instance.pD[demand] for demand in instance.demand_bus_mapping[bus]) +\
                                                    sum(instance.GB[s] for s in instance.SHUNT if (bus,s) in instance.SHUNTbs),
                'set': instance.B
            }
        }

        # --- KVL CONSTRAINTS---
        self.KVL_blocks = {        
            'DCOPF_lines': {
                'function': lambda instance, line: instance.pL[line] == (1/instance.line_reactance[line])*instance.deltaL[line],
                'set': instance.L
            },
            'DCOPF_transformer': {
                'function': lambda instance, transformer: instance.pLT[transformer] == (1/instance.transformer_reactance[transformer])*instance.deltaLT[transformer],
                'set': instance.L
            },
        }

        # --- TRANSFORMER CONSTRAINTS---
        self.transformer_blocks = {        
            'continuous_real_max_pstveDCOPF_lines': {
                'function': lambda instance, transformer: instance.pLT[transformer] <= instance.transformer_max_continuous_P[transformer],
                'set': instance.TRANSF
            },
            'continuous_real_max_ngtve': {
                'function': lambda instance, transformer: instance.pLT[transformer] >= -instance.transformer_max_continuous_P[transformer],
                'set': instance.TRANSF
            },
        }

        # --- VOLTAGE CONSTRAINTS---
        self.voltage_blocks = {        
            'line_delta': {
                'function': lambda instance, line: instance.deltaL[line] == \
                                                    + instance.delta[instance.line_busses[line].at(1)]\
                                                    - instance.delta[instance.line_busses[line].at(2)],
                'set': instance.L
            },
            'transformer_delta': {
                'function': lambda instance, transformer: instance.deltaLT[transformer] == \
                                                            + instance.delta[instance.transformer_busses[transformer].at(1)]\
                                                            - instance.delta[instance.transformer_busses[transformer].at(2)],
                'set': instance.TRANSF
            },
            'reference_bus': {
                'function': lambda instance, bus: instance.delta[bus]==0,
                'set': instance.B
            },
        }