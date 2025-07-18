import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo.environ import *
from pyomo_models.sets_build.setsbuild import Sets_Dict

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()

from pyomo.environ import Set

def add_sets_to_instance(instance, sets_dict_obj):
    for set_name, set_def in sets_dict_obj.sets.items():
        set_type = set_def.get('type', 'flat')
        dimen = set_def.get('dimen', 1)
        within = set_def.get('within', None)
        initialize = set_def.get('initialize')()

        print(set_name, set_type, dimen, within, initialize)

        #TODO - Buid iterative addition of sets into the instance.
        
        # if set_type == 'flat':
        #     instance.add_component(
        #         set_name,
        #         Set(
        #             dimen=dimen,
        #             within=within if isinstance(within, (tuple, Set, str)) else Set(),  # handle tuple or Set or None
        #             initialize=initialize,
        #             ordered=False,
        #             validate=None,
        #         )
        #     )
        # elif set_type == 'indexed':
        #     # assume initialize returns a dict of lists, e.g., {index: [items]}
        #     instance.add_component(
        #         set_name,
        #         Set(
        #             dimen=dimen,
        #             within=within if isinstance(within, (tuple, Set, str)) else Set(),
        #             initialize=initialize,
        #             ordered=False,
        #             validate=None,
        #         )
        #     )
        # else:
        #     raise ValueError(f"Unsupported set type: {set_type} for set {set_name}")

add_sets_to_instance(instance, Sets_Dict(case))

...
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