from pyomo_models.build.definitions import *
from pyomo_models.build.build_functions import *
from pyomo_models.build.names import *

import functools
import data_io.pyomo_io as pyomo_io
import pyomo_models.build.pyosolve as pyosolve
from pyomo_models.build.obj_functions import (dcopf_marginal_cost_objective,
                                              copper_plate_marginal_cost_objective,
                                              redispatch_from_market_cost_objective,
                                              redispatch_from_secure_cost_objective)

# Set up logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)



#=============# FUNCTION FOR MUON CONSTRAINTS ==================#

def MUON_constraints(case, instance, constraint_dict, selected_constraints = None):
    #Define handling of default cosntraints to activate
    if selected_constraints == None:
        print("No MUON_MW Constraints Defined")
        return
    
    #Create dictionary of MUON constraint groups defined within the case
    constraints_in_case_dict = helpers.comma_param_as_index_to_dict(case, 'generators', 'name', 'MUON_group')

    #Check if sets have been defined in case, and raise error if not.
    empty_constraint_sets = []
    for constraint in selected_constraints:
        if constraint not in constraints_in_case_dict.keys():
            empty_constraint_sets += [constraint]
    if len(empty_constraint_sets) > 0:
        raise KeyError(f"No generator sets are defined for the followin MUON NB constraints in the case xls: {empty_constraint_sets} ")

    #Add sets of generator to model if (a) they're selected, and (b) they have been defined in the case
    added_sets = []
    for constraint in selected_constraints:
        constraint_set = Set(within = instance.G,
                                initialize = constraints_in_case_dict[constraint],
                                dimen = 1)
        instance.add_component('G_'+constraint, constraint_set)
        added_sets += [constraint]
    print(f"Sets for the following MUON contraints have been added to the model \n {added_sets}")

    #Create Overall MUON Constrain Block if it doesn't already exist
    if hasattr(instance, "MUON") == False:
        setattr(instance, "MUON", Block())
    #Create helper variable
    MUON_block = getattr(instance, "MUON")

    
    added_constraints = []
    for constraint in selected_constraints:
        #Define helper variables
        constraint_def = constraint_dict.get(constraint)
        constraint_type = constraint_def.get("type")
        MUON_type_bound_map = {"MW": {"UB": "PG_UB", "LB": "PG_LB"}, "NB": {"UB": "Ug_UB", "LB": "Ug_LB"}}
        LB_name = MUON_type_bound_map.get(constraint_def.get("type")).get("LB")
        UB_name = MUON_type_bound_map.get(constraint_def.get("type")).get("UB")
        LB = constraint_def.get(LB_name)
        UB = constraint_def.get(UB_name)

        #Define variable to be cosntrained based on type
        if constraint_type == "NB":
            constraint_var = "u_g"
        elif constraint_type == "MW":
            constraint_var = "pG"

        
        #Create sub_block within instance.MUON for the constraint to contain UB and LB constraints
        setattr(MUON_block, constraint, Block())
        constraint_block = getattr(MUON_block, constraint)

        #Create constraints for upper and lower bounds as required
        for bound, suffix in [[LB, '_LB'], [UB, '_UB']]:
            if bound is not None:
                if callable(bound) == False:
                    if suffix == '_LB':
                        constraint_block.add_component(suffix,
                                                       Constraint(rule = sum(getattr(instance, constraint_var)[g] 
                                                                             for g in getattr(instance, 'G_'+constraint))
                                                                             >= bound))
                    if suffix == '_UB':
                        constraint_block.add_component(suffix,
                                                       Constraint(rule = sum(getattr(instance, constraint_var)[g] 
                                                                             for g in getattr(instance, 'G_'+constraint))
                                                                             <= bound))
                else:                  
                    if suffix == '_LB':
                        constraint_block.add_component(suffix,
                                                       Constraint(rule = sum(getattr(instance, constraint_var)[g] 
                                                                             for g in getattr(instance, 'G_'+constraint))
                                                                             >= bound()))
                    if suffix == '_UB':
                        constraint_block.add_component(suffix,
                                                       Constraint(rule = sum(getattr(instance, constraint_var)[g] 
                                                                             for g in getattr(instance, 'G_'+constraint))
                                                                             <= bound()))
            ...
    added_constraints += [constraint]
    print(f"The following MUON constraints have been added to the model \n {added_constraints}")

