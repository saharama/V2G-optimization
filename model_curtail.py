############################################
# EE635 Final Project
# Integration of V2G for Renewables
# Collaborators: Beck, David;
#                Leong, Christopher;
#                Sahara, Matthew W.;
# two models? one accounting for generation,
#             one with curtail data
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

#list of all vehicle types
m.VEHICLES = Set()

# amount of load to be served each timepoint
m.nominal_load = Param(m.TIMEPOINTS, within = Reals)

# load shifting
m.dispatchable_load_share = Param(mutable = True, within = Reals)

# *NEW* starting vehicle capacity
m.starting_capacity = Param(m.VEHICLES, within = Reals)

# *NEW* maximum capacity (kWh)
m.max_capacity = Param(m.VEHICLES, within = Reals)

# *NEW* curtailed pass through
m.curtailed_energy = Param(m.TIMEPOINTS, within = Reals)


#####################
# Decision Variables - what the model can output on its own

# let model decide if/when load is dispatched
m.DispatchLoad = Var(m.TIMEPOINTS)

# *NEW* let model decide how many of each vehicle exist
m.VehicleCount = Var(m.VEHICLES, within = NonNegativeIntegers)

# *NEW* let model decide how much energy is dispatched from curtail
m.DispatchCurtail = Var(m.TIMEPOINTS, within = NonNegativeReals)

#####################
# Objective Function
def TotalVehicles_rule(m):
    total_vehicles = sum(
        (
            m.fixed_cost_per_mw_per_hour[g] * m.BuildGen[g] +
            m.variable_cost_per_mwh[g] * (m.DispatchGen[g,t] + m.ChargeCurtail[t])
        )
        for t in m.TIMEPOINTS for g in m.GENERATORS
    )
    return total_cost / total_load
m.TotalVehicles = Objective(rule = TotalVehicles_rule, sense = minimize)

#####################
# Expressions

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
        m.starting_capacity[v]
        for v in m.VEHICLES
    )
    return total_start_capac
m.total_start_capacity = Expression(rule = total_start_capac_rule)

# *NEW* total battery capacity
m.BatteryCharge = Var(m.TIMEPOINTS, initialize = m.total_start_capacity)

# *NEW* vehicle storage capacity factor
#m.vehicle_cf = m.total_start_capac / m.total_max_capacity


#####################
# Constraints

# *NEW* Dispatched Curtail power never exceeds available curtailed + charged
def DispatchedCurtail_rule(m, t):
    return(
        m.DispatchCurtail[t] <= m.BatteryCharge[t] + m.ChargeCurtail[t]
    )
m.DispatchedCurtail = Constraint(
    m.TIMEPOINTS, rule = DispatchedCurtail_rule
)

# *NEW* battery charge never goes over mex capacity
def MaxCapacity_rule(m,t):
    return(
        m.BatteryCharge[t] <= m.total_max_capacity
    )
m.MaxCapacityTF = Constraint(
    m.TIMEPOINTS, rule = MaxCapacity_rule
)

def ChargeCurtail_rule(m,t):
    return(
        m.ChargeCurtail[t] <= m.total_max_capacity - m.BatteryCharge[t]
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