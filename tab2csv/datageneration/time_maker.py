## File that generates times in 2 hour increments for a month.
## I may have brute forced this, not best python practices

#output file to write the result to
fout = open("times.csv", "wt")

year = '2021'
month = '06'

# csv header
fout.write('TIMEPOINT')

for day in range(32):
	day_str = day
	if day < 10:
		day_str = '0' + str(day)
	for hour in range(12):
		if (hour-1) < 4:
			textline = ''.join([year,'-',month,'-',str(day_str),' ','0',str(hour*2),':00'])
		else:
			textline = ''.join([year,'-',month,'-',str(day_str),' ',str(hour*2),':00'])
		fout.write(textline)
		fout.write('\n')

#output files
fout.close()
