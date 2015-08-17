import googleDownloader
from googleDownloader import pyGTrends
import time
from random import randint
from pandas import DataFrame
import pandas as pd

def googleExport(googleDict, inputDict, exportType):
	
	# Define and import attributes for the google export
	google_username = googleDict['googleUserName']
	google_pass = googleDict['googlePassword']
	industry = inputDict['industry']
	
	# Create the csv downloader object
	downloader = pyGTrends(google_username, google_pass)

	# Wait some time to avoid blocking by google
	time.sleep(randint(0, 5))

	# Attributes for the url - differentiate between trends and news
	trendData = downloader.download_report(keywords = industry, gprop = exportType)
	return trendData

def googleFramer(googleDict, inputDict, exportType):
	
	# Define and import the relevant input arguments
	startDate = inputDict['startDate']
	endDate = inputDict['endDate']

	# Get the csv table from google downloader
	csvTable = googleExport(googleDict, inputDict, exportType)

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
