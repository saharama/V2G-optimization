############################################
# EE635 Final Project
# Integration of V2G for Renewables
# Collaborators: Beck, David;
#                Leong, Christopher;
#                Sahara, Matthew W.;
# 
############################################


from pyomo.environ import (
    AbstractModel, Set, Param, Var, Constraint, 
    Objective, Expression, Reals, NonNegativeReals,
    Any, minimize, value, SolverFactory
)

m = AbstractModel()

#Objective: Optimize ? (cost)


#Insert a lot of constraints
#Curtailed energy must not exceed measured for data set
#
#
#CO2 emission free

#What do we need?
#Data on V2G
    #Cost to set up and maintain (charging station, vehicle)
    #Power data
#Model parameters
#Emergency cases: as reserves, model backfeed, use of vehicles as power source
    #cost analysis v battery degradation
    #time trace frequency of grid
#bulk charging?
#quantify services and optimize cost
#compare to grid connected default batteries already used
#or how much of this service do we need?