# This file combines the data from aseg_stats.xlsx and subject_info_v2.txt into a new
# file (brain_data.csv) whose data is cleaned and ready to be analyzed.
# Output files: brain_data.csv, aseg_stats.csv (csv version of aseg_stats.xlsx),
# and subject_info_v2.csv (csv version of subject_info_v2.txt)
# ** note: brain_data.csv has 977 rows, but aseg_stats.csv has 998 rows. some patients' data
# were lost, either because they were took out or because their id didn't match with
# id's in subject_info_v2.txt

import csv
import xlrd

# Parameters: txt_file (.txt file, tab delimited); csv_file (name for output file)
# Method reads in txt_file and creates a new csv file containing data from txt_file
def txt_to_csv(txt_file, csv_file):
	in_txt = csv.reader(open(txt_file, "rU"), dialect=csv.excel_tab)
	out_csv = csv.writer(open(csv_file, 'wb'))
	out_csv.writerows(in_txt)

# Parameters: xlsx_wkbk (excel workbook to be read); sheet_name (sheet within that workbook);
# csv_file (name for output file)
# Method reads in data from the specified sheet of the specified excel workbook and creates
# a new csv file containing that data
def xlsx_to_csv(xlsx_wkbk, sheet_name, csv_file):
	wb = xlrd.open_workbook(xlsx_wkbk)
	sh = wb.sheet_by_name(sheet_name)
	csv_file = open(csv_file, 'wb')
	wr = csv.writer(csv_file, quoting=csv.QUOTE_ALL)

	for rownum in xrange(sh.nrows):
		wr.writerow(sh.row_values(rownum))

	csv_file.close()

# Parameters: brain_data (data from aseg_stats.csv); gender_data (data from subject_info_v2.csv)
# Method outputs a new csv file (brain_data.csv):
# 	1. writes in gender data to rows from aseg_stats.csv
#	2. takes out the two rows from aseg_stats.csv that have incomplete data
#	3. takes out columns in aseg_stats.csv with no data (age, height, and tanner_stage)
def combine_files(brain_data, gender_data):
	gender_map = {}
	gender_rows = []
	with open(gender_data) as csvfile:
		reader = csv.reader(csvfile)
		gender_rows = list(reader)
	del gender_rows[0]
	for patient in gender_rows:
		gender_map[patient[1]] = patient[2]

	brain_stats = []
	with open(brain_data) as csvfile:
		reader = csv.reader(csvfile)
		brain_stats = list(reader)
	#these patients are missing data
	brain_stats = [x for x in brain_stats if x[1] != 603061555716 or x[1] != 609054620434]
	for stats in brain_stats[1:]:
		#some subject id's contain decimal points (.0)
		stats[1] = stats[1].split(".", 1)[0]
		#sex
		if(stats[1] in gender_map):
			stats[2] = gender_map[stats[1]]
		else:
			brain_stats.remove(stats)

	#take out columns that have no data
	brain_stats[0] = [x for x in brain_stats[0] if x not in ['Age', 'Height', 'Tanner_Stage']]
	#take out those with data that's all zero: 'Left-WM-hypointensities', 
	#'Right-WM-hypointensities', 'Left-non-WM-hypointensities', 'Right-non-WM-hypointensities'
	#indices = indices for those four brain regions in each row
	indices = [i for i, j in enumerate(brain_stats[0]) if j in ['Left-WM-hypointensities', 'Right-WM-hypointensities', 
		'Left-non-WM-hypointensities', 'Right-non-WM-hypointensities']]
	brain_stats[0] = [x for x in brain_stats[0] if x not in ['Left-WM-hypointensities', 'Right-WM-hypointensities', 
		'Left-non-WM-hypointensities', 'Right-non-WM-hypointensities']]

	#change column names that begin with digits to begin with letters
	for i, name in enumerate(brain_stats[0]):
		if(name == '3rd-Ventricle'):
			brain_stats[0][i] = 'Third-Ventricle'
		elif(name == '4th-Ventricle'):
			brain_stats[0][i] = 'Fourth-Ventricle'
		elif(name == '5th-Ventricle'):
			brain_stats[0][i] = 'Fifth-Ventricle'
			
	index = 1
	for stats in brain_stats[1:]:
		brain_stats[index] = filter(lambda a: a!='', brain_stats[index])
		brain_stats[index] = [i for j, i in enumerate(brain_stats[index]) if j not in indices]
		index = index+1 #colum number


	#write to csv
	csv_file = csv.writer(open('data/brain_data.csv', 'wb'))
	csv_file.writerows(brain_stats)


if __name__ == "__main__":

	# Convert files into csv files
	txt_to_csv('data/subject_info_v2.txt', 'data/subject_info_v2.csv')
	xlsx_to_csv('data/aseg_stats.xlsx', 'aseg_stats', 'data/aseg_stats.csv')

	# Combine two data files
	combine_files('data/aseg_stats.csv', 'data/subject_info_v2.csv')

