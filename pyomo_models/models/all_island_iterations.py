from pyomo_models.build.definitions import *
from pyomo_models.build.build_functions import *
from pyomo_models.build.names import *
import data_io.pyomo_io as pyomo_io
import pyomo_models.build.pyosolve as pyosolve
from pyomo_models.build.obj_functions import dcopf_marginal_cost_objective


def model(case: object, solver):
    #Create Model & Instance
    model = AbstractModel()
    instance = model.create_instance()

    #Define Data Outputs
    output = {
        "copper_market": {},
        "copper_constrained": {},
        "dcopt_curtailed": {}
    }

    result = {
        "copper_market": {},
        "copper_constrained": {},
        "dcopt_curtailed": {}
    }

    copper_market_output = {}
    copper_market_result = {}
    copper_constrained_output = {}
    copper_constrained_result = {}
    dcopf_curtailed_output = {}
    dcopf_curtailed_result = {}

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
        ComponentName.L_nonzero,
        ComponentName.bus_line_in,
        ComponentName.bus_line_out,
        ComponentName.line_busses,
        ComponentName.TRANSF,
        ComponentName.TRANSF_nonzero,
        ComponentName.bus_transformer_in,
        ComponentName.bus_transformer_out,
        ComponentName.transformer_busses,
        ComponentName.D,
        ComponentName.DNeg,
        ComponentName.demand_bus_mapping,
    ]
    build_sets(instance, case, setlist)

    #Define list of parameters for model and add to model
    paramlist = [
        ComponentName.line_max_continuous_P,
        ComponentName.line_susceptance,
        ComponentName.line_reactance,
        ComponentName.transformer_max_continuous_P,
        ComponentName.transformer_susceptance,
        ComponentName.transformer_reactance,
        ComponentName.PD,
        ComponentName.VOLL,
        ComponentName.PGmax,
        ComponentName.PGmin,
        ComponentName.PGMINGEN,
        ComponentName.c0,
        ComponentName.c1,
        ComponentName.bid,
        ComponentName.baseMVA,
    ]
    build_params(instance, case, paramlist)

    #Define list of variables for model and add to model
    varlist = [
        ComponentName.pG,
        ComponentName.pD,
        ComponentName.alpha,
        ComponentName.zeta_cg,
        ComponentName.zeta_wind,
        ComponentName.zeta_bin,
        ComponentName.prorata_minimum_zeta,
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

    #Define list of network constraints for model and add to model
    #NOTE: The constraints are copper constraints, so network constraints are disregarded
    constraintlist_network = [
        ComponentName.KCL_copperplate,
        ComponentName.demand_real_alpha_controlled,
        ComponentName.demand_alpha_max,
        ComponentName.demand_alpha_fixneg,
    ]
    build_constraints(instance, constraintlist_network)

    #List of constraints for generators
    #NOTE: All generators are forced to individual dispatch for initial copper run
    constraintlist_gen = [
        ComponentName.gen_forced_individual_realpower_max,
        ComponentName.gen_forced_individual_realpower_min
    ]
    build_constraints(instance, constraintlist_gen)

    #Define Objective Function
    instance.OBJ = Objective(rule = dcopf_marginal_cost_objective(instance), sense=minimize)

    #Define time dependent parameters
    ts_params = ['PD',
                'VOLL',
                'line_max_continuous_P',
                'transformer_max_continuous_P',
                'PGmin',
                'PGmax',
                'bid'] 

    for iteration in case.iterations:
        #Update parameters for current timestep
        add_iteration_params_to_instance(instance, case, ts_params, iteration)

        #~~~~~~~~~~~# COPPER PLATE MARKET MODEL SECTION #~~~~~~~~~~~#
        
        #Solve Copperplate Model Run
        copper_market_result[iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["copper_market"][iteration] = pyomo_io.InstanceCache(copper_market_result[iteration], data_to_cache)
        output["copper_market"][iteration].set(instance)
        output["copper_market"][iteration].var(instance)
        output["copper_market"][iteration].param(instance)
        output["copper_market"][iteration].obj_value(instance)
        

        #~~~~~~~~~~~# COPPER PLATE 'SECURE' MODEL SECTION #~~~~~~~~~~~#
        
        #Delete constraints for upper bound to generation (to be replaced below)
        remove_component_from_instance(instance, [ComponentName.gen_forced_individual_realpower_max])
        
        ##Update PGmax parameter for non-synchronouse generators to the market results
        for generator in instance.G_ns:
            instance.PGmax[generator] = instance.pG[generator].value

        #Introduce constraint to enforce MINGEN (superceeds PGMin) for all generators
        build_constraints(instance, [ComponentName.gen_mingen_LB])

        #Introduce constraint to enforce individual PGmax for synchronous generators
        build_constraints(instance, [ComponentName.gen_synchronous_individual_realpower_max])

        #Introduce constraint to dispatch down all non-synchronous generators pro-rata
        build_constraints(instance, [ComponentName.gen_post_mingen_redispatch_UB])

        #Solve Copperplate Model Run
        copper_constrained_result[iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["copper_constrained"][iteration] = pyomo_io.InstanceCache(copper_market_result[iteration], data_to_cache)
        output["copper_constrained"][iteration].set(instance)
        output["copper_constrained"][iteration].var(instance)
        output["copper_constrained"][iteration].param(instance)
        output["copper_constrained"][iteration].obj_value(instance)


        #~~~~~~~~~~~# COPPER PLATE TEST CODE RESET #~~~~~~~~~~~#
        #remove copper plate secure constraints
        remove_constraints_list = [ComponentName.gen_mingen_LB,
                                   ComponentName.gen_synchronous_individual_realpower_max,
                                   ComponentName.gen_post_mingen_redispatch_UB
                                   ]
        remove_component_from_instance(instance, remove_constraints_list)
        
        #Reapply the gen_forced_individual_realpower_max constraint
        build_constraints(instance, [ComponentName.gen_forced_individual_realpower_max])
    
    return output, result













def store(instance):
    #List of constraints for LIFO generators
    constraintlist_get_LIFO = [
        ComponentName.gen_LIFO_realpower_max,
        ComponentName.gen_LIFO_realpower_min,
        ComponentName.gen_LIFO_gamma,
        ComponentName.gen_LIFO_beta,
    ]

    #List of constraints for ProRata generators
    constraintlist_gen_prorata = [
        ComponentName.gen_prorata_realpower_max,
        ComponentName.gen_prorata_realpower_min,
        ComponentName.gen_prorata_realpower_min_zeta,
        ComponentName.gen_prorata_zeta_max,
        ComponentName.gen_prorata_zeta_min,
        ComponentName.gen_prorata_zeta_binary,
    ]

    #List of constraints for individually controlled generators
    constraintlist_gen_individual = [
        ComponentName.gen_individual_realpower_max,
        ComponentName.gen_individual_realpower_min,
    ]

    #List of constraints for uncontrollable generators
    constraintlist_gen_uncontrollable = [
        ComponentName.gen_uncontrollable_realpower_sp,
    ]

    #Define list of constraints to be aplied across generators, depending on types of export control defined, and add to model
    constraintlist_gen = []
    if [g for g in instance.G_LIFO] != []:
        constraintlist_gen += constraintlist_get_LIFO
    if [g for g in instance.G_prorata] != []:
        constraintlist_gen += constraintlist_gen_prorata
    if [g for g in instance.G_individual] != []:
        constraintlist_gen += constraintlist_gen_individual
    if [g for g in instance.G_uncontrollable] != []:
        constraintlist_gen += constraintlist_gen_uncontrollable
    build_constraints(instance, constraintlist_gen)