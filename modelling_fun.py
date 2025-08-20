from pyomo.environ import *
from pyomo_models.build.functions import (
    build_snapshot_dcopf_constraints,
    build_snapshot_dcopf_params,
    build_snapshot_dcopf_sets,
    build_snapshot_dcopf_variables,
    dcopf_marginal_cost_objective
)
import data_io.load_case as load_case
import pyomo_models.pyosolve as pyosolve


case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()

build_snapshot_dcopf_sets(instance, case)
build_snapshot_dcopf_params(instance, case)
build_snapshot_dcopf_variables(instance)
build_snapshot_dcopf_constraints(instance)
instance.OBJ = Objective(rule = dcopf_marginal_cost_objective(instance), sense=minimize)
result = pyosolve.solveinstance(instance, solver="appsi_highs")


...
# Further model processing would continue here
