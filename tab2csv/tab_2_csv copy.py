#input file
fin = open("tab_loads.txt", "rt")
#output file to write the result to
fout = open("csv_loads.txt", "wt")

#for each line in the input file
for line in fin:
	#read replace the string and write to output file
	fout.write(line.replace('\t', ','))

#close input and output files
fin.close()
fout.close()