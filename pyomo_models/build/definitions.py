from dataclasses import dataclass
from typing import Any, Callable, Dict, Optional, Tuple, Union

import data_io.helpers as helpers
from pyomo.environ import *
from .names import ComponentName


@dataclass(slots=True)
class SetDef:
    index: Optional[Union[ComponentName, Tuple[ComponentName, ...], Any]] = None
    within: Optional[Union[ComponentName, Tuple[ComponentName, ...], Any]] = None
    initialize: Optional[Callable] = None
    dimen: int = 1
    ordered: bool = False


@dataclass(slots=True)
class VarDef:
    index: Optional[Union[ComponentName, Tuple[ComponentName, ...], Any]] = None
    domain: Any = None
    bounds: Optional[Tuple[Any, Any]] = None
    initialize: Optional[Callable] = None


@dataclass(slots=True)
class ParamDef:
    index: Optional[Union[ComponentName, Tuple[ComponentName, ...], Any]] = None
    within: Any = None
    initialize: Optional[Callable] = None
    mutable: bool = False


@dataclass(slots=True)
class ConstraintDef:
    rule: Callable
    index: Optional[Union[ComponentName, Tuple[ComponentName, ...], Any]] = None


class Sets_Blocks:
    def __init__(self, case: Any):
        self.blocks: Dict[ComponentName, SetDef] = {
            # --- SETS FOR BUSSES ---
            ComponentName.B: SetDef(
                initialize=lambda: helpers.get_param_list(case, "busses", "name"),
            ),
            ComponentName.b0: SetDef(
                within=ComponentName.B,
                initialize=lambda: helpers.get_param_list(
                    case, "busses", "name", "type", "=", 3
                ),
            ),

            # --- SETS FOR GENERATORS ---
            ComponentName.G: SetDef(
                initialize=lambda: helpers.get_param_list(
                    case, "generators", "name"
                ),
            ),
            ComponentName.generator_mapping: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "generators",
                    "name",
                    "busname",
                ),
            ),
            ComponentName.G_LIFO: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "export_policy",
                    "=",
                    "LIFO",
                ),
            ),
            ComponentName.G_LIFO_pairs: SetDef(
                within=(ComponentName.G_LIFO, ComponentName.G_LIFO),
                initialize=lambda: helpers.get_ordered_groupwise_combinations(
                    case, "generators", "name", "lifo_group", "lifo_position"
                ),
                dimen=2,
                ordered=True,
            ),
            ComponentName.G_prorata: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "export_policy",
                    "=",
                    "Pro-Rata",
                ),
            ),
            ComponentName.G_prorata_map: SetDef(
                index=ComponentName.G_prorata,
                initialize=lambda: helpers.comma_param_to_dict(
                    case,
                    "generators",
                    "name",
                    "prorata_groups",
                    "export_policy",
                    "=",
                    "Pro-Rata",
                ),
            ),
            ComponentName.G_prorata_pairs: SetDef(
                initialize=lambda: helpers.get_paired_params_list(
                    case,
                    "generators",
                    "name",
                    "prorata_groups",
                    True,
                    "export_policy",
                    "=",
                    "Pro-Rata",
                ),
                dimen=2,
            ),
            ComponentName.G_individual: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "export_policy",
                    "=",
                    "Individual",
                ),
            ),
            ComponentName.G_uncontrollable: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "export_policy",
                    "=",
                    "Uncontrollable",
                ),
            ),
            ComponentName.G_s: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "synchronous",
                    "=",
                    "Yes",
                ),
            ),
            ComponentName.G_ns: SetDef(
                within=ComponentName.G,
                initialize=lambda: helpers.get_param_list(
                    case,
                    "generators",
                    "name",
                    "synchronous",
                    "=",
                    "No",
                ),
            ),
            ComponentName.prorata_groups: SetDef(
                initialize=lambda: helpers.comma_param_to_list(
                    case,
                    "generators",
                    "prorata_groups",
                    "export_policy",
                    "=",
                    "Pro-Rata",
                ),
            ),

            # --- SETS FOR POWER LINES ---
            ComponentName.L: SetDef(
                initialize=lambda: helpers.get_param_list(
                    case, "branches", "name"
                ),
            ),
            ComponentName.bus_line_in: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "branches",
                    "name",
                    "to_busname",
                ),
            ),
            ComponentName.bus_line_out: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "branches",
                    "name",
                    "from_busname",
                ),
            ),
            ComponentName.line_busses: SetDef(
                index=ComponentName.L,
                initialize=lambda: helpers.get_zipped_param_list(
                    case,
                    "branches",
                    "name",
                    ["from_busname", "to_busname"],
                ),
                ordered=True,
            ),

            # --- SETS FOR TRANSFORMERS ---
            ComponentName.TRANSF: SetDef(
                initialize=lambda: helpers.get_param_list(
                    case, "transformers", "name"
                ),
            ),
            ComponentName.bus_transformer_in: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "transformers",
                    "name",
                    "to_busname",
                ),
            ),
            ComponentName.bus_transformer_out: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "transformers",
                    "name",
                    "from_busname",
                ),
            ),
            ComponentName.transformer_busses: SetDef(
                index=ComponentName.TRANSF,
                initialize=lambda: helpers.get_zipped_param_list(
                    case,
                    "transformers",
                    "name",
                    ["from_busname", "to_busname"],
                ),
                ordered=True,
            ),

            # --- SETS FOR DEMANDS ---
            ComponentName.D: SetDef(
                initialize=lambda: helpers.get_param_list(
                    case, "demands", "name"
                ),
            ),
            ComponentName.DNeg: SetDef(
                within=ComponentName.D,
                initialize=lambda: helpers.get_param_list(
                    case, "demands", "name", "real", "<", 0
                ),
            ),
            ComponentName.demand_bus_mapping: SetDef(
                index=ComponentName.B,
                initialize=lambda: helpers.component_map_complete_dict(
                    case,
                    "busses",
                    "name",
                    "demands",
                    "name",
                    "busname",
                ),
            ),
        }


