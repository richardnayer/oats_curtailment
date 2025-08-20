from pyomo_models.build.functions import build_snapshot_dcopf_instance
import data_io.load_case as load_case


case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

instance = build_snapshot_dcopf_instance(case)

# Further model processing would continue here
