from build.definitions import *
from build.build_functions import *
from build.names import *
import data_io.load_case as load_case
import build.pyosolve as pyosolve
import models.dcopf as dcopf_model

#Load Case


def run_model(testcase = "end-to-end-testcase.xlsx", solver = "appsi_highs", model="DCOPF"):

    #load case
    case = load_case.Case()
    case._load_excel_case("end-to-end-testcase.xlsx")
    case.summary()

    #run model
    match model:
        case 'DCOPF':

            result = dcopf_model.dcopf_snaphot(case)
            ...

    

