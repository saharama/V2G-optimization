############################################
# EE635 Final Project
# Integration of V2G for Renewables
# Collaborators: Beck, David;
#                Leong, Christopher;
#                Sahara, Matthew W.;
# two models? one accounting for generation,
#             one with curtail data
# account for each individual vehicle
############################################

from pyomo.environ import (
    AbstractModel, Set, Param, Var, Constraint, 
    Objective, Expression, Reals, NonNegativeReals,
    Any, minimize, value, SolverFactory, NonNegativeIntegers
)

m = AbstractModel()

#####################
# Parameters - what we define for the model

# Timepoints for model
m.TIMEPOINTS = Set(ordered=True)

# Duration between timepoints (hours)
m.timepoint_duration = Param(within = Reals)

# Date for each timepoint
m.date = Param(m.TIMEPOINTS, within = Any)

#list of all dates
def DATES_rule(m):
    unique_dates = set(m.date[t] for t in m.TIMEPOINTS)
    return sorted(unique_dates)
m.DATES = Set(initialize = DATES_rule)

#list of all generators
m.GENERATORS = Set()

#list of all vehicle types
m.VEHICLES = Set()

#maximum capacity factor 
m.max_cf = Param(m.GENERATORS, m.TIMEPOINTS, default = 1.0, within = Reals)

# amount of load to be served each timepoint
m.nominal_load = Param(m.TIMEPOINTS, within = Reals)

# load shifting
m.dispatchable_load_share = Param(mutable = True, within = Reals)

# costs of owning and operating each generator tech
m.fixed_cost_per_mw_per_hour = Param(m.GENERATORS, within = Reals)
m.variable_cost_per_mwh = Param(m.GENERATORS, within = Reals)

# *NEW* costs of owning and operating each V2G station (will this be necessary?)
# use base costs for charging, find rate for discharging
m.discharge_cost = Param(within = Reals)

# *NEW* maximum capacity (kWh)
m.max_capacity = Param(m.VEHICLES, within = Reals)

# *NEW* starting vehicle capacity
m.start_capacity = Param(m.VEHICLES, within = Reals)

# *NEW* define number of vehicles
#m.num_vehicles = Param(m.VEHICLES, within = NonNegativeIntegers)

# CO2 tons per MWh for each tech
m.co2_per_mwh = Param(m.GENERATORS, within = Reals)

# maximum amount of CO2 defined
m.co2_baseline_tons = Param(within = Reals)
m.co2_limit_vs_baseline = Param(mutable = True, within = Reals)



#####################
# Decision Variables - what the model can output on its own

# how much of each generator to build (MW) (maximum)
m.BuildGen = Var(m.GENERATORS, within = NonNegativeReals)

# power dispatched from each gen each hour (MW)
m.DispatchGen = Var(m.GENERATORS, m.TIMEPOINTS, within = NonNegativeReals)

# let model decide if/when load is dispatched
m.DispatchLoad = Var(m.TIMEPOINTS, within = Reals)

# *NEW* let model decide how many of each vehicle exist
m.NumVehicles = Var(m.VEHICLES, within = NonNegativeIntegers)

# *NEW* let model decide how much energy is dispatched from curtail
m.DispatchCurtail = Var(m.VEHICLES, m.TIMEPOINTS, within = NonNegativeReals)

# *NEW* battery capacity factor
# m.BatteryCharge = Var(m.TIMEPOINTS, initialize = m.total_start_capac)

# *NEW* let model decide how much energy is overproduced to curtail
m.ChargeCurtail = Var(m.VEHICLES, m.TIMEPOINTS, within = NonNegativeReals)

#####################
# Objective Function
def AverageCost_rule(m):
    total_cost = sum(
        (
            m.fixed_cost_per_mw_per_hour[g] * m.BuildGen[g] +
            m.variable_cost_per_mwh[g] * (m.DispatchGen[g,t] + m.ChargeCurtail[t])
        )
        for t in m.TIMEPOINTS for g in m.GENERATORS
    )
    total_load = sum(
        m.nominal_load[t]*m.timepoint_duration
        for t in m.TIMEPOINTS
    )
    return total_cost / total_load
