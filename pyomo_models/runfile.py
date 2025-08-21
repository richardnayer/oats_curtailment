#Set Path
from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

#Import Modules
import data_io.load_case as load_case
import pyomo_models.models.dcopf as dcopf_model


def run_model(testcase = "end-to-end-testcase.xlsx", solver = "appsi_highs", model="DCOPF"):

    #load case
    case = load_case.Case()
    case._load_excel_case("end-to-end-testcase.xlsx")
    case.summary()

    #run model
    match model:
        case 'DCOPF':

            output, result = dcopf_model.dcopf_snaphot(case)
            return output, result

output, result = run_model()
...

