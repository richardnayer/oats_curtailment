from pyomo.environ import *
from functools import reduce
from operator import mul
#--
import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo_models.build.definitions import Sets_Blocks, Constraint_Blocks, Params_Blocks, Variables_Blocks
from pyomo_models.build.functions import *
#--

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()


snapshot_DCOPF_sets = [
    "B",
    "b0",
    "G",
    "generator_mapping",
    "G_LIFO",
    "G_LIFO_pairs",
    "G_prorata",
    "G_prorata_map",
    "G_prorata_pairs",
    "G_individual",
    "G_uncontrollable",
    "prorata_groups",
    "L",
    "bus_line_in",
    "bus_line_out",
    "line_busses",
    "TRANSF",
    "bus_transformer_in",
    "bus_transformer_out",
    "transformer_busses",
    "D",
    "DNeg",
    "demand_bus_mapping"
]

snapshot_DCOPF_params = [
  "line_max_continuous_P",
  "line_susceptance",
  "line_reactance",
  "transformer_max_continuous_P",
  "transformer_susceptance",
  "transformer_reactance",
  "PD",
  "VOLL",
  "PGmax",
  "PGmin",
  "c0",
  "c1",
  "bid",
  "baseMVA"
]

snapshot_DCOPF_variables = [
  "pG",
  "pD",
  "alpha",
  "zeta_cg",
  "zeta_wind",
  "zeta_bin",
  "minimum_zeta",
  "gamma",
  "beta",
  "deltaL",
  "deltaLT",
  "delta",
  "pL",
  "pLT"
]

snapshot_DCOPF_network_constraints = [
  "KCL_networked_realpower_noshunt",
  "KVL_DCOPF_lines",
  "KVL_DCOPF_transformer",
  "demand_real_alpha_controlled",
  "demand_alpha_max",
  "demand_alpha_fixneg",
  "line_cont_realpower_max_pstve",
  "line_cont_realpower_max_ngtve",
  "volts_line_delta",
  "transf_continuous_real_max_pstve",
  "transf_continuous_real_max_ngtve",
  "volts_transformer_delta",
  "volts_reference_bus"
]

snapshot_DCOPF_LIFO_constraints = [
  "gen_PGmaxC_LIFO",
  "gen_PGminC_LIFO",
  "gen_gamma_LIFO",
  "gen_beta_LIFO",
]

snapshot_DCOPF_prorata_constraints = [
  "gen_prorata_realpower_max",
  "gen_prorata_realpower_min",
  "gen_prorata_realpower_min_zeta",
  "gen_prorata_zeta_max",
  "gen_prorata_zeta_min",
  "gen_prorata_zeta_binary",
]

snapshot_DCOPF_individual_constraints = [
  "gen_individual_realpower_max",
  "gen_individual_realpower_min",
]

snapshot_DCOPF_uncontrollable_constraints = [
  "gen_uncontrollable_realpower_sp",
]




add_sets_to_instance(instance, Sets_Blocks(case),snapshot_DCOPF_sets)

add_params_to_instance(instance, Params_Blocks(case), snapshot_DCOPF_params)

add_variables_to_instance(instance, Variables_Blocks(instance), snapshot_DCOPF_variables)

constraints_list = snapshot_DCOPF_network_constraints
if [g for g in instance.G_LIFO] != []:
    constraints_list += snapshot_DCOPF_LIFO_constraints
if [g for g in instance.G_prorata] != []:
    constraints_list += snapshot_DCOPF_prorata_constraints
if [g for g in instance.G_individual] != []:
    constraints_list += snapshot_DCOPF_individual_constraints
if [g for g in instance.G_uncontrollable] != []:
    constraints_list += snapshot_DCOPF_uncontrollable_constraints

add_constraints_to_instance(instance, Constraint_Blocks(instance), constraints_list)

...
