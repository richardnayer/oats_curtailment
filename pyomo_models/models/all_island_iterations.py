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
        "format": "iteration",
        "copper_market": {},
        "copper_constrained": {},
        "dcopf_curtailed": {}
    }

    result = {
        "format": "iteration",
        "copper_market": {},
        "copper_constrained": {},
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
        ComponentName.c0, #Defined each timestep
        ComponentName.c1,
        ComponentName.bid, #Defined each timestep
        ComponentName.baseMVA,
        ComponentName.SNSP_curtailment
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
    ts_params = [ComponentName.PD,
                ComponentName.VOLL,
                ComponentName.line_max_continuous_P,
                ComponentName.transformer_max_continuous_P,
                ComponentName.PGmin,
                ComponentName.PGmax,
                ComponentName.PGMINGEN,
                ComponentName.bid] 

    #Define time dependent sets
    ts_sets = [ComponentName.L_nonzero,
               ComponentName.TRANSF_nonzero] 

    for iteration in case.iterations:
        #Update parameters for current timestep
        add_iteration_params_to_instance(instance, case, ts_params, iteration)

        #Update any sets for current timestep
        add_iteration_sets_to_instance(instance, case, ts_sets, iteration)

        #~~~~~~~~~~~# COPPER PLATE MARKET MODEL SECTION #~~~~~~~~~~~#
        
        #Solve Copperplate Model Run
        result["copper_market"][iteration] = pyosolve.solveinstance(instance, solver = solver)

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
        #TODO - Currently this section only considers MINGEN, and not SNSP or other constraints.
        #     - Ideally it should also take into consideration all other secure constraints
        
        #Delete individual dispatch pGUB (upper bound power output (i.e. pGMax) constraints (to be replaced below)
        remove_component_from_instance(instance, [ComponentName.gen_forced_individual_realpower_max])
        
        ##Update PGmax parameter for non-synchronouse generators to the copper_market pG set-points
        for generator in instance.G_ns:
            instance.PGmax[generator] = instance.pG[generator].value

        #Introduce constraint to enforce MINGEN (pG >= pGMINGEN) (superceeds PGMin) for ALL generators
        #TODO - Replace with actual requirements from weekly constraints report
        build_constraints(instance, [ComponentName.gen_mingen_redispatch_LB])

       #Introduce constraint to re-dispatch down all non-synchronous generators pro-rata (pG = pGmax * mingen_zeta)
        #Required as mingen generators will have be redispatched up
        build_constraints(instance, [ComponentName.gen_mingen_redispatch_UB])

        #Introduce constraint to enforce individual (pG = pGmax * mingen_zeta) PGmax for synchronous generators
        build_constraints(instance, [ComponentName.gen_synchronous_individual_realpower_max])

 
        #Solve Copperplate Model Run
        result["copper_constrained"][iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["copper_constrained"][iteration] = pyomo_io.InstanceCache(result["copper_constrained"][iteration], data_to_cache)
        output["copper_constrained"][iteration].set(instance)
        output["copper_constrained"][iteration].var(instance)
        output["copper_constrained"][iteration].param(instance)
        output["copper_constrained"][iteration].obj_value(instance)


        #~~~~~~~~~~~# CREATE SNSP CONSTRAINT #~~~~~~~~~~~#
        #NOTE Previous version had SNSP coded in as a parameter update following the copper_redipsatch to account for mingen
        #NOTE It would be better to have this as a constraint in the previous section, however need to ensure linearity can be maintained

        #Calculation of % of non-synchronous generation (as percent of generation)
        synchronous_penetration = (sum(instance.pG[generator].value for generator in instance.G_ns)) / \
                                (sum(instance.pG[generator].value for generator in instance.G_ns) + sum(instance.pG[generator].value for generator in instance.G_s))
        
        #Calculation of curtailment factor
        if synchronous_penetration == 0:
            instance.SNSP_curtailment = 0
        else:
            instance.SNSP_curtailment = 1 - max(min(0.75/synchronous_penetration, 1), 0)

        #~~~~~~~~~~~# DCOPF MODEL SECTION #~~~~~~~~~~~#
        #Update non-synchronous generator maximum outputs based on curtailment requirements, but while respecting PGmin of generators.
        for generator in instance.G_ns:
            instance.PGmax[generator] = max(instance.pG[generator].value * (1 - instance.SNSP_curtailment.value), instance.PGmin[generator].value)

        #Remove constraints
        constraints_to_remove = [#Generation constraints used in previous models (superceeded by updated PGmax)
                                 ComponentName.gen_forced_individual_realpower_min,
                                 ComponentName.gen_synchronous_individual_realpower_max,
                                 ComponentName.gen_mingen_redispatch_UB,
                                 
                                 #Remove Copperplate KCL Constraint
                                 ComponentName.KCL_copperplate
                                 ]
        remove_component_from_instance(instance, constraints_to_remove)

        #Add in network constraints
        build_constraints(instance, [#Kirchoffs Current Law
                                               ComponentName.KCL_networked_realpower_noshunt,
                                               
                                               #Kirchoffs Voltage Law
                                               ComponentName.KVL_DCOPF_lines,
                                               ComponentName.KVL_DCOPF_transformer,
                                               
                                               #Power Line Operational Limits
                                               ComponentName.line_cont_realpower_max_ngtve,
                                               ComponentName.line_cont_realpower_max_pstve,
                                               ComponentName.volts_line_delta,

                                               #Transformer Line Operational Limits
                                               ComponentName.transf_continuous_real_max_ngtve,
                                               ComponentName.transf_continuous_real_max_pstve,
                                               ComponentName.volts_transformer_delta,

                                               #Reference bus voltage
                                               ComponentName.volts_reference_bus
                                               ])
        
        #Add in generator constraints
        gen_constraints_list = []
        #LIFO Generator Constraints
        if [g for g in instance.G_LIFO] != []:
            gen_constraints_list += [ComponentName.gen_LIFO_realpower_max,
                                    ComponentName.gen_LIFO_realpower_min,
                                    ComponentName.gen_LIFO_gamma,
                                    ComponentName.gen_LIFO_beta,
                                   ]
        #Prorata Generator Constraints
        if [g for g in instance.G_prorata] != []:
            gen_constraints_list += [ComponentName.gen_prorata_realpower_max,
                                    ComponentName.gen_prorata_realpower_min,
                                    ComponentName.gen_prorata_realpower_min_zeta,
                                    ComponentName.gen_prorata_zeta_max,
                                    ComponentName.gen_prorata_zeta_min,
                                    ComponentName.gen_prorata_zeta_binary,
                                    ]
        #Individually Controlled Generator Constraints
        if [g for g in instance.G_individual] != []:
            gen_constraints_list += [ComponentName.gen_individual_realpower_max,
                                    ComponentName.gen_individual_realpower_min,
                                   ]
        if [g for g in instance.G_uncontrollable] != []:
            gen_constraints_list += [ComponentName.gen_uncontrollable_realpower_sp]

        build_constraints(instance, gen_constraints_list)


        #Solve DCOPF Model Run
        result["dcopf_curtailed"][iteration] = pyosolve.solveinstance(instance, solver = solver)

        #Define Data to Save
        data_to_cache = {"Var": [], 
                    "Param" : [],
                    "Set" : []}
        
        #Cache Data
        output["dcopf_curtailed"][iteration] = pyomo_io.InstanceCache(result["copper_constrained"][iteration], data_to_cache)
        output["dcopf_curtailed"][iteration].set(instance)
        output["dcopf_curtailed"][iteration].var(instance)
        output["dcopf_curtailed"][iteration].param(instance)
        output["dcopf_curtailed"][iteration].obj_value(instance)

        #~~~~~~~~~~~# COPPER PLATE TEST CODE RESET #~~~~~~~~~~~#
        #remove copper plate secure constraints
        remove_constraints_list = [#Kirchoffs Current Law
                                   ComponentName.KCL_networked_realpower_noshunt,
                                   #Kirchoffs Voltage Law
                                   ComponentName.KVL_DCOPF_lines,
                                   ComponentName.KVL_DCOPF_transformer,
                                   #Power Line Operational Limits
                                   ComponentName.line_cont_realpower_max_ngtve,
                                   ComponentName.line_cont_realpower_max_pstve,
                                   ComponentName.volts_line_delta,
                                   #Transformer Line Operational Limits
                                   ComponentName.transf_continuous_real_max_ngtve,
                                   ComponentName.transf_continuous_real_max_pstve,
                                   ComponentName.volts_transformer_delta,
                                   #Reference bus voltage
                                   ComponentName.volts_reference_bus,
                                   #MINGEN Generation Constraints
                                   ComponentName.gen_mingen_redispatch_LB,
                                   #LIFO Generation Constraints
                                   ComponentName.gen_LIFO_realpower_max,
                                   ComponentName.gen_LIFO_realpower_min,
                                   ComponentName.gen_LIFO_gamma,
                                   ComponentName.gen_LIFO_beta,
                                   #Prorata Generation Constraints
                                   ComponentName.gen_prorata_realpower_max,
                                   ComponentName.gen_prorata_realpower_min,
                                   ComponentName.gen_prorata_realpower_min_zeta,
                                   ComponentName.gen_prorata_zeta_max,
                                   ComponentName.gen_prorata_zeta_min,
                                   ComponentName.gen_prorata_zeta_binary,
                                   #Individual Generation Constraints
                                   ComponentName.gen_individual_realpower_max,
                                   ComponentName.gen_individual_realpower_min,
                                   #Uncontrollable Generation Constraints
                                   ComponentName.gen_uncontrollable_realpower_sp
                                   ]
        remove_component_from_instance(instance, remove_constraints_list, skip_missing = True)
        
        #Reapply the timeseries constraints
        build_constraints(instance, [ComponentName.gen_forced_individual_realpower_max,
                                     ComponentName.gen_forced_individual_realpower_min,
                                     ComponentName.KCL_copperplate])

    return output, result







