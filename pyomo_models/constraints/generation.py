"""
__authors__ = "Richard Nayer, Sam Hodges, Waqquas Bukhsh"
__credits__ = "RES, University of Strathclyde"
__version__ = "1.0.1"
__status__ = "Prototype"
"""
'''
Collection of constraints for conventional generators
'''


#-------------------------------------------------------------------------#
#                          Uncontrollable EER Policy
#
# Generators cannot be curtailed, and always output at their maximum.
#-------------------------------------------------------------------------#

def uncontrollable_realpower_sp(model, generator):
    '''
    Constrains output of each generator to equal to the setpoint. \n
    Should be defined against the set of uncontrollable generators (model.G_uncontrollable)
    '''
    return model.pG[generator] == model.PG[generator]


#-------------------------------------------------------------------------#
#                          MINGEN Requirements
#
# Constraint for generators with a MINGEN Requirement
#-------------------------------------------------------------------------#

def mingen_LB(model, generator):
    '''
    Constrains output of each generator to less than or equal to the maximum value. \n
    Should be defined against the set of individually curtailed generators (model.G_individual)
    '''
    return model.pG[generator] >= model.PGMINGEN[generator]





#-------------------------------------------------------------------------#
#                          Individual EER Policy
#
# Generators are curtailed individually based on their bid price.
#-------------------------------------------------------------------------#

def individual_realpower_max(model, generator):
    '''
    Constrains output of each generator to less than or equal to the maximum value. \n
    Should be defined against the set of individually curtailed generators (model.G_individual)
    '''
    return model.pG[generator] <= model.PGmax[generator]

def individual_realpower_min(model,generator): #Wind Power Minimum Power Output
    '''
    Constrains output of each generator  to greater than or equal to the minimum value. \n
    Should be defined against the set of individually generators (model.G_individual)
    '''
    return model.pG[generator] >= model.PGmin[generator]



#-------------------------------------------------------------------------#
#                       Pro-Rata ERG Curtailment
#
# Pro-Rata formulations ensure that curtailment/constraints of generators
# within a curtailment group is shared as a fixed percentage of each
# generators planned output. The formulation introduces a zeta variable 
# which is continuous between 0 and 1 to control the % curtailment, where
# 0 is full curtailment, and 1 is 100% output. 
#
# The formulation below allows for generators to belong to multiple constraint
# groups, and be curtailed/constrained in output to the level of the most constrained group.
# To enable this 'zeta' values are defined for each group, and each generator.
# A further 'zeta_bin' binary variable is introduced to ensure that individual generators
# cannot be curtailed further than the pro-rata value.
#
#
#-------------------------------------------------------------------------#

def prorata_realpower_max(model, generator):
    '''
    Constrains output of each generator to less than or equal to the maximum value, multiplied by the 'zeta' operator, where zeta is a number between 0 -> 1. \n
    Should be defined against the set of pro-rata generators (model.G_prorata)
    '''
    return model.pG[generator] <= model.PGmax[generator] * model.zeta_wind[generator]

def prorata_realpower_min(model,generator): 
    '''
    Constrains output of each generator to greater than or equal to the minimum defined value. \n
    Should be defined against the set of pro-rata generators (model.G_prorata)
    '''
    return model.pG[generator] >= model.PGmin[generator]

#Define the minimum power output of each generator in context of constraint groups and zeta
def prorata_realpower_min_zeta(model,generator): #Power Minimum Power Output
    '''
    Constrains output of each generator to greater than or equal to the minimum defined value, multiplied by the 'zeta' operator, where zeta is a number between 0 -> 1.  \n
    Should be defined against the set of pro-rata generators (model.G_prorata)
    '''
    return model.pG[generator] >= model.PGmax[generator] * model.zeta_wind[generator]

def prorata_zeta_max(model, generator, cg):
    '''
    Constraint that ensures the 'zeta' operator for each generator, is less than or equal to the 'zeta' operator of all the constraint groups (cg) to which the generator belongs. \n
    Should be defined against the set of pairs of wind generators and their constraint groups (model.WindCGPairs).
    '''
    return model.zeta_wind[generator] <=  model.zeta_cg[cg]

def prorata_zeta_min(model, generator, cg):
    '''
    Constraint that ensures that the 'zeta' operator for each generator is greater than at least one of the other 'zeta' operators within the constraint group. Note the inclusion of the zeta_bin variable, which is a binary value. \n
    Should be defined against the set of pairs of wind generators and their constraint groups (model.WindCGPairs). \n
    See link for more info on formulation: https://www.fico.com/fico-xpress-optimization/docs/dms2019-04/mipform/dhtml/chap2s1_sec_ssecminval.html
    '''
    return model.zeta_wind[generator] >= model.zeta_cg[cg] - (1 - 0) * (1-model.zeta_bin[(generator, cg)]) 

