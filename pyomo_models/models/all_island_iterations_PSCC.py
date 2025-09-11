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


def MUON_MW_constraints(case, instance, selected_constraints = None):

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

    #Dictionary of constraints & bounds
    constraint_dict={
        "S_MWMAX_NI_GT": {
            "PG_LB": None,
            "PG_UB": 272/instance.baseMVA 
        },
        "S_MWMIN_EWIC": {
            "PG_LB": -526/instance.baseMVA ,
            "PG_UB": None 
        },
        "S_MWMAX_EWIC": {
            "PG_LB": None,
            "PG_UB": 504/instance.baseMVA  
        },
        "S_MWMIN_MOYLE": {
            "PG_LB": -410/instance.baseMVA ,
            "PG_UB": None
        },
        "S_MWAX_MOYLE": {
            "PG_LB": None,
            "PG_UB": 441/instance.baseMVA   
        },
        "S_REP_ROI": {
            "PG_LB": None,
            "PG_UB": lambda: sum(instance.PGmax[g] for g in instance.G_S_REP_ROI) - 80/instance.baseMVA 
        },
        "S_MWMAX_CRK_MW": {
            "PG_LB": None,
            "PG_UB": 1370/instance.baseMVA  
        },
        "S_MWMAX_STH_MW": {
            "PG_LB": None,
            "PG_UB": 1835/instance.baseMVA  
        },
    }

    #Add sets of generator to model if (a) they're selected, and (b) they have been defined in the case
    added_sets = []
    for constraint in selected_constraints:
        constraint_set = Set(within = instance.G,
                                initialize = constraints_in_case_dict[constraint],
                                dimen = 1)
        instance.add_component('G_'+constraint, constraint_set)
        added_sets += [constraint]
    print(f"Sets for the following MW contraints have been added to the model \n {added_sets}")
           
    #Add Constraints into Model
    instance.MUON_MW = Block()

    added_constraints = []
    for constraint in selected_constraints:
        #Apply LB constraint (checks if callable function for bounds with a formula)
        if constraint_dict.get(constraint).get('PG_LB') is not None:
            if callable(constraint_dict.get(constraint).get('PG_LB')) == False:
                instance.MUON_MW.add_component(constraint+'_LB', Constraint(rule = sum(instance.pG[g] for g in getattr(instance, 'G_'+constraint)) >= constraint_dict.get(constraint).get('PG_LB')))
            else:
                instance.MUON_MW.add_component(constraint+'_LB', Constraint(rule = sum(instance.pG[g] for g in getattr(instance, 'G_'+constraint)) >= constraint_dict.get(constraint).get('PG_LB')()))
            added_constraints += [constraint+'_LB']
        #Apply UB constraint (checks if callable function for bounds with a formula)
        if constraint_dict.get(constraint).get('PG_UB') is not None:
            if callable(constraint_dict.get(constraint).get('PG_UB')) == False:
                instance.MUON_MW.add_component(constraint+'_UB', Constraint(rule = sum(instance.pG[g] for g in getattr(instance, 'G_'+constraint)) <= constraint_dict.get(constraint).get('PG_UB')))
            else:
                instance.MUON_MW.add_component(constraint+'_UB', Constraint(rule = sum(instance.pG[g] for g in getattr(instance, 'G_'+constraint)) <= constraint_dict.get(constraint).get('PG_UB')()))
            added_constraints += [constraint+'_UB']


    print(f"The following MW constraints have been added to the model \n {added_constraints}")
    ...

