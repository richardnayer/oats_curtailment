"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of constraints for managing demands in OATS
'''


def real_alpha_controlled(model,demand):
    '''
    Constraints the realised real power demand (model output variable) to be equal to the input demand requirement, multiplied by the alpha factor (alpha is a real number between 0 and 1)
    Should be defined against the set of all demand (model.D), and alpha should be defined as a non-negative real number.
    '''
    return model.pD[demand] == model.alpha[demand]*model.PD[demand]

def alpha_max(model,demand):
    '''
    Constraints the demand controlling alpha factor to less than or equal to 1. \n
    Should be defined against the set of all demand (model.D), and alpha should be defined as a non-negative real number.
    '''
    return model.alpha[demand] <= 1

def alpha_fixneg(model,demand):
    '''
    Constraints the demand controlling alpha factor to equal to 1 where demand requirements are negative.\n
    Should be defined against the set of all negative demands (model.DNeg), and alpha should be defined as a non-negative real number.
    '''
    return model.alpha[demand] == 1
