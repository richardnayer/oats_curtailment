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
                'ordered': False
            },
            'b0': {
                'type': 'flat',
                'index': None,
                'within': 'B',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name', 'type', '=', 3),
                'ordered': False
            },
            
            # --- SETS FOR GENERATORS ---
            'G': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name'),
                'ordered': False
            },
            'generator_mapping': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'generators', 'name',
                                                                          'busname'),
                'ordered': False
            },
            'G_LIFO': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'LIFO'),
                'ordered': False
            },
            'G_LIFO_pairs': {
                'type': 'flat',
                'index': None,
                'within': ('G_LIFO', 'G_LIFO'),
                'dimen': 2,
                'initialize': lambda: helpers.get_ordered_groupwise_combinations(case, 'generators', 'name', 'lifo_group', 'lifo_position'),
                'ordered': True
            },
            'G_prorata': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators','name', 'export_policy', '=', 'Pro-Rata'),
                'ordered': False
            },
            'G_prorata_map': {
                'type': 'indexed',
                'index': 'G_prorata',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups', 'export_policy', '=', 'Pro-Rata'),
                'ordered': False
            },
            'G_prorata_pairs': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 2,
                'initialize': lambda: helpers.get_paired_params_list(case, 'generators', 'name', 'prorata_groups', True,'export_policy', '=', 'Pro-Rata'),
                'ordered': False
            },
            'G_individual': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Individual'),
                'ordered': False
            },
            'G_uncontrollable': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'export_policy', '=', 'Uncontrollable'),
                'ordered': False
            },
            'G_s': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'Yes'),
                'ordered': False
            },
            'G_ns': {
                'type': 'flat',
                'index': None,
                'within': 'G',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'generators', 'name', 'synchronous', '=', 'No'),
                'ordered': False
            },
            'prorata_groups': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.comma_param_to_list(case, 'generators', 'prorata_groups', 'export_policy', '=', 'Pro-Rata'),
                'ordered': False
            },

            # --- SETS FOR POWER LINES ---
            'L': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'branches', 'name'),
                'ordered': False
            },
            'bus_line_in': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'to_busname'),
                'ordered': False
            },
            'bus_line_out': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'branches', 'name',
                                                                          'from_busname'),
                'ordered': False
            },
            'line_busses': {
                'type': 'indexed',
                'index': 'L',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'branches', 'name', ['from_busname', 'to_busname']),
                'ordered': True
            },

            # --- SETS FOR TRANSFORMERS ---
            'TRANSF': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'transformers', 'name'),
                'ordered': False
            },
            'bus_transformer_in': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'to_busname'),
                'ordered': False
            },
            'bus_transformer_out': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'transformers', 'name',
                                                                          'from_busname'),
                'ordered': False
            },
            'transformer_busses': {
                'type': 'indexed',
                'index': 'TRANSF',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_zipped_param_list(case, 'transformers', 'name', ['from_busname', 'to_busname']),
                'ordered': True
            },

            # --- SETS FOR DEMANDS ---
            'D': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands', 'name'),
                'ordered': False
            },
            'DNeg': {
                'type': 'flat',
                'index': None,
                'within': 'D',
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'demands','name', 'real', '<', 0),
                'ordered': False
            },
            'demand_bus_mapping': {
                'type': 'indexed',
                'index': 'B',
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.component_map_complete_dict(case,
                                                                          'busses', 'name',
                                                                          'demands', 'name',
                                                                          'busname'),
                'ordered': False
            }
        }