m.AverageCost = Objective(rule = AverageCost_rule, sense = minimize)

#####################
# Expressions

#total CO2 emitted
def co2_total_tons_rule(m):
    total_tons = sum(
        (
            m.co2_per_mwh[g] * m.DispatchGen[g, t] * m.timepoint_duration
        )
        for g in m.GENERATORS for t in m.TIMEPOINTS
    )
    return total_tons
m.co2_total_tons = Expression(rule=co2_total_tons_rule)

def report_results(m):
    print(value(m.co2_total_tons))

# curtail
def curtailed_energy_rule(m, g, t):
    total_curtail = (
        (
            m.BuildGen[g] * m.max_cf[g,t] - m.DispatchGen[g, t]
        )
    )
    return total_curtail
m.curtailed_energy = Expression(
    m.GENERATORS, m.TIMEPOINTS, rule=curtailed_energy_rule
)

# *NEW* total maximum capacity kWh
def total_max_capacity_rule(m):
    total_max = sum(
        m.max_capacity[v] # * m.num_vehicles[v]
        for v in m.VEHICLES
    )
    return total_max
m.total_max_capacity = Expression(rule = total_max_capacity_rule)

# *NEW* total starting capacity in kwh
def total_start_capac_rule(m):
    total_start_capac = sum(
        m.start_capacity[v]
        for v in m.VEHICLES
    )
    return total_start_capac
m.total_start_capacity = Expression(rule = total_start_capac_rule)

# *NEW* total battery capacity
m.BatteryCharge = Var(m.VEHICLES, m.TIMEPOINTS, initialize = m.total_start_capacity)

# *NEW* vehicle storage capacity factor
#m.vehicle_cf = m.total_start_capac / m.total_max_capacity


#####################
# Constraints
# generated power + curtailed power serves load
def ServeLoadConstraint_rule(m, t):
    return (
        sum(m.DispatchGen[g, t] for g in m.GENERATORS) + m.DispatchCurtail[t]
        ==
        (m.nominal_load[t] + m.DispatchLoad[t] + m.ChargeCurtail[t])
    )
m.ServeLoadConstraint = Constraint(
    m.TIMEPOINTS, rule=ServeLoadConstraint_rule
)

# dispatched generated power must be less than what exists
def MaxOutputConstraint_rule(m, g, t):
    return (
        m.DispatchGen[g, t] <= m.BuildGen[g] * m.max_cf[g, t]
    )
m.MaxOutputConstraint = Constraint(
    m.GENERATORS, m.TIMEPOINTS, rule=MaxOutputConstraint_rule
)

# emitted CO2 must be less than what's allowed
def LimitCO2_rule(m):
    return (m.co2_total_tons <= m.co2_baseline_tons * m.co2_limit_vs_baseline)
m.LimitCO2 = Constraint(rule=LimitCO2_rule)

# DispatchLoad does not change total load served in the day
def NoDailyLoadChange_rule(m, d):
    return (
        sum(
            m.DispatchLoad[t]
            for t in m.TIMEPOINTS if m.date[t] == d
        )
        ==
        0
    )
m.NoDailyLoadChange = Constraint(
    m.DATES, rule= NoDailyLoadChange_rule
)

# DispatchLoad never exceeds that which is allowed
def LoadReduction_rule(m, t):
    return(
        m.DispatchLoad[t] >= -(m.dispatchable_load_share * m.nominal_load[t])
    )
m.LoadReduction = Constraint(
    m.TIMEPOINTS, rule = LoadReduction_rule
)

# *NEW* Dispatched Curtail power never exceeds available curtailed + charged
def DispatchedCurtail_rule(m, t):
    return(
        0 <= m.DispatchCurtail[t] <= m.BatteryCharge[t] + m.ChargeCurtail[t]
    )
m.DispatchedCurtail = Constraint(
    m.TIMEPOINTS, rule = DispatchedCurtail_rule
)