def MUON_NB_constraints(case, instance, selected_constraints = None):

    #Define handling of default constraints to activate
    if selected_constraints == None:
        print("No MUON_NB Constraints Defined")
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
    

    #Dictionary of constraints & bounds
    constraint_dict={
        "S_NBMIN_MINNIU": {
            "Condition": None,
            "Ug_LB": 3,
            "Ug_UB": None 
        },
        "S_NBMIN_MINNI3": {
            "Condition": None,
            "Ug_LB": 1,
            "Ug_UB": None 
        },
        "S_NBMIN_ROImin": {
            "Condition": None,
            "Ug_LB": 4,
            "Ug_UB": None 
        },
        "S_NBMIN_DubNB": {
            "Condition": None,
            "Ug_LB": 1,
            "Ug_UB": None 
        },
        "S_NBMIN_DubNB2": {
            "Condition": None,
            "Ug_LB": 2,
            "Ug_UB": None 
        },
        "S_NBMIN_DUB_L1": {
            "Condition": lambda: sum(instance.PD[d].value for d in instance.D_ROI) >= 4000/instance.baseMVA,
            "Ug_LB": 3,
            "Ug_UB": None 
        },
        "S_NBMIN_DUB_L2": {
            "Condition": lambda: sum(instance.PD[d].value for d in instance.D_ROI) >= 0/instance.baseMVA,
            "Ug_LB": 1,
            "Ug_UB": None 
        },
        "MP5_NB": {
            "Ug_LB": None,
            "Ug_UB": 1 
        },
    }

    #Add sets of generator to model if (a) they're selected, and (b) they have been defined in the case
    added_sets = []
    for constraint in selected_constraints:
        constraint_set = Set(within = instance.G,
                                initialize = constraints_in_case_dict[constraint],
                                dimen = 1)
        instance.add_component('G_'+constraint, constraint_set)
        added_sets += [constraint]
    print(f"The following NB contraint sets have been added to the model \n {added_sets}")
    

    #Add Constraints to Model
    instance.MUON_NB = Block()

    added_constraints = []
    for constraint in selected_constraints:
        #Check if a condition applies to constraint. if it does and isn't met then continue to next constraint
        if constraint_dict.get(constraint).get('Condition') is not None:
            if constraint_dict.get(constraint).get('Condition')() == False:
                print(f"The requirement for constraint {constraint} to apply has not been met, so it has not been applied")
                continue
    
            
        #Apply LB constraint (checks if callable function for bounds with a formula)
        if constraint_dict.get(constraint).get('Ug_LB') is not None:
            if callable(constraint_dict.get(constraint).get('Ug_LB')) == False:
                instance.MUON_NB.add_component(constraint+'_LB', Constraint(rule = sum(instance.u_g[g] for g in getattr(instance, 'G_'+constraint)) >= constraint_dict.get(constraint).get('Ug_LB')))
            else:
                instance.MUON_NB.add_component(constraint+'_LB', Constraint(rule = sum(instance.u_g[g] for g in getattr(instance, 'G_'+constraint)) >= constraint_dict.get(constraint).get('Ug_LB')()))
            added_constraints += [constraint+'_LB']
        #Apply UB constraint (checks if callable function for bounds with a formula)
        if constraint_dict.get(constraint).get('Ug_UB') is not None:
            if callable(constraint_dict.get(constraint).get('Ug_UB')) == False:
                instance.MUON_NB.add_component(constraint+'_UB', Constraint(rule = sum(instance.u_g[g] for g in getattr(instance, 'G_'+constraint)) <= constraint_dict.get(constraint).get('Ug_UB')))
            else:
                instance.MUON_NB.add_component(constraint+'_UB', Constraint(rule = sum(instance.u_g[g] for g in getattr(instance, 'G_'+constraint)) <= constraint_dict.get(constraint).get('Ug_UB')()))
            added_constraints += [constraint+'_UB']


    print(f"The following NB constraints have been added to the model \n {added_constraints}")        
    ...

