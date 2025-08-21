from pyomo_models.build.definitions import *
from pyomo_models.build.build_functions import *
from pyomo_models.build.names import *
import data_io.load_case as load_case
import pyomo_models.build.pyosolve as pyosolve


# --- Snapshot DCOPF component groups -------------------------------------

SETS = [
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

PARAMS = [
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

VARIABLES = [
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

NETWORK_CONSTRAINTS = [
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

LIFO_CONSTRAINTS = [
    ComponentName.gen_LIFO_realpower_max,
    ComponentName.gen_LIFO_realpower_min,
    ComponentName.gen_LIFO_gamma,
    ComponentName.gen_LIFO_beta,
]

PRORATA_CONSTRAINTS = [
    ComponentName.gen_prorata_realpower_max,
    ComponentName.gen_prorata_realpower_min,
    ComponentName.gen_prorata_realpower_min_zeta,
    ComponentName.gen_prorata_zeta_max,
    ComponentName.gen_prorata_zeta_min,
    ComponentName.gen_prorata_zeta_binary,
]

INDIVIDUAL_CONSTRAINTS = [
    ComponentName.gen_individual_realpower_max,
    ComponentName.gen_individual_realpower_min,
]

UNCONTROLLABLE_CONSTRAINTS = [
    ComponentName.gen_uncontrollable_realpower_sp,
]

def dcopf_snaphot():
    ...
    model = AbstractModel()
    instance = model.create_instance()
    



constraints_list = list(SNAPSHOT_DCOPF_NETWORK_CONSTRAINTS)
if [g for g in instance.G_LIFO] != []:
    constraints_list += SNAPSHOT_DCOPF_LIFO_CONSTRAINTS
if [g for g in instance.G_prorata] != []:
    constraints_list += SNAPSHOT_DCOPF_PRORATA_CONSTRAINTS
if [g for g in instance.G_individual] != []:
    constraints_list += SNAPSHOT_DCOPF_INDIVIDUAL_CONSTRAINTS
if [g for g in instance.G_uncontrollable] != []:
    constraints_list += SNAPSHOT_DCOPF_UNCONTROLLABLE_CONSTRAINTS

constraint_blocks = Constraint_Blocks(instance).blocks
constraint_defs = [
    SimpleNamespace(name=n, **asdict(constraint_blocks[n])) for n in constraints_list
]
add_constraints_to_instance(instance, constraint_defs)
