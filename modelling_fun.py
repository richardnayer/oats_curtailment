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

comma_param_to_dict = helpers.comma_param_to_dict(case, 'generators', 'name', 'prorata_groups', 'export_policy', '!=', 'Pro-Rata')

ordered_groupwise_combinations = helpers.get_ordered_groupwise_combinations(case, 'generators', 'name', 'lifo_group', 'lifo_position')

get_zipped_params = helpers.get_zipped_param_list(case, 'branches', 'name', ['to_busname', 'from_busname'])

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