def MUON_NB_BigM_constraints(case, instance, selected_constraints = None):

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
        raise KeyError(f"No generator sets are defined for the followin MUON NB constraints in the case xls: {empty_constraint_sets} ")

    #Add constraint sets to model
    added_sets = []
    for constraint in selected_constraints:
        constraint_set = Set(within = instance.G,
                                initialize = constraints_in_case_dict[constraint],
                                dimen = 1)
        instance.add_component('G_'+constraint, constraint_set)
        added_sets += [constraint]
    print(f"The following NB contraint sets have been added to the model \n {added_sets}")

    constraint_dict={
            "S_NBMIN_CPS": {
                #TODO Update limit values to real Ireland system
                "PDlim": 0/instance.baseMVA,
                "pGlim": 2000/instance.baseMVA,
                "Ug_LB": 1,
                "Ug_UB": None, 
            },
            "S_NBMIN_MP_NB": {
                #TODO Update limit values to real Ireland system
                "pGlim": 130/instance.baseMVA,
                "Ug_LB": 1,
                "Ug_UB": None, 
            },

    }

    #Constraints Block
    instance.MUON_NB_BigM = Block()

    if "S_NBMIN_CPS" in selected_constraints:
        #TODO Update limit values to real Ireland system

        #Create Demand Binary Parameter
        if sum(instance.PD[d].value for d in instance.D_NI) >= constraint_dict["S_NBMIN_CPS"]["PDlim"]:
            y_D_CPS = 1
        else:
            y_D_CPS = 0
        instance.MUON_NB_BigM.bMparam_y_D_CPS = Param(within = Binary, initialize = y_D_CPS)
        
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
        #TODO Ensure demand condition is measured against NI demand only
        #TODO Ensure generation is for wind generation in NI only

        #Create variables for generation and overall control
        instance.MUON_NB_BigM.bMvar_y_G_MP_NB = Var(domain = Binary)
        #Create big-M parameters
        instance.MUON_NB_BigM.bMparam_M_G_MP_NB_L = constraint_dict["S_NBMIN_MP_NB"]["pGlim"] - sum(instance.PGmin[g] for g in instance.G_ns)
        instance.MUON_NB_BigM.bMparam_M_G_MP_NB_U = sum(instance.PGmax[g] for g in instance.G_ns) - constraint_dict["S_NBMIN_MP_NB"]["pGlim"]
        #Add constraints
        instance.MUON_NB_BigM.bMconst_M_MP_NB_L = Constraint(rule = constraint_dict["S_NBMIN_MP_NB"]["pGlim"] - sum(instance.pG[g] for g in instance.G_ns) <= instance.MUON_NB_BigM.bMparam_M_G_MP_NB_L * instance.MUON_NB_BigM.bMvar_y_G_MP_NB)
        instance.MUON_NB_BigM.bMconst_M_MP_NB_U = Constraint(rule = sum(instance.pG[g] for g in instance.G_ns) - constraint_dict["S_NBMIN_MP_NB"]["pGlim"] <=  instance.MUON_NB_BigM.bMparam_M_G_MP_NB_U * (1-instance.MUON_NB_BigM.bMvar_y_G_MP_NB))
        instance.MUON_NB_BigM.S_NBMIN_MP_NB = Constraint(rule = sum(instance.u_g[g] for g in instance.G_S_NBMIN_MP_NB) >= constraint_dict["S_NBMIN_MP_NB"]["Ug_LB"] * instance.MUON_NB_BigM.bMvar_y_G_MP_NB)
        print(f"Big-M NB constraint [S_NBMIN_MP_NB] added to instance")

  