def MUON_NB_BigM_constraints(case, instance, constraint_dict, selected_constraints = None):

    #Define handling of default constraints to activate
    if selected_constraints == None:
        print("No MUON_NB Big-M Constraints Defined")
        return
        
    #Create dictionary of MUON constraint groups defined within the case
    constraints_in_case_dict = helpers.comma_param_as_index_to_dict(case, 'generators', 'name', 'MUON_group')

    #Check if sets have been defined in case, and raise error if not.
    empty_constraint_sets = []
    for constraint in selected_constraints:
        if constraint not in constraints_in_case_dict.keys():
            empty_constraint_sets += [constraint]
    if len(empty_constraint_sets) > 0:
        raise KeyError(f"No generator sets are defined for the followin MUON NB-BigM constraints in the case xls: {empty_constraint_sets} ")

    #Add constraint sets to model
    added_sets = []
    for constraint in selected_constraints:
        constraint_set = Set(within = instance.G,
                                initialize = constraints_in_case_dict[constraint],
                                dimen = 1)
        instance.add_component('G_'+constraint, constraint_set)
        added_sets += [constraint]
    print(f"The following NB-BigM contraint sets have been added to the model \n {added_sets}")

    #Constraints Block
    instance.MUON_NB_BigM = Block()

    if "S_NBMIN_CPS" in selected_constraints:
        #TODO Update limit values to real Ireland system

        #Create Demand Binary Parameter (Function defined to be called in main body, so as to update each iteration)
        instance.MUON_NB_BigM.bMparam_y_D_CPS = Param(within = Binary, initialize = 0, mutable = True)
        
        #Create variables for generation and overall control
        instance.MUON_NB_BigM.bMvar_y_G_CPS = Var(domain = Binary)
        instance.MUON_NB_BigM.bMvar_y_CPS = Var(domain = Binary)
        #Create big-M parameters
        instance.MUON_NB_BigM.bMparam_M_G_CPS_L = constraint_dict["S_NBMIN_CPS"]["pGlim"] - sum(instance.PGmin[g] for g in instance.G_NI_Wind)
        instance.MUON_NB_BigM.bMparam_M_G_CPS_U = sum(instance.PGmax[g] for g in instance.G_NI_Wind) - constraint_dict["S_NBMIN_CPS"]["pGlim"]
        #Add constraints
        instance.MUON_NB_BigM.bMconst_M_CPS_L = Constraint(rule = constraint_dict["S_NBMIN_CPS"]["pGlim"] - sum(instance.pG[g] for g in instance.G_NI_Wind) <= instance.MUON_NB_BigM.bMparam_M_G_CPS_L * instance.MUON_NB_BigM.bMvar_y_G_CPS)
        instance.MUON_NB_BigM.bMconst_M_CPS_U = Constraint(rule = sum(instance.pG[g] for g in instance.G_NI_Wind) - constraint_dict["S_NBMIN_CPS"]["pGlim"] <=  instance.MUON_NB_BigM.bMparam_M_G_CPS_U * (1-instance.MUON_NB_BigM.bMvar_y_G_CPS))
        instance.MUON_NB_BigM.bMconst_y_G_CPS_limit = Constraint(rule = instance.MUON_NB_BigM.bMvar_y_CPS <= instance.MUON_NB_BigM.bMvar_y_G_CPS)
        instance.MUON_NB_BigM.bMconst_y_D_CPS_limit = Constraint(rule = instance.MUON_NB_BigM.bMvar_y_CPS <= instance.MUON_NB_BigM.bMparam_y_D_CPS)
        instance.MUON_NB_BigM.bMconst_y_CPS_limit = Constraint(rule = instance.MUON_NB_BigM.bMvar_y_CPS >= instance.MUON_NB_BigM.bMparam_y_D_CPS + instance.MUON_NB_BigM.bMvar_y_G_CPS - 1)
        instance.MUON_NB_BigM.S_NBMIN_CPS = Constraint(rule = sum(instance.u_g[g] for g in instance.G_S_NBMIN_CPS) >= constraint_dict["S_NBMIN_CPS"]["Ug_LB"] * instance.MUON_NB_BigM.bMvar_y_CPS)
        print(f"Big-M NB constraint [S_NBMIN_CPS] added to instance")


    if "S_NBMIN_MP_NB" in selected_constraints:
        #TODO Update limit values to real Ireland system

        #Create variables for generation and overall control
        instance.MUON_NB_BigM.bMvar_y_G_MP_NB = Var(domain = Binary)
        #Create big-M parameters
        instance.MUON_NB_BigM.bMparam_M_G_MP_NB_L = constraint_dict["S_NBMIN_MP_NB"]["pGlim"] - sum(instance.PGmin[g] for g in instance.G_ROI_Wind)
        instance.MUON_NB_BigM.bMparam_M_G_MP_NB_U = sum(instance.PGmax[g] for g in instance.G_ROI_Wind) - constraint_dict["S_NBMIN_MP_NB"]["pGlim"]
        #Add constraints
        instance.MUON_NB_BigM.bMconst_M_MP_NB_L = Constraint(rule = constraint_dict["S_NBMIN_MP_NB"]["pGlim"] - sum(instance.pG[g] for g in instance.G_ROI_Wind) <= instance.MUON_NB_BigM.bMparam_M_G_MP_NB_L * instance.MUON_NB_BigM.bMvar_y_G_MP_NB)
        instance.MUON_NB_BigM.bMconst_M_MP_NB_U = Constraint(rule = sum(instance.pG[g] for g in instance.G_ROI_Wind) - constraint_dict["S_NBMIN_MP_NB"]["pGlim"] <=  instance.MUON_NB_BigM.bMparam_M_G_MP_NB_U * (1-instance.MUON_NB_BigM.bMvar_y_G_MP_NB))
        instance.MUON_NB_BigM.S_NBMIN_MP_NB = Constraint(rule = sum(instance.u_g[g] for g in instance.G_S_NBMIN_MP_NB) >= constraint_dict["S_NBMIN_MP_NB"]["Ug_LB"] * instance.MUON_NB_BigM.bMvar_y_G_MP_NB)
        print(f"Big-M NB constraint [S_NBMIN_MP_NB] added to instance")

