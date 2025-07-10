import data_io.load_case as load_case
import data_feed.pyomo.generators as gen_attr
from pyomo.environ import *

case = load_case.Case()
case.load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

map = gen_attr.individual_EER_policy(case)
print(map)