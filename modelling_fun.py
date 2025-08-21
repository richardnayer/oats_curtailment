from pyomo.environ import *
from pyomo_models.build.build_functions import (
    build_constraints,
    build_params,
    build_sets,
    build_variables,
)
from pyomo_models.build.obj_functions import dcopf_marginal_cost_objective
import data_io.load_case as load_case
import pyomo_models.build.pyosolve as pyosolve


case = load_case.Case()
case._load_excel_case("end-to-end-testcase.xlsx", timeseries = True)
case.summary()

model = AbstractModel()
instance = model.create_instance()

build_sets(instance, case)
build_params(instance, case)
build_variables(instance)
build_constraints(instance)
instance.OBJ = Objective(rule = dcopf_marginal_cost_objective(instance), sense=minimize)
result = pyosolve.solveinstance(instance, solver="appsi_highs")


...
# Further model processing would continue here
