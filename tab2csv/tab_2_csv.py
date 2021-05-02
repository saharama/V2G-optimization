#input file
fin = open("tab_loads.txt", "rt")
#output file to write the result to
fout = open("csv_loads2.csv", "wt")

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
		textline = ','.join([timepoint,date,stuff[1]])
	else:
		textline = ','.join([stuff[0],'date',stuff[1]])

	fout.write(textline)
	i = i +1

	#read replace the string and write to output file

#close input and output files
fin.close()
fout.close()