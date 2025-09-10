#Set Path
from pathlib import Path
import sys
path_root = Path(__file__).parents[1]
sys.path.append(str(path_root))

#Import Modules
import data_io.load_case as load_case
import pyomo_models.models.dcopf_snapshot as dcopf_snapshot
import pyomo_models.models.dcopf_iterations as dcopf_iterations
import pyomo_models.models.all_island_iterations_v2 as all_island_iterations

# Set up logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def run_model(testcase = "end-to-end-testcase.xlsx", solver = "appsi_highs", model="DCOPF"):


    match model:
        case 'DCOPF Snapshot':
            #load case
            case = load_case.Case()
            case._load_excel_case("end-to-end-testcase.xlsx")
            case.summary()
            #run model
            output, result = dcopf_snapshot.model(case, solver)
            return output, result
        
        case 'DCOPF Timeseries':
            #load case
            case = load_case.Case()
            case._load_excel_case("end-to-end-testcase.xlsx", iterative = True)
            case.summary()
            output, result = dcopf_iterations.model(case, solver)
            return output, result
        
        case 'All Island Timeseries':
            #load case
            case = load_case.Case()
            case._load_excel_case("end-to-end-testcase.xlsx", iterative = True)
            case.summary()
            output, result = all_island_iterations.model(case, solver)
            return output, result

        case _:
            KeyError(f"The model selected ({model}) has not been defined")
        

output, result = run_model(model = "All Island Timeseries")
...

