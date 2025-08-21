
from pyomo.environ import *
from pyomo.opt import SolverFactory


def solveinstance(instance, solver='appsi_highs'):
    '''
    This function solves the instance
    '''
    opt = SolverFactory(solver)
    result = opt.solve(instance)
    return result
