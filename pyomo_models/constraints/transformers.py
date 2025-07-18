"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of constraints over transformers for OATS
'''

def continuous_real_max_pstve(model,transformer):
    '''
    Require transformer power flow in positive direction to be less than rated continuous power flow. \n
    Should be defined over all transformers (model.TRANSF) \n
    pLT[transformer] <= transformer_max_continous_P[transformer] \n
    '''
    return model.pLT[transformer] <= model.transformer_max_continuous_P[transformer]


def continuous_real_max_ngtve(model,transformer):
    '''
    Require transformer real power flow in reverse direction to be less than rated continuous power flow. \n
    Should be defined over all transformers (model.TRANSF) \n
    pLT[transformer] >= -transformer_max_continous_P[transformer] \n

    '''
    return model.pLT[transformer] >= -model.transformer_max_continuous_P[transformer]

