import os
import urllib
import requests
import time
from random import randint

from pandas import DataFrame
import pandas as pd

from googleDownloader import pyGTrends


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
	    resp = requests.get(cbUrl)
	    with open('./Excel/excelExport.xlsx', 'wb') as output:
	    	output.write(resp.content)

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


def googleFramer(googleDict, inputDict, exportType):
	
	# Define and import the relevant input arguments
	startDate = inputDict['startDate']
	endDate = inputDict['endDate']
	industry = inputDict['industry']
	google_username = googleDict['googleUserName']
	google_pass = googleDict['googlePassword']

	# Create the csv downloader object
	downloader = pyGTrends(google_username, google_pass)

	# Wait some time to avoid blocking by google
	time.sleep(randint(0, 5))

	# Attributes for the url - differentiate between trends and news
	csvTable = downloader.download_report(keywords = industry, gprop = exportType)

	# Export only relevant week data (quick and dirty solution, will improve it in a later version)
	weeksTable = csvTable.split('\n')[5:]
	count = 0
	numberEntrees = 0
	for check in weeksTable:
	    if check == '':
	        count +=1
	    else:
	        numberEntrees +=1
	    if count == 2:
	        break
	
	# Split the rows into a 3-value list and extract only the endweek and the index value (2 values) (Note: Google shows values for the week, thus I use the endweek value and not the starweek value)
	weekList = []
	wochenListe = [entree.split(' - ')[1:3] for entree in
	               [' - '.join(weekly.split(',')) for weekly in weeksTable[:numberEntrees]]]
	for woche in wochenListe:
		if woche[1] not in ['',' ']:
			weekList.append([woche[0], int(woche[1])])
	# Create a dataframe out of the week list         
	resultFrame = DataFrame(weekList, columns = ['EndWeek', 'Google Index for %s' % exportType.capitalize()])
	
	# Change date to datetime format
	resultFrame['EndWeek'] = pd.to_datetime(resultFrame['EndWeek'])
	
	#Use the endweek as index for a later merge
	resultFrame = resultFrame.set_index('EndWeek')
	
	# Crate a new range with all days between start date and enddate
	dateRange = pd.date_range(start = startDate, 
	                          end = endDate,
	                          freq = 'D')

	# Merge daterange list and the google index list - use backfill to fill empty spaces with the relevant value 
	googleFrame = pd.concat([DataFrame(index = dateRange),resultFrame], axis = 1).fillna( method = 'backfill')
	return googleFrame.ix[startDate:endDate]
