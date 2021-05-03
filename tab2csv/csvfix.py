#input file
fin = open("max_cf.csv", "rt")
#output file to write the result to
fout = open("max_cf2.csv", "wt")

i = 0
#for each line in the input file
for line in fin:
	args = line.split(',')
	if i > 0 and ((i%2)=0):
		timedate = args[0]
		year = timedate[0:4] + '-'
		mon = timedate[4:6]+'-'
		day = timedate[6:8]
		hour = timedate[8:10]+':00'
		timepoint = ''.join([year, mon, day, ' ', hour])
		date = ''.join([year,mon,day])
		textline = ','.join([timepoint,date,stuff[1]])
	else:
		textline = ','.join(args)

	fout.write(textline)
	i = i +1

	#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()