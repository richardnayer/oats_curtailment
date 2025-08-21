from pyomo_models.build.definitions import *
from pyomo_models.build.build_functions import *
from pyomo_models.build.names import *
import data_io.load_case as load_case
import pyomo_models.build.pyosolve as pyosolve
import pyomo_models.models.dcopf as dcopf_model

#Load Case


def run_model(testcase = "end-to-end-testcase.xlsx", solver = "appsi_highs", model="DCOPF"):

    #load case
    case = load_case.Case()
    case._load_excel_snapshot_case("end-to-end-testcase.xlsx")
    case.summary()

    #run model
    match model:
        case 'DCOPF':
            build_sets()
            dcopf_model.SNAPSHOT_DCOPF_INDIVIDUAL_CONSTRAINTS

    

