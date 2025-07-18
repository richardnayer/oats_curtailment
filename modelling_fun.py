import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo.environ import *
from pyomo_models.sets_build.setsbuild import Sets_Dict

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()

for set_name, set_definition in Sets_Dict(case).sets.items():
    if set_definition['within'] is None:
        setattr(instance, set_name, Set(initialize = set_definition['initialize']()))
    else:
        setattr(instance, set_name, Set(set_definition['within'], initialize = set_definition['initialize']()))

# instance.PD = Param(instance.D,
#                     within=Reals,
#                     initialize = helpers.get_PerUnit_param_dict(case,
#                                                                 'demands',
#                                                                 'name',
#                                                                 'real',
#                                                                 case.baseMVA),
#                     mutable = True) #Real Power Demand
# instance.alpha = Var(instance.D, domain= NonNegativeReals)
# instance.pD = Var(instance.D, domain = NonNegativeReals)




# ...