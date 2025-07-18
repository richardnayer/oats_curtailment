"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of Kirchoff's Current Law (KCL) constraints for use within OATS. 
'''


#-------------------------------------------------------------------------#
#                   Kirchoff's Current Law with Network
#-------------------------------------------------------------------------#

def networked_realpower_noshunt(model, bus):
    '''
    Kirchoff's Current Law (KCL) defined at all busses within the model to ensure power flow in equals power flow out. \n
    Should be defined against the set of all busses. \n
    Includes terms for:
    - Conventional Generators
    - Power Lines
    - Power Transformers
    - Demands
    '''
    return \
    + sum(model.pG[generator] for generator in model.generator_mapping[bus])\
    - sum(model.pL[line] for line in model.bus_line_out[bus])\
    + sum(model.pL[line] for line in model.bus_line_in[bus])\
    - sum(model.pLT[transformer] for transformer in model.bus_transformer_out[bus])\
    +sum(model.pLT[transformer] for transformer in model.bus_transformer_in[bus])\
    ==\
    sum(model.pD[demand] for demand in model.demand_bus_mapping[bus])


def networked_realpower_withshunt(model, bus):
    '''
    Kirchoff's Current Law (KCL) defined at all busses within the model to ensure power flow in equals power flow out. \n
    Should be defined against the set of all busses (model.B). \n
    - Conventional Generators
    - Power Lines
    - Power Transformers
    - Demands
    - Shunts
    '''
    return \
    + sum(model.pG[generator] for generator in model.generator_mapping[bus])\
    - sum(model.pL[line] for line in model.bus_line_out[bus])\
    + sum(model.pL[line] for line in model.bus_line_in[bus])\
    - sum(model.pLT[transformer] for transformer in model.bus_transformer_out[bus])\
    +sum(model.pLT[transformer] for transformer in model.bus_transformer_in[bus])\
    ==\
    sum(model.pD[demand] for demand in model.demand_bus_mapping[bus]) +\
    sum(model.GB[s] for s in model.SHUNT if (bus,s) in model.SHUNTbs)


#-------------------------------------------------------------------------#
#                   Kirchoff's Current Law for Copper Plate
#-------------------------------------------------------------------------#

def copperplate_realpower(model):
    '''
    Kirchoff's Current Law (KCL) defined for a copper-plate to ensure power flow in equals power flow out. \n
    Should be defined against the set of all busses. \n
    Includes terms for:
    - Generators
    - Demands
    '''
    return \
    + sum(model.pG[generator] for generator in model.G)\
    ==\
    sum(model.pD[demand] for demand in model.D)