def MUON_conditional_activation(instance, constraint_dict, selected_constraints = None):
        MUON_block = getattr(instance, "MUON")
        

        for constraint in selected_constraints:
            #Get constraint condition
            constraint_condition = constraint_dict.get(constraint).get('Condition', None)

            #Check if a condition applies to constraint. if it does and isn't met then continue to next constraint
            if constraint_condition is None:
                continue
            else:
                if constraint_condition() == True:
                    getattr(MUON_block, constraint) .activate()

                if constraint_condition() == False:
                    print(f"The requirement for constraint {constraint} to apply has not been met, so it has not been applied")
                    continue

def MUON_NB_BigM_param_update(instance, constraint_dict):
    #Update y binary parameter for S_NBMIN_CPS
    if sum(instance.PD[d].value for d in instance.D_NI) >= constraint_dict["S_NBMIN_CPS"]["PDlim"]:
        instance.MUON_NB_BigM.bMparam_y_D_CPS = 1
    else:
        instance.MUON_NB_BigM.bMparam_y_D_CPS = 0


#========== START OF MODEL FUNCTION =============#




def model(case: object, solver):
    #Create Model & Instance
    model = AbstractModel()
    instance = model.create_instance()
    #instance.dual = Suffix(direction=Suffix.IMPORT)

    #Create Data Ouput & Result Dictionaries
    output = {"format": "iteration"}
    result = {"format": "iteration"}

    #Define list of sets for model and add to model
    setlist = [
        ComponentName.B,
        ComponentName.b0,
        ComponentName.G,
        ComponentName.generator_mapping,
        ComponentName.G_prorata,
        ComponentName.G_prorata_map,
        ComponentName.G_prorata_pairs,
        ComponentName.G_individual,
        ComponentName.G_uncontrollable,
        ComponentName.G_s,
        ComponentName.G_ns,
        ComponentName.prorata_groups,
        ComponentName.L,
        #ComponentName.L_nonzero, #Defined each timestep
        ComponentName.bus_line_in,
        ComponentName.bus_line_out,
        ComponentName.line_busses,
        ComponentName.TRANSF,
        #ComponentName.TRANSF_nonzero, #Defined each timestep
        ComponentName.bus_transformer_in,
        ComponentName.bus_transformer_out,
        ComponentName.transformer_busses,
        ComponentName.D,
        ComponentName.DNeg,
        ComponentName.demand_bus_mapping,
    ]
    build_sets(instance, case, setlist)

    #ROI & NI Demand Sets
    instance.D_ROI = Set(within = instance.D, initialize = list(case.demands\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: d['zone'] == 'ROI']['name']))
    instance.D_NI = Set(within = instance.D, initialize = list(case.demands\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: d['zone'] == 'NI']['name']))

    #ROI & NI Generator Sets
    instance.G_ROI = Set(within = instance.G, initialize = list(case.generators\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: d['zone'] == 'ROI']['name']))
    instance.G_NI = Set(within = instance.G, initialize = list(case.generators\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: d['zone'] == 'NI']['name']))

    #ROI & NI Wind Only Sets
    instance.G_ROI_Wind = Set(within = instance.G, initialize = list(case.generators\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: (d['zone'] == 'ROI') & (d['FuelType'] == 'Wind')]['name']))

    instance.G_NI_Wind = Set(within = instance.G, initialize = list(case.generators\
                                                                .merge(case.busses[['name', 'zone']],
                                                                       how = 'inner',
                                                                       left_on = 'busname',
                                                                       right_on = 'name',
                                                                       suffixes = ('', '_drop'))\
                                                                .drop(columns='name_drop')\
                                                                .loc[lambda d: (d['zone'] == 'NI') & (d['FuelType'] == 'Wind')]['name']))



    #Define time dependent sets (to be updated each iteration)
    ts_sets = [ComponentName.L_nonzero,
               ComponentName.TRANSF_nonzero] 

    #Define list of parameters for model and add to model
    paramlist = [
        ComponentName.line_max_continuous_P, #Defined each timestep
        ComponentName.line_susceptance,
        ComponentName.line_reactance,
        ComponentName.transformer_max_continuous_P, #Defined each timestep
        ComponentName.transformer_susceptance,
        ComponentName.transformer_reactance,
        ComponentName.PD, #Defined each timestep
        ComponentName.VOLL, #Defined each timestep
        ComponentName.PGmax, #Defined each timestep
        ComponentName.PGmin, #Defined each timestep
        ComponentName.PGMINGEN,
        ComponentName.c_0, #Defined each timestep
        ComponentName.c_1,
        ComponentName.c_bid, #Defined each timestep
        ComponentName.c_offer, #TODO - Define for each timestep
        ComponentName.baseMVA,
        ComponentName.SNSP_curtailment
    ]
    build_params(instance, case, paramlist)

    #Define time dependent parameters (to be updated each iteration)
    ts_params = [ComponentName.PD,
                ComponentName.VOLL,
                ComponentName.line_max_continuous_P,
                ComponentName.transformer_max_continuous_P,
                ComponentName.PGmin,
                ComponentName.PGmax,
                ComponentName.PGMINGEN,
                ComponentName.c_bid] 

    #Special Model Parameters
    instance.PG_MARKET = Param(instance.G,
                            within = Reals,
                            initialize = {g: 0 for g in instance.G},
                            mutable = True)

    instance.UG_MARKET = Param(instance.G,
                                within = Binary,
                                initialize = {g: 0 for g in instance.G},
                                mutable = True) 

    #Special Model Parameters
    instance.PG_SECURE = Param(instance.G,
                            within = Reals,
                            initialize = {g: 0 for g in instance.G},
                            mutable = True)

    instance.UG_SECURE = Param(instance.G,
                                within = Binary,
                                initialize = {g: 0 for g in instance.G},
                                mutable = True) 

    #Define list of variables for model and add to model
    varlist = [
        ComponentName.pG,
        ComponentName.pG_bid,
        ComponentName.pG_offer,
        ComponentName.u_g,
        ComponentName.pD,
        ComponentName.alpha,
        ComponentName.xi_cg,
        ComponentName.xi_prorata,
        ComponentName.beta_prorata,
        ComponentName.prorata_minimum_zeta,
        ComponentName.prorata_curtailment_zeta,
        ComponentName.deltaL,
        ComponentName.deltaLT,
        ComponentName.delta,
        ComponentName.pL,
        ComponentName.pLT,
    ]
    build_variables(instance, varlist)

    #Preload First Iteration Params & Sets
    add_iteration_params_to_instance(instance, case, ts_params, case.iterations[0])
    add_iteration_sets_to_instance(instance, case, ts_sets, case.iterations[0])

    #COPPER PLATE MARKET MODEL CONSTRAINTS #
    copper_plate_market_constraints = [#Power Balance & Demand Constraints
                                ComponentName.KCL_copperplate,
                                ComponentName.demand_real_alpha_controlled,
                                ComponentName.demand_alpha_max,
                                ComponentName.demand_alpha_fixneg,
                                 
                                #Generation Constraints
                                ComponentName.gen_forced_individual_realpower_min,
                                ComponentName.gen_forced_individual_realpower_max,
                                ComponentName.gen_uc_min,
                                ComponentName.gen_uc_max]
    build_constraints(instance, copper_plate_market_constraints)

    #COPPER PLATE SECURE MODEL CONSTRAINTS #
    copper_plate_secure_constraints = [#constraints for market re-dispatch, pro-rata cosntraint, and SNSP
                                ComponentName.gen_market_redispatch,
                                ComponentName.gen_prorata_curtailment_realpower,
                                ComponentName.gen_SNSP]
    build_constraints(instance, copper_plate_secure_constraints)
    

    #- MUON MW Constraints
    #TODO - Update limits for Ireland
    MUON_MW_constraint_dict={
        "S_MWMAX_NI_GT": {
            "PG_LB": None,
            "PG_UB": 80/instance.baseMVA,
            "type": "MW" 
        },
        "S_MWMIN_EWIC": {
            "PG_LB": -526/instance.baseMVA ,
            "PG_UB": None,
            "type": "MW" 
        },
        "S_MWMAX_EWIC": {
            "PG_LB": None,
            "PG_UB": 504/instance.baseMVA,
            "type": "MW"   
        },
        "S_MWMIN_MOYLE": {
            "PG_LB": -410/instance.baseMVA ,
            "PG_UB": None,
            "type": "MW" 
        },
        "S_MWAX_MOYLE": {
            "PG_LB": None,
            "PG_UB": 441/instance.baseMVA,
            "type": "MW"    
        },
        "S_REP_ROI": {
            "PG_LB": None,
            "PG_UB": lambda: sum(instance.PGmax[g] for g in instance.G_S_REP_ROI) - 80/instance.baseMVA,
            "type": "MW"  
        },
        "S_MWMAX_CRK_MW": {
            "PG_LB": None,
            "PG_UB": 1370/instance.baseMVA,
            "type": "MW"   
        },
        "S_MWMAX_STH_MW": {
            "PG_LB": None,
            "PG_UB": 1835/instance.baseMVA,
            "type": "MW"   
        },
    }
    MUON_MW_constraint_list = ['S_MWMAX_NI_GT']
    MUON_constraints(case, instance, MUON_MW_constraint_dict, selected_constraints = MUON_MW_constraint_list)
    
    
    #- MUON NB Constraints
    MUON_NB_constraint_dict={
        "S_NBMIN_MINNIU": {
            "Condition": None,
            "Ug_LB": 3,
            "Ug_UB": None,
            "type": "NB"  
        },
        "S_NBMIN_MINNI3": {
            "Condition": None,
            "Ug_LB": 1,
            "Ug_UB": None,
            "type": "NB" 
        },
        "S_NBMIN_ROImin": {
            "Condition": None,
            "Ug_LB": 4,
            "Ug_UB": None,
            "type": "NB" 
        },
        "S_NBMIN_DubNB": {
            "Condition": None,
            "Ug_LB": 1,
            "Ug_UB": None,
            "type": "NB" 
        },
        "S_NBMIN_DubNB2": {
            "Condition": None,
            "Ug_LB": 2,
            "Ug_UB": None,
            "type": "NB" 
        },
        "S_NBMIN_DUB_L1": {
            "Condition": lambda: sum(instance.PD[d].value for d in instance.D_ROI) >= 4000/instance.baseMVA,
            "Ug_LB": 3,
            "Ug_UB": None,
            "type": "NB" 
        },
        "S_NBMIN_DUB_L2": {
            "Condition": lambda: sum(instance.PD[d].value for d in instance.D_ROI) >= 0/instance.baseMVA,
            "Ug_LB": 1,
            "Ug_UB": None,
            "type": "NB" 
        },
        "MP5_NB": {
            "Ug_LB": None,
            "Ug_UB": 1,
            "type": "NB" 
        },
    }
    MUON_NB_constraints_list = ['S_NBMIN_DUB_L2']
    MUON_constraints(case, instance, MUON_NB_constraint_dict, selected_constraints = MUON_NB_constraints_list)
    
    #- MUON NB Big-M Constraints
    MUON_NB_bigM_constraint_dict={
            "S_NBMIN_CPS": {
                #TODO Update limit values to real Ireland system
                "PDlim": 100/instance.baseMVA, #When demand above this value
                "pGlim": 25/instance.baseMVA, #And wind in NI below this value
                "Ug_LB": 1,
                "Ug_UB": None, 
            },
            "S_NBMIN_MP_NB": {
                #TODO Update limit values to real Ireland system
                "pGlim": 40/instance.baseMVA, #When wind generation in ROI less than                                    
                "Ug_LB": 1,
                "Ug_UB": None, 
            },

    }
    MUON_NB_bigM_constraints_list = []
    MUON_NB_BigM_constraints(case, instance, MUON_NB_bigM_constraint_dict, selected_constraints = MUON_NB_bigM_constraints_list)

    #DCOPF MODEL CONSTRAINTS #
    dcopf_constraints = [#Power Balance - Kirchoffs Current Law (P
                        ComponentName.KCL_networked_realpower_noshunt,
                        #Power Flow - Kirchoffs Voltage Law
                        ComponentName.KVL_DCOPF_lines,
                        ComponentName.KVL_DCOPF_transformer,
                        #Power Flow - Power Line Operational Limits
                        ComponentName.line_cont_realpower_max_ngtve,
                        ComponentName.line_cont_realpower_max_pstve,
                        ComponentName.volts_line_delta,
                        #Power Flow - Transformer Line Operational Limits
                        ComponentName.transf_continuous_real_max_ngtve,
                        ComponentName.transf_continuous_real_max_pstve,
                        ComponentName.volts_transformer_delta,
                        #Reference bus voltage
                        ComponentName.volts_reference_bus,
                        #Redispatch COnstraint
                        ComponentName.gen_secure_redispatch,
                        #Pro-Rata Constraint Group Constraints
                        ComponentName.gen_prorata_realpower_max_xi,
                        ComponentName.gen_prorata_realpower_min_xi,
                        ComponentName.gen_prorata_xi_max,
                        ComponentName.gen_prorata_xi_min,
                        ComponentName.gen_prorata_beta,
                    ]
    build_constraints(instance, dcopf_constraints)

    #Deactivate all constraints ready for iteration
    global_constraints = ['KCL_copperplate', 'demand_real_alpha_controlled', 'demand_alpha_max', 'demand_alpha_fixneg', 'gen_uc_min', 'gen_uc_max', 'gen_forced_individual_realpower_min', 'gen_forced_individual_realpower_max', 'gen_market_redispatch', 'gen_prorata_curtailment_realpower', 'gen_SNSP', 'KCL_networked_realpower_noshunt', 'KVL_DCOPF_lines', 'KVL_DCOPF_transformer', 'line_cont_realpower_max_ngtve', 'line_cont_realpower_max_pstve', 'volts_line_delta', 'transf_continuous_real_max_ngtve', 'transf_continuous_real_max_pstve', 'volts_transformer_delta', 'volts_reference_bus', 'gen_secure_redispatch', 'gen_prorata_realpower_max_xi', 'gen_prorata_realpower_min_xi', 'gen_prorata_xi_max', 'gen_prorata_xi_min', 'gen_prorata_beta']
    block_constraints =  ['MUON', 'MUON_NB_BigM']
    for c in global_constraints:
        getattr(instance, c).deactivate()
    for block in block_constraints:
        getattr(instance, block).deactivate()




    #MODEL ITERATIONS
    for iteration in case.iterations:
        #Create new output & result dictionary space
        output[iteration] = {}
        result[iteration] = {}

        #~~~~~~~~~~~# ITERATION INPUT DATA UPDATES #~~~~~~~~~~~#
        #Update parameters for current timestep
        add_iteration_params_to_instance(instance, case, ts_params, iteration)

        #Update big-M binary parameters for this iteration
        MUON_NB_BigM_param_update(instance, MUON_NB_bigM_constraint_dict)

        #Update any sets for current timestep
        add_iteration_sets_to_instance(instance, case, ts_sets, iteration)

        #~~~~~~~~~~~# COPPER PLATE MARKET MODEL SECTION #~~~~~~~~~~~#
        market_constraints_to_activate = [#Add Power Balance & Demand
                                   ComponentName.KCL_copperplate,
                                   ComponentName.demand_real_alpha_controlled,
                                   ComponentName.demand_alpha_max,
                                   ComponentName.demand_alpha_fixneg,
                                   #Add Generation Constraints
                                   ComponentName.gen_forced_individual_realpower_min,
                                   ComponentName.gen_forced_individual_realpower_max
                                ]
        
        for c in market_constraints_to_activate:
            getattr(instance, c).activate()
        
        #Set Objective
        instance.OBJ = Objective(rule = copper_plate_marginal_cost_objective(instance), sense = minimize)

        #Solve Copperplate Model Run
        result[iteration]["copper_market"] = pyosolve.solveinstance(instance, solver = solver)

        #Define Output Parameters
        for g in instance.G:
            instance.PG_MARKET[g] = round(instance.pG[g].value, 6)

        # #Define Data to Save
        # data_to_cache = {"Var": [], 
        #             "Param" : [],
        #             "Set" : []}
        
        # #Cache Data
        # output[iteration]["copper_market"] = pyomo_io.InstanceCache(result[iteration]["copper_market"], data_to_cache)
        # output[iteration]["copper_market"].set(instance)
        # output[iteration]["copper_market"].var(instance)
        # output[iteration]["copper_market"].param(instance)
        # output[iteration]["copper_market"].obj_value(instance)

        #~~~~~~~~~~~# COPPER PLATE 'SECURE' MODEL SECTION #~~~~~~~~~~~#
        #Remove generation constraint that doesn't respect on/off states.
        constraints_to_deactivate_for_secure = [#Generation constraints used in previous models (superceeded by updated PGmax)
                                 ComponentName.gen_forced_individual_realpower_min,
                                 ComponentName.gen_forced_individual_realpower_max]
        
        for c in constraints_to_deactivate_for_secure:
            getattr(instance, c).deactivate()

        #Add Constraints (Except MUON Constraints)
        secure_constraints_to_activate = [#Respecting Minimum Generation
                                          ComponentName.gen_uc_min,
                                          ComponentName.gen_uc_max,  
            
                                        #Market Redispatch
                                         ComponentName.gen_market_redispatch,
                                         #Prorata Curtailment
                                         ComponentName.gen_prorata_curtailment_realpower,
                                         #SNSP
                                         ComponentName.gen_SNSP
                                         ]

        for c in secure_constraints_to_activate:
            getattr(instance, c).activate()


        #Activate overall MUON docs
        getattr(instance, "MUON").activate()
        getattr(instance, "MUON_NB_BigM").activate()

        #Conditionally activate MUON MW and NB constraints
        MUON_conditional_activation(instance,
                                    MUON_MW_constraint_dict | MUON_NB_constraint_dict,
                                    MUON_MW_constraint_list + MUON_NB_constraints_list)
    
        #Update Objective
        instance.del_component(instance.OBJ)
        instance.OBJ = Objective(rule = redispatch_from_market_cost_objective(instance), sense = minimize)
                        
        #Solve Copperplate Model Run
        result[iteration]["copper_curtailed"] = pyosolve.solveinstance(instance, solver = solver)

        #Define Output Parameters
        for g in instance.G:
            instance.PG_SECURE[g] = round(instance.pG[g].value, 6)

        for g in instance.G:
            instance.UG_SECURE[g] = round(instance.u_g[g].value, 0)

        # #Define Data to Save
        # data_to_cache = {"Var": [], 
        #             "Param" : [],
        #             "Set" : []}
        
        # #Cache Data
        # output[iteration]["copper_curtailed"] = pyomo_io.InstanceCache(result[iteration]["copper_curtailed"], data_to_cache)
        # output[iteration]["copper_curtailed"].set(instance)
        # output[iteration]["copper_curtailed"].var(instance)
        # output[iteration]["copper_curtailed"].param(instance)
        # output[iteration]["copper_curtailed"].obj_value(instance)


        #~~~~~~~~~~~# DCOPF MODEL SECTION #~~~~~~~~~~~#
        #Remove Constraints No Longer Needed
        constraints_to_deactivate_for_dcopf = [#Generation constraints used in previous models (superceeded by updated PGmax)
                                 ComponentName.gen_market_redispatch,
                                 ComponentName.gen_prorata_curtailment_realpower,
                                 
                                 #Remove Copperplate KCL Constraint
                                 ComponentName.KCL_copperplate
                                 ]
        
        for c in constraints_to_deactivate_for_dcopf:
            getattr(instance, c).deactivate()

        #Rebuild constraints with variable set dimensions (Line and Transformers):
        constraints_to_rebuild = [ComponentName.KVL_DCOPF_lines, ComponentName.KVL_DCOPF_transformer]
        build_constraints(instance, constraints_to_rebuild)

        #Activate in dcopf constraints
        dcopf_constraints_to_activate = [#Power Balance - Kirchoffs Current Law (P
                                     ComponentName.KCL_networked_realpower_noshunt,
                                    
                                     #Power Flow - Kirchoffs Voltage Law
                                     ComponentName.KVL_DCOPF_lines,
                                     ComponentName.KVL_DCOPF_transformer,
                                    
                                     #Power Flow - Power Line Operational Limits
                                     ComponentName.line_cont_realpower_max_ngtve,
                                     ComponentName.line_cont_realpower_max_pstve,
                                     ComponentName.volts_line_delta,

                                     #Power Flow - Transformer Line Operational Limits
                                     ComponentName.transf_continuous_real_max_ngtve,
                                     ComponentName.transf_continuous_real_max_pstve,
                                     ComponentName.volts_transformer_delta,

                                     #Reference bus voltage
                                     ComponentName.volts_reference_bus,

                                     #Redispatch Constraint
                                     ComponentName.gen_secure_redispatch,

                                     #Pro-Rata Constraint Group Constraints
                                     ComponentName.gen_prorata_realpower_max_xi,
                                     ComponentName.gen_prorata_realpower_min_xi,
                                     ComponentName.gen_prorata_xi_max,
                                     ComponentName.gen_prorata_xi_min,
                                     ComponentName.gen_prorata_beta,
                                    ]
    
        for c in dcopf_constraints_to_activate:
            getattr(instance, c).activate()

        #Update Objective
        instance.del_component(instance.OBJ)
        instance.OBJ = Objective(rule = redispatch_from_secure_cost_objective(instance), sense = minimize)


        result[iteration]["dcopf"] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output[iteration]["dcopf"] = pyomo_io.InstanceCache(result[iteration]["dcopf"], data_to_cache)
        output[iteration]["dcopf"].set(instance)
        output[iteration]["dcopf"].var(instance)
        output[iteration]["dcopf"].param(instance)
        output[iteration]["dcopf"].obj_value(instance)

        #~~~~~~~~~~~# COPPER PLATE TEST CODE RESET #~~~~~~~~~~~#
        #list of constraints to deactivate
        constraints_to_deactivate_to_end_dcopf = [
                                     #Generation
                                     'gen_uc_max', 'gen_uc_min',
                                     #SNSP Constraint
                                     'gen_SNSP',
                                     #KCL Power Balance
                                     'KCL_networked_realpower_noshunt',
                                     #KVL Power FLow
                                     'KVL_DCOPF_lines', 'KVL_DCOPF_transformer', 'line_cont_realpower_max_ngtve', 'line_cont_realpower_max_pstve', 'volts_line_delta', 'transf_continuous_real_max_ngtve', 'transf_continuous_real_max_pstve', 'volts_transformer_delta', 'volts_reference_bus',
                                     #Redispatch 
                                     'gen_secure_redispatch',
                                     #Prorata Curtailment
                                     'gen_prorata_realpower_max_xi', 'gen_prorata_realpower_min_xi', 'gen_prorata_xi_max', 'gen_prorata_xi_min', 'gen_prorata_beta',
                                     #MUON Constraint Blocks
                                    'MUON', 'MUON_NB_BigM']
        
        for c in constraints_to_deactivate_to_end_dcopf:
            getattr(instance, c).deactivate()
        
        #Delete objective
        instance.del_component(instance.OBJ)
    
        #~~~~~~~~~~~# CALCULATE CURTAILMENT AND CONSTRAINT VOLUMES #~~~~~~~~~~~#
        #Calculate overall surplus volumes, and surplus per generator
        setattr(output[iteration]["dcopf"], 'V_Surplus', sum((instance.PGmax[g].value - instance.PG_MARKET[g].value) for g in instance.G_ns))
        setattr(output[iteration]["dcopf"], 'v_Surplus_g', {g: (instance.PGmax[g].value - instance.PG_MARKET[g].value) for g in instance.G_ns})
        output[iteration]["dcopf"].v_Surplus_g.update({g: 0 for g in instance.G_s})
        

        #Calculate overall SNSP volume. Then divide by non-synchronous generators pro-rata.
        setattr(output[iteration]["dcopf"], 'V_SNSP', max(0, sum(instance.PG_MARKET[g].value for g in instance.G_ns) - 0.75*sum(instance.PG_MARKET[g].value for g in instance.G)))
        setattr(output[iteration]["dcopf"], 'x_SNSP', max(0, sum(instance.PG_MARKET[g].value for g in instance.G_ns)/sum(instance.PG_MARKET[g].value for g in instance.G_ns) - 0.75))
        setattr(output[iteration]["dcopf"], 'v_SNSP_g', {g: (instance.PG_MARKET[g].value * output[iteration]["dcopf"].x_SNSP) for g in instance.G_ns})
        output[iteration]["dcopf"].v_SNSP_g.update({g: 0 for g in instance.G_s})

        #Calculate overall MUON volume. Then divide by non-synchronous generators pro-rata
        setattr(output[iteration]["dcopf"], 'V_MUON', sum((instance.PG_MARKET[g].value - instance.PG_SECURE[g].value) for g in instance.G_ns) - output[iteration]["dcopf"].V_SNSP)
        setattr(output[iteration]["dcopf"], 'x_MUON', output[iteration]["dcopf"].V_MUON / sum(instance.PG_MARKET[g].value for g in instance.G_ns))
        setattr(output[iteration]["dcopf"], 'v_MUON_g', {g: (instance.PG_MARKET[g].value * output[iteration]["dcopf"].x_MUON) for g in instance.G_ns})
        output[iteration]["dcopf"].v_MUON_g.update({g: 0 for g in instance.G_s})

        #Calculate overall constraint volume.
        setattr(output[iteration]["dcopf"],'V_Constraint', sum((instance.PG_SECURE[g].value - instance.pG[g].value) for g in instance.G_ns))
        setattr(output[iteration]["dcopf"],'x_Constraint',{g: (instance.PG_SECURE[g].value - instance.pG[g].value)/instance.PG_SECURE[g].value if instance.PG_SECURE[g].value > 0 else 0 for g in instance.G_ns})
        setattr(output[iteration]["dcopf"], 'v_Constraint_g',{g: (instance.PG_SECURE[g].value - instance.pG[g].value) for g in instance.G_ns})
        output[iteration]["dcopf"].v_Constraint_g.update({g: 0 for g in instance.G_s})
        ...


    return output, result







