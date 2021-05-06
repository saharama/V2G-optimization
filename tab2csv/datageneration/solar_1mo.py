import numpy as np
# import math
# from scipy.stats import truncnorm

#input file
fin = open("times.csv", "rt")
#output file to write the result to
fout = open("month_max_cf_solar.csv", "wt")

i = 0
#for each line in the input file
for line in fin:

# read in data like a meathead
	timepoint = line
	year = line[0:4]
	month = line[5:7]
	day = line[8:10]
	hour = line[11:13]
	minute = line[14:16] 
	# debug:
	#print(year + month + day + ' ' + hour +':' + minute)

	# define gaussian distribution for solar
	#mu, sigma = 0.5, 0.5
	#gaussian = np.random.normal(mu, sigma, 24)
	# solar generation must be positive
	#solar_hour = int(timedate[8:10])
		
	# scipy.stats.truncnorm
		
	# random number/load generation
	rng = np.random.default_rng()
	rfloat = rng.random()
	cos_meathead = [0,0,0,0.5,0.85,0.97,1,0.97,0.85,0.5,0,0]
	time_index = int(hour)
	#print(rfloat)
	if time_index > 18 or time_index < 6:
		solar_gen = 0
	else:
		solar_gen = rfloat * cos_meathead[int(time_index/2)] 

	# prepare data point
	textline = ','.join([timepoint[:-1],'Solar', str(solar_gen)])

	fout.write(textline)
	fout.write('\n')

#output files
fin.close()
#output files
fout.close()