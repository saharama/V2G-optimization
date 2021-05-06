import numpy as np

#input file
fin = open("times.csv", "rt")
#output file to write the result to
fout = open("loads.csv", "wt")

fout.write('timepoint, date, system_load' + '\n')

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
	cos_meathead = [0.4,0.4,0.5,0.6,0.5,0.4,0.3,0.5,0.9,1,0.85,0.6]
	time_index = int(hour)
	#print(rfloat)

	# estimate of load characteristics based on min/max of 2020 est. load data
	load = 550 + 700 * rfloat * cos_meathead[int(time_index/2)] 

	datepoint_NBC = year + '-' + month + '-' + day
	textline = ','.join(['Oahu',timepoint[:-1],datepoint_NBC,str(load)])

	fout.write(textline)
	fout.write('\n')

	#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()