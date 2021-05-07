import numpy as np

#input file
fin = open("times.csv", "rt")
#output file to write the result to
fout = open("ev_loads.csv", "wt")

fout.write('TIMEPOINT,vehicle,max_capacity,vehicle_state' + '\n')

# for each one of 11000 vehicles
for loop in range(11000):

	# determine vehicle being evaluated

	# determine initial state of charge

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

		# vehicle - determine type of vehicle

		# soc - state of charge (ratio between stored charge and max storage)
		rng = np.random.default_rng()
		rfloat = rng.random()

		# boolean - is the vehicle charging?
		vehicle_state = str(np.random.randint(0,2))

		textline = ','.join([timepoint[:-1],vehicle,soc,vehicle_state])

		fout.write(textline)
		fout.write('\n')

		#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()