def model(case: object, solver):
    #Create Model & Instance
    model = AbstractModel()
    instance = model.create_instance()
    #instance.dual = Suffix(direction=Suffix.IMPORT)

    #Define Data Outputs
    output = {
        "format": "iteration",
        "copper_market": {},
        "copper_curtailed": {},
        "dcopf_curtailed": {}
    }

    result = {
        "format": "iteration",
        "copper_market": {},
        "copper_curtailed": {},
        "dcopf_curtailed": {}
    }

    #Define list of sets for model and add to model
    setlist = [
        ComponentName.B,
        ComponentName.b0,
        ComponentName.G,
        ComponentName.generator_mapping,
        ComponentName.G_LIFO,
        ComponentName.G_LIFO_pairs,
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
        ComponentName.MINGEN_zeta,
        ComponentName.gamma,
        ComponentName.beta,
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
                                 ComponentName.gen_uc_max,
                                 ComponentName.gen_uc_min]
    build_constraints(instance, copper_plate_market_constraints)

    #COPPER PLATE SECURE MODEL CONSTRAINTS #
    copper_plate_secure_constraints = [#constraints for market re-dispatch, pro-rata cosntraint, and SNSP
                                ComponentName.gen_market_redispatch,
                                ComponentName.gen_prorata_curtailment_realpower,
                                ComponentName.gen_SNSP]
    build_constraints(instance, copper_plate_secure_constraints)
        
    #- MUON MW Constraints
    MUON_MW_constraint_list = ['S_MWMAX_NI_GT', 'S_REP_ROI']
    MUON_MW_constraints(case, instance, selected_constraints = MUON_MW_constraint_list)
    #- MUON NB Constraints
    MUON_NB_constraints_list = ['S_NBMIN_DUB_L2']
    MUON_NB_constraints(case, instance, selected_constraints = MUON_NB_constraints_list)
    #- MUON NB Big-M Constraints
    MUON_NB_bigM_constraints_list = ['S_NBMIN_CPS','S_NBMIN_MP_NB']
    MUON_NB_BigM_constraints(case, instance, selected_constraints = MUON_NB_bigM_constraints_list)

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
    global_constraints = ['KCL_copperplate', 'demand_real_alpha_controlled', 'demand_alpha_max', 'demand_alpha_fixneg', 'gen_uc_max', 'gen_uc_min', 'gen_market_redispatch', 'gen_prorata_curtailment_realpower', 'gen_SNSP', 'KCL_networked_realpower_noshunt', 'KVL_DCOPF_lines', 'KVL_DCOPF_transformer', 'line_cont_realpower_max_ngtve', 'line_cont_realpower_max_pstve', 'volts_line_delta', 'transf_continuous_real_max_ngtve', 'transf_continuous_real_max_pstve', 'volts_transformer_delta', 'volts_reference_bus', 'gen_secure_redispatch', 'gen_prorata_realpower_max_xi', 'gen_prorata_realpower_min_xi', 'gen_prorata_xi_max', 'gen_prorata_xi_min', 'gen_prorata_beta']
    block_constraints =  ['MUON_MW', 'MUON_NB', 'MUON_NB_BigM']
    for c in global_constraints:
        getattr(instance, c).deactivate()
    for block in block_constraints:
        getattr(instance, block).deactivate()








    #MODEL ITERATIONS
    for iteration in case.iterations:
        #Update parameters for current timestep
        add_iteration_params_to_instance(instance, case, ts_params, iteration)

        #Update any sets for current timestep
        add_iteration_sets_to_instance(instance, case, ts_sets, iteration)

        #~~~~~~~~~~~# COPPER PLATE MARKET MODEL SECTION #~~~~~~~~~~~#
        market_constraints_to_activate = [#Add Power Balance & Demand
                                   ComponentName.KCL_copperplate,
                                   ComponentName.demand_real_alpha_controlled,
                                   ComponentName.demand_alpha_max,
                                   ComponentName.demand_alpha_fixneg,
                                   #Add Generation Constraints
                                   ComponentName.gen_uc_max,
                                   ComponentName.gen_uc_min
                                ]
        
        for c in market_constraints_to_activate:
            getattr(instance, c).activate()
        
        #Set Objective
        instance.OBJ = Objective(rule = copper_plate_marginal_cost_objective(instance), sense = minimize)

        #Solve Copperplate Model Run
        result["copper_market"][iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Output Parameters
        for g in instance.G:
            instance.PG_MARKET[g] = round(instance.pG[g].value, 6)

        for g in instance.G:
            instance.UG_MARKET[g] = round(instance.u_g[g].value, 0)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["copper_market"][iteration] = pyomo_io.InstanceCache(result["copper_market"][iteration], data_to_cache)
        output["copper_market"][iteration].set(instance)
        output["copper_market"][iteration].var(instance)
        output["copper_market"][iteration].param(instance)
        output["copper_market"][iteration].obj_value(instance)

        #~~~~~~~~~~~# COPPER PLATE 'SECURE' MODEL SECTION #~~~~~~~~~~~#
        #Add Constraints (Except MUON Constraints)
        secure_constraints_to_activate = [#Market Redispatch
                                         ComponentName.gen_market_redispatch,
                                         #Prorata Curtailment
                                         ComponentName.gen_prorata_curtailment_realpower,
                                         #SNSP
                                         ComponentName.gen_SNSP
                                         ]

        for c in secure_constraints_to_activate:
            getattr(instance, c).activate()

        #Add MUON Constraints
        secure_block_constraints_to_activate = ['MUON_MW', 'MUON_NB', 'MUON_NB_BigM']
        for c in secure_block_constraints_to_activate:
            getattr(instance, c).activate()

        #Update Objective
        instance.del_component(instance.OBJ)
        instance.OBJ = Objective(rule = redispatch_from_market_cost_objective(instance), sense = minimize)
                        
        #Solve Copperplate Model Run
        result["copper_curtailed"][iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Output Parameters
        for g in instance.G:
            instance.PG_SECURE[g] = round(instance.pG[g].value, 6)

        for g in instance.G:
            instance.UG_SECURE[g] = round(instance.u_g[g].value, 0)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["copper_curtailed"][iteration] = pyomo_io.InstanceCache(result["copper_curtailed"][iteration], data_to_cache)
        output["copper_curtailed"][iteration].set(instance)
        output["copper_curtailed"][iteration].var(instance)
        output["copper_curtailed"][iteration].param(instance)
        output["copper_curtailed"][iteration].obj_value(instance)


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

                                     #Redispatch COnstraint
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


        result["dcopf_curtailed"][iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["dcopf_curtailed"][iteration] = pyomo_io.InstanceCache(result["dcopf_curtailed"][iteration], data_to_cache)
        output["dcopf_curtailed"][iteration].set(instance)
        output["dcopf_curtailed"][iteration].var(instance)
        output["dcopf_curtailed"][iteration].param(instance)
        output["dcopf_curtailed"][iteration].obj_value(instance)

        #~~~~~~~~~~~# COPPER PLATE TEST CODE RESET #~~~~~~~~~~~#
        #list of constraints to deactivate
        constraints_to_deactivate_to_end_dcopf = [#SNSP Constraint
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
                                    'MUON_MW', 'MUON_NB', 'MUON_NB_BigM']
        
        for c in constraints_to_deactivate_to_end_dcopf:
            getattr(instance, c).deactivate()
    
        #~~~~~~~~~~~# CALCULATE CURTAILMENT AND CONSTRAINT VOLUMES #~~~~~~~~~~~#
        #Calculate overall surplus volumes, and surplus per generator
        output['V_Surplus'] = sum((instance.PGmax[g].value - instance.PG_MARKET[g].value) for g in instance.G_ns)
        output['v_Surplus_g'] = {g: (instance.PGmax[g].value - instance.PG_MARKET[g].value) for g in instance.G_ns}

        #Calculate overall SNSP volume. Then divide by non-synchronous generators pro-rata.
        output['V_SNSP'] = max(0, sum(instance.PG_MARKET[g].value for g in instance.G_ns) - 0.75*sum(instance.PG_MARKET[g].value for g in instance.G))
        output['x_SNSP'] = max(0, sum(instance.PG_MARKET[g].value for g in instance.G_ns)/sum(instance.PG_MARKET[g].value for g in instance.G) - 0.75)
        output['v_SNSP_g'] = {g: (instance.PG_MARKET[g].value * output['x_SNSP']) for g in instance.G_ns}

        #Calculate overall MUON volume. Then divide by non-synchronous generators pro-rata
        output['V_MUON'] = sum((instance.PG_MARKET[g].value - instance.PG_SECURE[g].value) for g in instance.G_ns) - output['V_SNSP']
        output['x_MUON'] = output['V_MUON'] / sum(instance.PG_MARKET[g].value for g in instance.G_ns)
        output['v_MUON_g'] = {g: (instance.PG_MARKET[g].value * output['x_MUON']) for g in instance.G_ns}
        
        ...


    return output, result







