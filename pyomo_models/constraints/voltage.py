"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of Voltage constraints for use within OATS. Includes:
- Voltage Angle
- TBC
'''


#-------------------------------------------------------------------------#
#                            Voltage Angles
#-------------------------------------------------------------------------#

def line_delta(model,line):
    '''
    Require voltage angle difference (deltaL[line]) across each power line to be equal to the voltage angle at each bus (delta[bus]) \n
    Define against set of lines (model.L)
    '''
    return \
    model.deltaL[line] == \
    + model.delta[model.line_busses[line].at(1)]\
    - model.delta[model.line_busses[line].at(2)]


def transformer_delta(model,transformer):
    '''
    Require voltage angle difference (deltaL[transformer]) across each transformer to be equal to the voltage angle at each bus (delta[bus]) \n
    Define against set of transformers (model.TRANSF)
    '''
    return \
    model.deltaLT[transformer] == \
    + model.delta[model.transformer_busses[transformer].at(1)]\
    - model.delta[model.transformer_busses[transformer].at(2)]


#-------------------------------------------------------------------------#
#                        Reference Bus Voltage
#-------------------------------------------------------------------------#

def reference_bus(model,bus):
    '''
    Constrain the voltage angle of the reference bus to 0 \n
    MUST BE DEFINED AGAINST THE REFERENCE BUS SET (mode.b0), WHICH CONTAINS A SINGLE BUS REFERENCE
    '''
    return model.delta[bus]==0


