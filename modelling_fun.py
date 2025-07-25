from pyomo.environ import *
from functools import reduce
from operator import mul
#--
import data_io.load_case as load_case
import data_io.helpers as helpers
from pyomo_models.build.definitions import Sets_Blocks
from pyomo_models.build.functions import *
#--

case = load_case.Case()
case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
case.summary()

model = AbstractModel()
instance = model.create_instance()


add_sets_to_instance(instance, Sets_Blocks(case))

...