class Params_Blocks():
    def __init__(self, case, instance):
        self.blocks = {
            #LINE CONSTRAINTS#
            'line_max_continuous_P': {
                'index': instance.L,
                'within': NonNegativeReals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'branches', 'name', 'ContinousRating', case.baseMVA),
                'mutable': True
            },
            'line_susceptance': {
                'index': instance.L,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'branches', 'name', 'b'),
                'mutable': False
            },
            'line_reactance': {
                'index': instance.L,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'branches', 'name', 'x'),
                'mutable': False
            },

            #TRANSFORMER PARAMETERS
            'transformer_max_continuous_P': {
                'index': instance.TRANSF,
                'within': NonNegativeReals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'transformers', 'name', 'ContinousRating', case.baseMVA),
                'mutable': True
            },
            'transformer_susceptance': {
                'index': instance.TRANSF,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'transformers', 'name', 'b'),
                'mutable': False
            },
            'transformer_reactance': {
                'index': instance.TRANSF,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'transformers', 'name', 'x'),
                'mutable': False
            },

            #DEMAND PARAMETERS
            'PD': {
                'index': instance.D,
                'within': NonNegativeReals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'demands', 'name', 'real', case.baseMVA),
                'mutable': True
            },
            'VOLL': {
                'index': instance.D,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'demands', 'name', 'VOLL'),
                'mutable': True
            },

            #GENERATOR POWER PARAMETERS
            'PGmax': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'generators', 'name', 'PGUB', case.baseMVA),
                'mutable': True
            },
            'PGmin': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'generators', 'name', 'PGLB', case.baseMVA),
                'mutable': True
            },
            'PGMINGEN': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_PerUnit_param_dict(case, 'generators', 'name', 'PGMINGEN', case.baseMVA),
                'mutable': True
            },
        
            #GENERATOR COST PARAMETERS
            'c0': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'generators', 'name', 'costc0'),
                'mutable': False
            },
            'c1': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'generators', 'name', 'costc1'),
                'mutable': False
            },
            'bid': {
                'index': instance.G,
                'within': Reals,
                'initialize': lambda: helpers.get_param_dict(case, 'generators', 'name', 'bid'),
                'mutable': True
            },

            #BASE MVA PARAMETER
            'baseMVA': {
                'index': instance.G,
                'within': NonNegativeReals,
                'initialize': lambda: case.baseMVA,
                'mutable': False
            }
        }

