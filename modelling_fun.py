from dataclasses import asdict
from types import SimpleNamespace

from pyomo.environ import *
from functools import reduce
from operator import mul

import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo_models.build.definitions import (
    Sets_Blocks,
    Constraint_Blocks,
    Params_Blocks,
    Variables_Blocks,
)
from pyomo_models.build.functions import (
    add_constraints_to_instance,
    add_params_to_instance,
    add_sets_to_instance,
    add_variables_to_instance,
)
from pyomo_models.build.names import ComponentName

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()


snapshot_DCOPF_sets = [
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
    ComponentName.prorata_groups,
    ComponentName.L,
    ComponentName.bus_line_in,
    ComponentName.bus_line_out,
    ComponentName.line_busses,
    ComponentName.TRANSF,
    ComponentName.bus_transformer_in,
    ComponentName.bus_transformer_out,
    ComponentName.transformer_busses,
    ComponentName.D,
    ComponentName.DNeg,
    ComponentName.demand_bus_mapping,
]

snapshot_DCOPF_params = [
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
    ComponentName.c0,
    ComponentName.c1,
    ComponentName.bid,
    ComponentName.baseMVA,
]

snapshot_DCOPF_variables = [
    ComponentName.pG,
    ComponentName.pD,
    ComponentName.alpha,
    ComponentName.zeta_cg,
    ComponentName.zeta_wind,
    ComponentName.zeta_bin,
    ComponentName.minimum_zeta,
    ComponentName.gamma,
    ComponentName.beta,
    ComponentName.deltaL,
    ComponentName.deltaLT,
    ComponentName.delta,
    ComponentName.pL,
    ComponentName.pLT,
]

snapshot_DCOPF_network_constraints = [
    ComponentName.KCL_networked_realpower_noshunt,
    ComponentName.KVL_DCOPF_lines,
    ComponentName.KVL_DCOPF_transformer,
    ComponentName.demand_real_alpha_controlled,
    ComponentName.demand_alpha_max,
    ComponentName.demand_alpha_fixneg,
    ComponentName.line_cont_realpower_max_pstve,
    ComponentName.line_cont_realpower_max_ngtve,
    ComponentName.volts_line_delta,
    ComponentName.transf_continuous_real_max_pstve,
    ComponentName.transf_continuous_real_max_ngtve,
    ComponentName.volts_transformer_delta,
    ComponentName.volts_reference_bus,
]

snapshot_DCOPF_LIFO_constraints = [
    ComponentName.gen_LIFO_realpower_max,
    ComponentName.gen_LIFO_realpower_min,
    ComponentName.gen_LIFO_gamma,
    ComponentName.gen_LIFO_beta,
]

snapshot_DCOPF_prorata_constraints = [
    ComponentName.gen_prorata_realpower_max,
    ComponentName.gen_prorata_realpower_min,
    ComponentName.gen_prorata_realpower_min_zeta,
    ComponentName.gen_prorata_zeta_max,
    ComponentName.gen_prorata_zeta_min,
    ComponentName.gen_prorata_zeta_binary,
]

snapshot_DCOPF_individual_constraints = [
    ComponentName.gen_individual_realpower_max,
    ComponentName.gen_individual_realpower_min,
]

snapshot_DCOPF_uncontrollable_constraints = [
    ComponentName.gen_uncontrollable_realpower_sp,
]


set_blocks = Sets_Blocks(case).blocks
set_defs = [
    SimpleNamespace(name=n, **asdict(set_blocks[n])) for n in snapshot_DCOPF_sets
]
add_sets_to_instance(instance, set_defs)

param_blocks = Params_Blocks(case).blocks
param_defs = [
    SimpleNamespace(name=n, **asdict(param_blocks[n])) for n in snapshot_DCOPF_params
]
add_params_to_instance(instance, param_defs)

var_blocks = Variables_Blocks(instance).blocks
var_defs = [
    SimpleNamespace(name=n, **asdict(var_blocks[n])) for n in snapshot_DCOPF_variables
]
add_variables_to_instance(instance, var_defs)

constraints_list = list(snapshot_DCOPF_network_constraints)
if [g for g in instance.G_LIFO] != []:
    constraints_list += snapshot_DCOPF_LIFO_constraints
if [g for g in instance.G_prorata] != []:
    constraints_list += snapshot_DCOPF_prorata_constraints
if [g for g in instance.G_individual] != []:
    constraints_list += snapshot_DCOPF_individual_constraints
if [g for g in instance.G_uncontrollable] != []:
    constraints_list += snapshot_DCOPF_uncontrollable_constraints

constraint_blocks = Constraint_Blocks(instance).blocks
constraint_defs = [
    SimpleNamespace(name=n, **asdict(constraint_blocks[n])) for n in constraints_list
]
add_constraints_to_instance(instance, constraint_defs)

# Further model processing would continue here
