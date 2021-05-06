import numpy as np

#input file
fin = open("times.csv", "rt")
#output file to write the result to
fout = open("month_max_cf_wind.csv", "wt")

fout.write('LOAD_ZONE,TIMEPOINT,zone_demand_mw' + '\n')

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

	# random number/load generation
	rng = np.random.default_rng()
	rfloat = rng.random()
	textline = ','.join([timepoint[:-1],'Wind', str(rfloat)])

	fout.write(textline)
	fout.write('\n')

	#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()