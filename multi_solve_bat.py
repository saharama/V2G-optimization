"""
This script runs the power planning model repeatedly with different
parameter values.
"""
from model import *

# create a working version of the model with data from power_plan.dat
instance = m.create_instance("model.dat")

# create a solver object
opt = SolverFactory("glpk")

n = 20 # number of carbon caps to consider
co2_limits = [float(x)/n for x in range(1,n+1)]
bat_capacs = [float(x)/n for x in range(1,n+1)]

# create a new empty results file
create_summary_results_file()

for co2_limit in [0.0, 0.25, 0.5, 0.75, 1.0]:
    for bat_capac in bat_capacs:
        # change values for the adjustable parameters
        instance.min_battery_capacity = bat_capac
        instance.co2_limit_vs_baseline = co2_limit
        instance.preprocess()

        # solve the model
        print(
            "solving model with co2_limit_vs_baseline={dl}, bat_capac={cl}"
            .format(dl=co2_limit, cl=bat_capac)
        )
        results = opt.solve(instance)

        # report and save results
        report_results(instance)
        report_avgcost(instance)
        save_summary_results(instance)
        # save_hourly_results(instance)