class Params_Blocks:
    def __init__(self, case: Any):
        self.blocks: Dict[ComponentName, ParamDef] = {
            # LINE CONSTRAINTS
            ComponentName.line_max_continuous_P: ParamDef(
                index=ComponentName.L,
                within=NonNegativeReals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "branches", "name", "ContinousRating", case.baseMVA
                ),
                mutable=True,
            ),
            ComponentName.line_susceptance: ParamDef(
                index=ComponentName.L,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "branches", "name", "b"
                ),
                mutable=False,
            ),
            ComponentName.line_reactance: ParamDef(
                index=ComponentName.L,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "branches", "name", "x"
                ),
                mutable=False,
            ),

            # TRANSFORMER PARAMETERS
            ComponentName.transformer_max_continuous_P: ParamDef(
                index=ComponentName.TRANSF,
                within=NonNegativeReals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "transformers", "name", "ContinousRating", case.baseMVA
                ),
                mutable=True,
            ),
            ComponentName.transformer_susceptance: ParamDef(
                index=ComponentName.TRANSF,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "transformers", "name", "b"
                ),
                mutable=False,
            ),
            ComponentName.transformer_reactance: ParamDef(
                index=ComponentName.TRANSF,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "transformers", "name", "x"
                ),
                mutable=False,
            ),

            # DEMAND PARAMETERS
            ComponentName.PD: ParamDef(
                index=ComponentName.D,
                within=NonNegativeReals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "demands", "name", "real", case.baseMVA
                ),
                mutable=True,
            ),
            ComponentName.VOLL: ParamDef(
                index=ComponentName.D,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "demands", "name", "VOLL"
                ),
                mutable=True,
            ),

            # GENERATOR POWER PARAMETERS
            ComponentName.PGmax: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "generators", "name", "PGUB", case.baseMVA
                ),
                mutable=True,
            ),
            ComponentName.PGmin: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "generators", "name", "PGLB", case.baseMVA
                ),
                mutable=True,
            ),
            ComponentName.PGMINGEN: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_PerUnit_param_dict(
                    case, "generators", "name", "PGMINGEN", case.baseMVA
                ),
                mutable=True,
            ),

            # GENERATOR COST PARAMETERS
            ComponentName.c0: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "generators", "name", "costc0"
                ),
                mutable=False,
            ),
            ComponentName.c1: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "generators", "name", "costc1"
                ),
                mutable=False,
            ),
            ComponentName.bid: ParamDef(
                index=ComponentName.G,
                within=Reals,
                initialize=lambda: helpers.get_param_dict(
                    case, "generators", "name", "bid"
                ),
                mutable=True,
            ),

            # BASE MVA PARAMETER
            ComponentName.baseMVA: ParamDef(
                index=ComponentName.G,
                within=NonNegativeReals,
                initialize=lambda: case.baseMVA,
                mutable=False,
            ),
        }


