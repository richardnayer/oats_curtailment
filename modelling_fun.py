from pyomo.environ import ConcreteModel
from pyomo_models.build.functions import (
    build_snapshot_dcopf_constraints,
    build_snapshot_dcopf_params,
    build_snapshot_dcopf_sets,
    build_snapshot_dcopf_variables,
)
import data_io.load_case as load_case


case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

instance = ConcreteModel()
build_snapshot_dcopf_sets(instance, case)
build_snapshot_dcopf_params(instance, case)
build_snapshot_dcopf_variables(instance)
build_snapshot_dcopf_constraints(instance)

# Further model processing would continue here
