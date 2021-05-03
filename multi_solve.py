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

# create a new empty results file
create_summary_results_file()

for dispatchable_load in [0.0, 0.3]:
    for co2_limit in co2_limits:
        # change values for the adjustable parameters
        instance.co2_limit_vs_baseline = co2_limit
        instance.dispatchable_load_share = dispatchable_load
        instance.preprocess()

        # solve the model
        print(
            "solving model with dispatchable_load={dl}, co2_limit={cl}"
            .format(dl=dispatchable_load, cl=co2_limit)
        )
        results = opt.solve(instance)

        # report and save results
        report_results(instance)
        report_avgcost(instance)
        save_summary_results(instance)
        # save_hourly_results(instance)
