


branches = {
    #Constrains positive real power flow over each power line (model.L) to less than or equal to the continuous rated maximum of the line.
    'cont_realpower_max_pstve': lambda model,line: model.pL[line] <= model.line_max_continuous_P[line],
    #Constrain reverse real power flow over each power line (model.L) to less than or equal to the continuous rated maximum of the line.
    'cont_realpower_max_ngtve': lambda model,line: model.pL[line] >= -model.line_max_continuous_P[line]
}


demands ={
    #Constraints the realised real power demand (model output variable) to be equal to the input demand requirement, multiplied by the alpha factor (alpha is a real number between 0 and 1)
    'real_alpha_controlled': lambda model,demand: model.pD[demand] == model.alpha[demand]*model.PD[demand],
    #Constraint the demand controlling alpha factor to less than or equal to 1.
    'alpha_max': lambda model,demand: model.alpha[demand] <= 1,
    'alpha_fixneg': lambda model,demand: model.alpha[demand] == 1
}






...