import data_io.load_case as load_case
import data_feed.pyomo.generators as gen_attr
import data_feed.pyomo.lines as line_attr
import data_feed.pyomo.helpers as helpers
import data_feed.pyomo.demands as demands
import data_feed.pyomo.generators as generators
from pyomo.environ import *

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

map = line_attr.bus_line_in(case)
print(map)

gen = helpers.get_param_list(case, 'generators', 'export_policy', '=', 'Individual', 'name')
print(gen)

what = helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups')
....
# model = AbstractModel()
# instance = model.create_instance()

# instance.D = Set(initialize = demands.identifiers(case))
# instance.PD = Param(instance.D,
#                     within=Reals,
#                     initialize = helpers.get_PerUnit_param_dict(case,
#                                                                 'demands',
#                                                                 'name',
#                                                                 'real',
#                                                                 case.baseMVA),
#                     mutable = True) #Real Power Demand
# ...