class Variables_Blocks:
    def __init__(self, instance: Any):
        self.blocks: Dict[ComponentName, VarDef] = {
            #CONTROL VARIABLES
            ComponentName.pG: VarDef(
                index=ComponentName.G,
                domain=Reals,
            ),
            ComponentName.pD: VarDef(
                index=ComponentName.D,
                domain=Reals,
            ),
            ComponentName.alpha: VarDef(
                index=ComponentName.D,
                domain=NonNegativeReals,
            ),

            #Pro-Rata Curtailment Control Variables
            ComponentName.zeta_cg: VarDef(
                index=ComponentName.prorata_groups,
                domain=NonNegativeReals,
                bounds=(0, 1),
            ),
            ComponentName.zeta_wind: VarDef(
                index=ComponentName.G_prorata,
                domain=NonNegativeReals,
                bounds=(0, 1),
            ),
            ComponentName.zeta_bin: VarDef(
                index=ComponentName.G_prorata_pairs,
                domain=Binary,
            ),
            ComponentName.minimum_zeta: VarDef(
                index=ComponentName.G_prorata_pairs,
                domain=NonNegativeReals,
                bounds=(0, 1),
            ),

            #LIFO Curtailment Control Variables
            ComponentName.gamma: VarDef(
                index=ComponentName.G_LIFO,
                domain=Binary,
            ),
            ComponentName.beta: VarDef(
                index=ComponentName.G_LIFO,
                domain=NonNegativeReals,
                bounds=(0, 1),
            ),

            #STATE VARIABLES
            ComponentName.deltaL: VarDef(
                index=ComponentName.L,
                domain=Reals,
            ),
            ComponentName.deltaLT: VarDef(
                index=ComponentName.TRANSF,
                domain=Reals,
            ),
            ComponentName.delta: VarDef(
                index=ComponentName.B,
                domain=Reals,
                initialize=0,
            ),
            ComponentName.pL: VarDef(
                index=ComponentName.L,
                domain=Reals,
            ),
            ComponentName.pLT: VarDef(
                index=ComponentName.TRANSF,
                domain=Reals,
            ),
        }