def prorata_zeta_binary(model, generator):
    '''
    Constraint that ensures that the sum of all of the binary 'zeta_bin' 
    Should be defined against the set of wind generators (model.WIND)
    See link for more info on formulation: https://www.fico.com/fico-xpress-optimization/docs/dms2019-04/mipform/dhtml/chap2s1_sec_ssecminval.html
    '''
    return sum(model.zeta_bin[(generator, cg)] for cg in model.G_prorata_map[generator]) == 1




#-------------------------------------------------------------------------#
#              Last-In-First-Out (LIFT) ERG Curtailment
#
# Generators are curtailed based on their position within a LIFO queue at a
# within a specific constraint group.
#-------------------------------------------------------------------------#

def LIFO_realpower_max(model, generators):
    '''
    Last-In-First-Out Constraint Rule \n
    Constrains output of each wind to less than or equal to the maximum value, multiplied by the 'Beta' operator, where Beta is a number between 0 -> 1. \n
    Should be defined against the set of wind generators (model.WIND)
    '''
    return model.pG[generators] <= (1 - model.beta[generators]) * model.PGmax[generators]

#Define the minimum power output of each generator (i.e. WGmin) in context of WGmin
def LIFO_realpower_min(model,generators): #Wind Power Minimum Power Output
    '''
    Last-In-First-Out Constraint Rule \n
    Constrains output of each wind to greater than or equal to the maximum value, multiplied by the 'gamma' operator, where gamma is a binary of either 1 or 0. \n
    Should be defined against the set of wind generators (model.WIND)
    '''
    return model.pG[generators] >= (1-model.gamma[generators])*model.PGmax[generators]

#LIFO gamma constraint, ensures w' (wind 1) can't be curtailed until w (wind 2) is curtailed)
def LIFO_gamma(model,gen1,gen2):
    '''
    Last-In-First-Out Constraint Rule \n
    Sets the gamma variable for wind 1 (that should be curtailed last) to less than or equal to 'gamma' wind 2 (that should be curtailed first).  \n
    Should be defined against the set of paired wind generators in order of priority within the LIFO group (model.LIFOset).
    '''
    return model.gamma[gen1] <= model.gamma[gen2]

#LIFO gamma constraint, 
def LIFO_beta(model,gen1,gen2):
    '''
    Last-In-First-Out Constraint Rule \n
    Sets the binary 'gamma' variable for wind 1 (that should be curtailed last) to less than or equal to 'Beta' for wind 2 (defined between 0 -> 1) (that should be curtailed first).  \n
    Should be defined against the set of paired wind generators in order of priority within the LIFO group (model.LIFOset).
    '''
    return model.gamma[gen1] <= model.beta[gen2]



# #-------------------------------------------------------------------------#
# #                    Pro-Rata SNSP Security Constraint
# #
# # Non-Synchronous Generators are curtailed pro-rata. to ensure that the SNSP
# # Limit is reached. SNSP limit to be defined within the constraint formulation.
# # 
# #-------------------------------------------------------------------------#

# def SNSP_prorata(model):
#     return (sum(model.pG[generator] for generator in model.G_ns)) / (sum(model.pG[generator] for generator in model.G_ns) + sum(model.pG[generator] for generator in model.G_s)) \
#     <= \
#     model.SNSP_limit

# def SNSP_pergen(model, generators):
#     return model.pG[generators] == model.PGmax[generators]*model.SNSP_zeta

def farm():
    '''
    Where functions go to retire, and they'll run through the fields and play forever and ever.
    '''
    # #-------------------------------------------------------------------------#
    # #                              Real Power
    # #-------------------------------------------------------------------------#

    # def realpower_max(model,generator): 
    #     '''
    #     Constrain real power output of each generator to less than or equal to it's maximum rated output. \n
    #     Should be defined against the set of conventional generators (model.G)
    #     '''
    #     return model.pG[generator] <= model.PGmax[generator]

    # #Generator Minimum Power OUtputs
    # def realpower_min(model,generator):
    #     '''
    #     Constrain real power output of each generator to greater than or equal to it's minimum rated output. \n
    #     Should be defined against the set of conventional generators (model.G)
    #     ''' 
    #     return model.pG[generator] >= model.PGmin[generator]