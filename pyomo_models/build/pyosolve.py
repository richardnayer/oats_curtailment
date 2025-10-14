
from pyomo.environ import *
from pyomo.opt import SolverFactory
from pyomo.contrib import appsi
from pyomo.util.infeasible import log_infeasible_constraints

# Set up logger
import logging
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
handler = logging.StreamHandler()
formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
handler.setFormatter(formatter)
logger.addHandler(handler)

def solveinstance(instance, solver='appsi_highs'):
    '''
    This function solves the instance
    '''
    if solver == 'gurobi':
        options = {
            'OutputFlag': 0
        }

        with SolverFactory(
            "gurobi",
            solver_io = 'python',
            manage_env = True,
            options = options
            ) as opt:

            try:
                # opt.set_instance(instance)
                result = opt.solve(instance, tee = False, warmstart = True)
                return result
            except RuntimeError as exc:
                log_infeasible_constraints(instance, logger=logger, log_expression=False, log_variables=False)
                raise RuntimeError("Solver Error") from exc
    
    else:
        opt = SolverFactory(solver)
    
        try:
            result = opt.solve(instance, tee=False, warmstart=True)
            return result
        except RuntimeError as exc:
            log_infeasible_constraints(instance, logger=logger, log_expression=False, log_variables=False)
            raise RuntimeError("Solver Error") from exc

    