# *NEW* battery charge never goes over mex capacity
def MaxCapacity_rule(m, t):
    return(
        m.max_capacity >= m.BatteryCharge[t] >= 0
    )
m.MaxCapacity = Constraint(
    m.TIMEPOINTS, rule = MaxCapacity_rule
)

def ChargeCurtail_rule(m,t):
    return(
        0 <= m.ChargeCurtail[t] <= m.max_capacity - m.BatteryCharge[t]
    )
m.ChargeCurtailTF = Constraint(
    m.TIMEPOINTS, rule = ChargeCurtail_rule
)

#####################
# Solver

#m main solver
def solve(m, show_details=False):
    # get a solver object
    opt = SolverFactory("glpk")
    # create a working instance of the model with data from power_plan.dat
    print("loading model data...")
    instance = m.create_instance("model.dat")
    # solve the model
    print("solving model...")
    results = opt.solve(instance)

    # summarize the results
    if show_details:
        print(results)
        print("Solver Status: {}".format(results.solver.status))
        print("Solution Status: {}".format(instance.solutions[-1].status))
        print("Termination Condition: {}".format(results.solver.termination_condition))

        for g in instance.GENERATORS:
            print("{} built: {:.3f}".format(g, value(instance.BuildGen[g])))

    print("co2 emissions (tCO2): {}".format(value(instance.co2_total_tons)))
    print("co2 limit vs baseline: {}".format(value(instance.co2_limit_vs_baseline)))
    print("dispatchable load share: {}".format(value(instance.dispatchable_load_share)))
    print("cost per MWh: {}".format(value(instance.AverageCost)))

    # return the solved model for further analysis
    return instance

# val to str converter, csv maker
def csv(output):
    """Convert items in `output` into a comma-separated string,
    retrieving component values if needed."""
    vals = [str(value(val)) for val in output]
    return ','.join(vals) + '\n'

# write header to summary file
def create_summary_results_file():
    with open('results.csv', 'w') as f:
        f.write("co2_limit_vs_baseline,dispatchable_load_share,AverageCost,CO2_total_tons\n")

# append results to summary file
def save_summary_results(instance):
    # add results to the results file
    with open('results.csv', 'a') as f:
        f.write(csv([
            instance.co2_limit_vs_baseline,
            instance.dispatchable_load_share,
            instance.AverageCost,
            instance.co2_total_tons
        ]))

# create hourly data, write to hourly data
def save_hourly_results(instance):
    # create a file showing the hourly operation of each generation project
    output_file = 'dispatch_{}_co2_{}_dr.csv'.format(
        value(instance.co2_limit_vs_baseline),
        value(instance.dispatchable_load_share)
    )
    with open(output_file, 'w') as f:
        # note: in Python, the `+` operator concatenates lists
        header = (
            ["timepoint", "nominal_load", "actual_load"]
            + ["dispatch_" + value(g) for g in instance.GENERATORS]
            + ["curtail_" + value(g) for g in instance.GENERATORS]
            + ["curtail_charge", "dispatched_charge", "battery_capacity"]
        )
        f.write(csv(header))
        for t in instance.TIMEPOINTS:
            basic = [t, instance.nominal_load[t]]
            load = [instance.nominal_load[t] + instance.DispatchLoad[t]]
            gen = [instance.DispatchGen[g, t] for g in instance.GENERATORS]
            curtail = [instance.curtailed_energy[g, t] for g in instance.GENERATORS]
            cur_charge = [instance.ChargeCurtail[t]]
            dis_charge = [instance.DispatchCurtail[t]]
            bat_capac = [instance.BatteryCharge[t]]
            f.write(csv(basic + load + gen + curtail + cur_charge + dis_charge + bat_capac))


#only runs when model is run on its own
if __name__ == '__main__':
    # This is running as its own script, not via `import ...`
    # Solve the model using default values and report detailed results
    instance = solve(m, show_details=True)
    report_results(instance)
    save_hourly_results(instance)



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