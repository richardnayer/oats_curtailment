"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of Kirchoff's Voltage Law (KVL) constraints for use within OATS.
'''

#-------------------------------------------------------------------------#
#                      Kirchoff's Voltage Law
#-------------------------------------------------------------------------#


def DCOPF_lines(model,line):
    '''
    Kirchoff's Voltage Law (KVL) defined for each power line for the DC simplifcation of AC system \n
    Should be defined against the set of all lines (model.L). \n
    power[line] = (1/reactance[line]) * voltage_angle_delta[line]

    '''
    return model.pL[line] == (1/model.line_reactance[line])*model.deltaL[line]

def DCOPF_transformer(model,transformer):
    '''
    Kirchoff's Voltage Law (KVL) defined for each power transformer for the DC simplifcation of an AC system \n
    Should be defined against the set of all transformers (model.TRANSF). \n
    power[transformer] = (1/reactance[transformer]) * voltage_angle_delta[transformer]

    '''
    return model.pLT[transformer] == (1/model.transformer_reactance[transformer])*model.deltaLT[transformer]
