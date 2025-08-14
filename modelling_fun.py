from pyomo.environ import *
from functools import reduce
from operator import mul
#--
import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo_models.build.definitions import Sets_Blocks, Constraint_Blocks, Params_Blocks, Variables_Blocks
from pyomo_models.build.functions import *
#--

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()

testydict = {'B': {
                'type': 'flat',
                'index': None,
                'within': None,
                'dimen': 1,
                'initialize': lambda: helpers.get_param_list(case, 'busses', 'name'),
            },
}

add_sets_to_instance(instance, Sets_Blocks(case))

add_params_to_instance(instance, Params_Blocks(case, instance))

add_variables_to_instance(instance, Variables_Blocks(instance))

add_constraints_to_instance(instance, Constraint_Blocks(instance))

...
