import numpy as np
import math
from scipy.stats import truncnorm

#input file
fin = open("tab_loads.txt", "rt")
#output file to write the result to
fout = open("max_cf_solar.csv", "wt")

i = 0
#for each line in the input file
for line in fin:
	stuff = line.split('\t')
	stuff.pop(0)
	if i > 0:
		timedate = stuff[0]
		year = timedate[0:4] + '-'
		mon = timedate[4:6]+'-'
		day = timedate[6:8]
		hour = timedate[8:10]+':00'
		timepoint = ''.join([year, mon, day, ' ', hour])
		date = ''.join([year,mon,day])

		# define gaussian distribution for solar
		#mu, sigma = 0.5, 0.5
		#gaussian = np.random.normal(mu, sigma, 24)
		# solar generation must be positive
		#solar_hour = int(timedate[8:10])
		
		# scipy.stats.truncnorm
		
		# random number/load generation
		rng = np.random.default_rng()
		rfloat = rng.random()
		cos_meathead = [0,0,0,0.5,0.85,1,1,1,0.85,0.5,0,0]
		time_index = int(timedate[8:10])
		print(rfloat)
		if time_index > 18 or time_index < 6:
			solar_gen = 0
		else:
			solar_gen = rfloat * cos_meathead[int(time_index/2)] 

		# prepare data point
		textline = ','.join([timepoint,'Solar', str(solar_gen)])
	else:
		# initialize the first line
		textline = ','.join([stuff[0],'date',stuff[1]])

	fout.write(textline)
	fout.write('\n')
	i = i + 1

	#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()