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

param_list = helpers.get_param_dict(case, 'generators', 'name', 'PGUB', 'export_policy', '!=', 'Pro-Rata')

component_map = helpers.component_map_complete_dict(case, 'busses', 'name', 'generators', 'name', 'busname')

helpers._filtered_df(case, 'generators', 'export_policy', '!=', 'Pro-Rata')
helpers._filtered_df()
...
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