class Variables_Blocks():
    def __init__(self, instance):
        self.blocks = {
            #CONTROL VARIABLES
            'pG': {
                'index': instance.G,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
            'pD': {
                'index': instance.D,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
            'alpha': {
                'index': instance.D,
                'domain': NonNegativeReals,
                'bounds': None,
                'initialize': None
            },

            #Pro-Rata Curtailment Control Variables
            'zeta_cg': {
                'index': instance.prorata_groups,
                'domain': NonNegativeReals,
                'bounds': (0, 1),
                'initialize': None
            },
            'zeta_wind': {
                'index': instance.G_prorata,
                'domain': NonNegativeReals,
                'bounds': (0, 1),
                'initialize': None
            },
            'zeta_bin': {
                'index': instance.G_prorata_pairs,
                'domain': Binary,
                'bounds': None,
                'initialize': None
            },
            'minimum_zeta': {
                'index': instance.G_prorata_pairs,
                'domain': NonNegativeReals,
                'bounds': (0, 1),
                'initialize': None
            },

            #LIFO Curtailment Control Variables
            'gamma': { # indicator variable for wind curtailment on/off
                'index': instance.G_LIFO,
                'domain': Binary,
                'bounds': None,
                'initialize': None
            },
            'beta': { #continuous curtailment variable between 0 & 1
                'index': instance.G_LIFO,
                'domain': NonNegativeReals,
                'bounds': (0, 1),
                'initialize': None
            },

            #STATE VARIABLES
            'deltaL': { #angle difference across lines
                'index': instance.L,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
            'deltaLT': { #angle difference across transformers
                'index': instance.TRANSF,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
            'delta': { #voltage phase angle at bus b, rad
                'index': instance.B,
                'domain': Reals,
                'bounds': None,
                'initialize': 0
            },
            'pL': { #real power injected at b onto line l, p.u.
                'index': instance.L,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
            'pLT': { #real power injected at b onto line l, p.u.
                'index': instance.TRANSF,
                'domain': Reals,
                'bounds': None,
                'initialize': None
            },
        }    

class Constraint_Blocks():
    def __init__(self, instance):
            
        self.blocks = {
            # --- POWER LINE CONSTRAINTS ---
            'line_cont_realpower_max_pstve': {
                'rule': lambda instance, line: instance.pL[line] <= instance.line_max_continuous_P[line],
                'index': instance.L
            },
            'line_cont_realpower_max_ngtve': {
                'rule': lambda instance, line: instance.pL[line] >= -instance.line_max_continuous_P[line],
                'index': instance.L
            },
            
            # --- DEMAND CONSTRAINTS ---            
            'demand_real_alpha_controlled': {
                'rule': lambda instance, demand: instance.pD[demand] == instance.alpha[demand]*instance.PD[demand],
                'index': instance.D
            },
            'demand_alpha_max': {
                'rule': lambda instance, demand: instance.alpha[demand] <= 1,
                'index': instance.D
            },
            'demand_alpha_fixneg': {
                'rule': lambda instance, demand: instance.alpha[demand] == 1,
                'index': instance.DNeg
            },

            #--- GENERATION CONSTRAINTS ---
            # --- Uncontrollable EER Poliy ---
              #Constrains output of each generator to equal to the setpoint. \n
              #Should be defined against the set of uncontrollable generators (instance.G_uncontrollable)
              
            'gen_uncontrollable_realpower_sp': {
                'rule': lambda instance, generator: instance.pG[generator] == instance.PG[generator],
                'index': instance.G_uncontrollable
            },

            # --- Mingen Requirements ---
            #Constrains output of each generator to less than or equal to the maximum value. \n
            #Should be defined against the set of individually curtailed generators (instance.G_individual)
            'gen_mingen_LB': {
                'rule': lambda instance, generator:  instance.pG[generator] >= instance.PGMINGEN[generator],
                'index': instance.G
            },

            # --- Individual EER Policy ---
            #Constrains output of each generator to less than or equal to the maximum value. \n
            #Should be defined against the set of individually curtailed generators (instance.G_individual)
            'gen_individual_realpower_max': {
                'rule': lambda instance, generator: instance.pG[generator] <= instance.PGmax[generator],
                'index': instance.G_individual
            },
            'gen_individual_realpower_min': {
                'rule': lambda instance, generator: instance.pG[generator] >= instance.PGmin[generator],
                'index': instance.G_individual
            },

            # --- Pro-Rata ERG Curtailment ---
            'gen_prorata_realpower_max': {
                'rule': lambda instance, generator: instance.pG[generator] <= instance.PGmax[generator] * instance.zeta_wind[generator],
                'index': instance.G_prorata
            },
            'gen_prorata_realpower_min': {
                'rule': lambda instance, generator: instance.pG[generator] >= instance.PGmin[generator],
                'index': instance.G_prorata
            },
            'gen_prorata_realpower_min_zeta': {
                'rule': lambda instance, generator: instance.pG[generator] >= instance.PGmax[generator] * instance.zeta_wind[generator],
                'index': instance.G_prorata
            },
            'gen_prorata_zeta_max': {
                'rule': lambda instance, generator, cg: instance.zeta_wind[generator] <=  instance.zeta_cg[cg],
                'index': instance.G_prorata_pairs
            },
            'gen_prorata_zeta_min': {
                'rule': lambda instance, generator, cg: instance.zeta_wind[generator] >= instance.zeta_cg[cg] - (1 - 0) * (1-instance.zeta_bin[(generator, cg)]),
                'index': instance.G_prorata_pairs
            },
            'gen_prorata_zeta_binary': {
                'rule': lambda instance, generator, cg: sum(instance.zeta_bin[(generator, cg)] for cg in instance.G_prorata_map[generator]) == 1,
                'index': instance.G_prorata
            },

            # --- Last-In-First-Out (LIFT) ERG Curtailment ---
            'gen_LIFO_realpower_max': {
                'rule': lambda instance, generator: instance.pG[generator] <= (1 - instance.beta[generator]) * instance.PGmax[generator],
                'index': instance.G_LIFO
            },
            'gen_LIFO_realpower_min': {
                'rule': lambda instance, generator: instance.pG[generator] >= (1-instance.gamma[generator])*instance.PGmax[generator],
                'index': instance.G_LIFO
            },
            'gen_LIFO_gamma': {
                'rule': lambda instance, gen1, gen2: instance.gamma[gen1] <= instance.gamma[gen2],
                'index': instance.G_LIFO_pairs
            },
            'gen_LIFO_beta': {
                'rule': lambda instance, gen1, gen2: instance.gamma[gen1] <= instance.beta[gen2],
                'index': instance.G_LIFO_pairs
            },

            # --- KCL CONSTRAINTS ---
            'KCL_networked_realpower_noshunt': {
                'rule': lambda instance, bus: + sum(instance.pG[generator] for generator in instance.generator_mapping[bus])\
                                                        - sum(instance.pL[line] for line in instance.bus_line_out[bus])\
                                                        + sum(instance.pL[line] for line in instance.bus_line_in[bus])\
                                                        - sum(instance.pLT[transformer] for transformer in instance.bus_transformer_out[bus])\
                                                        +sum(instance.pLT[transformer] for transformer in instance.bus_transformer_in[bus])\
                                                        ==\
                                                        sum(instance.pD[demand] for demand in instance.demand_bus_mapping[bus]),
                'index': instance.B
            },
            # 'KCL_networked_realpower_withshunt': {
            #     'rule': lambda instance, bus: + sum(instance.pG[generator] for generator in instance.generator_mapping[bus])\
            #                                         - sum(instance.pL[line] for line in instance.bus_line_out[bus])\
            #                                         + sum(instance.pL[line] for line in instance.bus_line_in[bus])\
            #                                         - sum(instance.pLT[transformer] for transformer in instance.bus_transformer_out[bus])\
            #                                         +sum(instance.pLT[transformer] for transformer in instance.bus_transformer_in[bus])\
            #                                         ==\
            #                                         sum(instance.pD[demand] for demand in instance.demand_bus_mapping[bus]) +\
            #                                         sum(instance.GB[s] for s in instance.SHUNT if (bus,s) in instance.SHUNTbs),
            #     'index': instance.B
            # },

            # --- KVL CONSTRAINTS---       
            'KVL_DCOPF_lines': {
                'rule': lambda instance, line: instance.pL[line] == (1/instance.line_reactance[line])*instance.deltaL[line],
                'index': instance.L
            },
            'KVL_DCOPF_transformer': {
                'rule': lambda instance, transformer: instance.pLT[transformer] == (1/instance.transformer_reactance[transformer])*instance.deltaLT[transformer],
                'index': instance.TRANSF
            },

            # --- TRANSFORMER CONSTRAINTS---
            'transf_continuous_real_max_pstve': {
                'rule': lambda instance, transformer: instance.pLT[transformer] <= instance.transformer_max_continuous_P[transformer],
                'index': instance.TRANSF
            },
            'transf_continuous_real_max_ngtve': {
                'rule': lambda instance, transformer: instance.pLT[transformer] >= -instance.transformer_max_continuous_P[transformer],
                'index': instance.TRANSF
            },

            # --- VOLTAGE CONSTRAINTS---      
            'volts_line_delta': {
                'rule': lambda instance, line: instance.deltaL[line] == \
                                                    + instance.delta[instance.line_busses[line].at(1)]\
                                                    - instance.delta[instance.line_busses[line].at(2)],
                'index': instance.L
            },
            'volts_transformer_delta': {
                'rule': lambda instance, transformer: instance.deltaLT[transformer] == \
                                                            + instance.delta[instance.transformer_busses[transformer].at(1)]\
                                                            - instance.delta[instance.transformer_busses[transformer].at(2)],
                'index': instance.TRANSF
            },
            'volts_reference_bus': {
                'rule': lambda instance, bus: instance.delta[bus]==0,
                'index': instance.B
            },
        }

