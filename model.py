############################################
# Integration of V2G for Renewables
# 
#
############################################


from pyomo.environ import (
    AbstractModel, Set, Param, Var, Constraint, 
    Objective, Expression, Reals, NonNegativeReals,
    Any, minimize, value, SolverFactory
)

m = AbstractModel()