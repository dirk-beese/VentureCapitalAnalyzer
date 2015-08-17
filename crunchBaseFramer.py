import os
import urllib
import pandas as pd
import datetime

def crunchBaseGrabber(crunchBaseDict, inputDict):

	#Get the input arguments
	cbKey = crunchBaseDict['crunchBaseKey']
	startDate = inputDict['startDate']
	endDate = inputDict['endDate']
	industry = inputDict['industry']

	'''There is no API which grants an overviewing access to the crunchbase funding data,
	thus the excel import is used.
	First the programm checks if the file is already on disk in the 'Excel Folder'. If no, its downloaded and saved.
	'''

	cbUrl = 'https://api.crunchbase.com/v/3/excel_export/crunchbase_export.xlsx?user_key=%s' % cbKey
	if not os.path.exists('./Excel'):
	    os.mkdir('./Excel')
	if not os.path.exists('./Excel/excelExport.xlsx'):
	    urllib.urlretrieve(cbUrl, './Excel/excelExport.xlsx')

	#Load Excel file and import as a pandas data frame
	cbExcelFile = pd.ExcelFile('./Excel/excelExport.xlsx')
	cbExcel = cbExcelFile.parse('Rounds', index_col = None, na_values=['NA'])

	#Function to match the company_category_list to the searched industry for later filtering
	def matchIndustry(x):
	    industryList = str(x).lower().split('|')
	    if industry.lower() in industryList:
	        return True
	    else:
	        return False
	cbExcel['IndustryPresent'] = cbExcel[['company_category_list']].applymap(matchIndustry)

	#Transform fundet_at column to datetime format
	cbExcel['funded_at'] = pd.to_datetime(cbExcel['funded_at'])

	#Filter out relevant results - between starting and enddate, matching industry. Return sorted dataframe
	cbExcelFinal = cbExcel[(cbExcel['funded_at'] >= startDate) & (cbExcel['funded_at'] <= endDate) & (cbExcel['IndustryPresent'] == True) & (cbExcel['company_country_code'] == 'USA')].sort(columns = 'funded_at')
	return cbExcelFinal