class Constraint_Blocks:
    def __init__(self, instance: Any):
        self.blocks: Dict[ComponentName, ConstraintDef] = {
            # --- POWER LINE CONSTRAINTS ---
            ComponentName.line_cont_realpower_max_pstve: ConstraintDef(
                index=ComponentName.L,
                rule=lambda inst, line: inst.pL[line]
                <= inst.line_max_continuous_P[line],
            ),
            ComponentName.line_cont_realpower_max_ngtve: ConstraintDef(
                index=ComponentName.L,
                rule=lambda inst, line: inst.pL[line]
                >= -inst.line_max_continuous_P[line],
            ),

            # --- DEMAND CONSTRAINTS ---
            ComponentName.demand_real_alpha_controlled: ConstraintDef(
                index=ComponentName.D,
                rule=lambda inst, demand: inst.pD[demand]
                == inst.alpha[demand] * inst.PD[demand],
            ),
            ComponentName.demand_alpha_max: ConstraintDef(
                index=ComponentName.D,
                rule=lambda inst, demand: inst.alpha[demand] <= 1,
            ),
            ComponentName.demand_alpha_fixneg: ConstraintDef(
                index=ComponentName.DNeg,
                rule=lambda inst, demand: inst.alpha[demand] == 1,
            ),

            #--- GENERATION CONSTRAINTS ---
            # --- Uncontrollable EER Policy ---
            ComponentName.gen_uncontrollable_realpower_sp: ConstraintDef(
                index=ComponentName.G_uncontrollable,
                rule=lambda inst, generator: inst.pG[generator]
                == inst.PG[generator],
            ),

            # --- Mingen Requirements ---
            ComponentName.gen_mingen_LB: ConstraintDef(
                index=ComponentName.G,
                rule=lambda inst, generator: inst.pG[generator]
                >= inst.PGMINGEN[generator],
            ),

            # --- Individual EER Policy ---
            ComponentName.gen_individual_realpower_max: ConstraintDef(
                index=ComponentName.G_individual,
                rule=lambda inst, generator: inst.pG[generator]
                <= inst.PGmax[generator],
            ),
            ComponentName.gen_individual_realpower_min: ConstraintDef(
                index=ComponentName.G_individual,
                rule=lambda inst, generator: inst.pG[generator]
                >= inst.PGmin[generator],
            ),

            # --- Pro-Rata ERG Curtailment ---
            ComponentName.gen_prorata_realpower_max: ConstraintDef(
                index=ComponentName.G_prorata,
                rule=lambda inst, generator: inst.pG[generator]
                <= inst.PGmax[generator] * inst.zeta_wind[generator],
            ),
            ComponentName.gen_prorata_realpower_min: ConstraintDef(
                index=ComponentName.G_prorata,
                rule=lambda inst, generator: inst.pG[generator]
                >= inst.PGmin[generator],
            ),
            ComponentName.gen_prorata_realpower_min_zeta: ConstraintDef(
                index=ComponentName.G_prorata,
                rule=lambda inst, generator: inst.pG[generator]
                >= inst.PGmax[generator] * inst.zeta_wind[generator],
            ),
            ComponentName.gen_prorata_zeta_max: ConstraintDef(
                index=ComponentName.G_prorata_pairs,
                rule=lambda inst, generator, cg: inst.zeta_wind[generator]
                <= inst.zeta_cg[cg],
            ),
            ComponentName.gen_prorata_zeta_min: ConstraintDef(
                index=ComponentName.G_prorata_pairs,
                rule=lambda inst, generator, cg: inst.zeta_wind[generator]
                >= inst.zeta_cg[cg] - (1 - 0) * (1 - inst.zeta_bin[(generator, cg)]),
            ),
            ComponentName.gen_prorata_zeta_binary: ConstraintDef(
                index=ComponentName.G_prorata,
                rule=lambda inst, generator: sum(
                    inst.zeta_bin[(generator, cg)]
                    for cg in inst.G_prorata_map[generator]
                )
                == 1,
            ),

            # --- Last-In-First-Out (LIFT) ERG Curtailment ---
            ComponentName.gen_LIFO_realpower_max: ConstraintDef(
                index=ComponentName.G_LIFO,
                rule=lambda inst, generator: inst.pG[generator]
                <= (1 - inst.beta[generator]) * inst.PGmax[generator],
            ),
            ComponentName.gen_LIFO_realpower_min: ConstraintDef(
                index=ComponentName.G_LIFO,
                rule=lambda inst, generator: inst.pG[generator]
                >= (1 - inst.gamma[generator]) * inst.PGmax[generator],
            ),
            ComponentName.gen_LIFO_gamma: ConstraintDef(
                index=ComponentName.G_LIFO_pairs,
                rule=lambda inst, gen1, gen2: inst.gamma[gen1]
                <= inst.gamma[gen2],
            ),
            ComponentName.gen_LIFO_beta: ConstraintDef(
                index=ComponentName.G_LIFO_pairs,
                rule=lambda inst, gen1, gen2: inst.gamma[gen1]
                <= inst.beta[gen2],
            ),

            # --- KCL CONSTRAINTS ---
            ComponentName.KCL_networked_realpower_noshunt: ConstraintDef(
                index=ComponentName.B,
                rule=lambda inst, bus: + sum(
                    inst.pG[generator]
                    for generator in inst.generator_mapping[bus]
                )
                - sum(inst.pL[line] for line in inst.bus_line_out[bus])
                + sum(inst.pL[line] for line in inst.bus_line_in[bus])
                - sum(
                    inst.pLT[transformer]
                    for transformer in inst.bus_transformer_out[bus]
                )
                + sum(
                    inst.pLT[transformer]
                    for transformer in inst.bus_transformer_in[bus]
                )
                == sum(
                    inst.pD[demand]
                    for demand in inst.demand_bus_mapping[bus]
                ),
            ),

            # --- KVL CONSTRAINTS---
            ComponentName.KVL_DCOPF_lines: ConstraintDef(
                index=ComponentName.L,
                rule=lambda inst, line: inst.pL[line]
                == (1 / inst.line_reactance[line]) * inst.deltaL[line],
            ),
            ComponentName.KVL_DCOPF_transformer: ConstraintDef(
                index=ComponentName.TRANSF,
                rule=lambda inst, transformer: inst.pLT[transformer]
                == (1 / inst.transformer_reactance[transformer])
                * inst.deltaLT[transformer],
            ),

            # --- TRANSFORMER CONSTRAINTS---
            ComponentName.transf_continuous_real_max_pstve: ConstraintDef(
                index=ComponentName.TRANSF,
                rule=lambda inst, transformer: inst.pLT[transformer]
                <= inst.transformer_max_continuous_P[transformer],
            ),
            ComponentName.transf_continuous_real_max_ngtve: ConstraintDef(
                index=ComponentName.TRANSF,
                rule=lambda inst, transformer: inst.pLT[transformer]
                >= -inst.transformer_max_continuous_P[transformer],
            ),

            # --- VOLTAGE CONSTRAINTS---
            ComponentName.volts_line_delta: ConstraintDef(
                index=ComponentName.L,
                rule=lambda inst, line: inst.deltaL[line]
                == + inst.delta[inst.line_busses[line].at(1)]
                - inst.delta[inst.line_busses[line].at(2)],
            ),
            ComponentName.volts_transformer_delta: ConstraintDef(
                index=ComponentName.TRANSF,
                rule=lambda inst, transformer: inst.deltaLT[transformer]
                == + inst.delta[
                    inst.transformer_busses[transformer].at(1)
                ]
                - inst.delta[
                    inst.transformer_busses[transformer].at(2)
                ],
            ),
            ComponentName.volts_reference_bus: ConstraintDef(
                index=ComponentName.B,
                rule=lambda inst, bus: inst.delta[bus] == 0,
            ),
        }


