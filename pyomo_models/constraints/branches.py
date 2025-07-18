"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of constraints over power lines for OATS
'''

def cont_realpower_max_pstve(model,line):
    '''
    Constrains positive real power flow over each power line to less than or equal to the continuous rated maximum of the line. \n
    Should be defined against the set of all power lines (model.L)
    '''
    return model.pL[line] <= model.line_max_continuous_P[line]


def cont_realpower_max_ngtve(model,line):
    '''
    Constrains reverse real power flow over each power line to less than or equal to the continuous rated maximum of the line. \n
    Should be defined against the set of all power lines (model.L)
    '''
    return model.pL[line] >= -model.line_max_continuous_P[line]
