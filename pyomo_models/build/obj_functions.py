import numpy as np

def dcopf_marginal_cost_objective(instance):
    '''
    Objective function for marginal costs: \n
     - Linear Generator Costs (c0 + c1), peturbed by random value between [0,1) to break symmetry
     - Value of Lost Load of Demands
     - Bid Price of Wind against total
     - TAKE CARE: Power variables are still in p.u, scaled by baseMVA. Therefore
        resulting obj will also be scaled by baseMVA. Variables not re-scaled here
        in cost function to avoid numerical trouble in solver
    '''
    rnd = np.random.default_rng(100)

    obj = sum((instance.c1[g]+rnd.random())*instance.pG[g]+(instance.c0[g]/instance.baseMVA) for g in instance.G) +\
          sum(instance.VOLL[d]*(1-instance.alpha[d])*instance.PD[d] for d in instance.D)+ \
          sum(instance.bid[g] * (instance.PGmax[g]-instance.pG[g]) for g in instance.G)
    return obj
