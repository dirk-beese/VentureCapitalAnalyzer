import datetime
import sys

import pandas as pd
from pandas import DataFrame
import numpy as np

from dataBaseExporter import googleFramer, crunchBaseGrabber


def getKeys(dictionary,keys):
    for dictKey in dictionary.keys():
        dictionary[dictKey] = [key.split(':')[1].strip(' ,\t\n\r') for key in keys 
            if key.split(':')[0].strip(' ,\t\n\r') == dictKey][0]
    return dictionary

def dataSummarizer(inputDict, crunchBase, googleTrends= None, googleNews = None, frequency = 'Q'):
  
  #First, create an empty dataframe with the dates between start and enddate as index for a daily basis
  startDate = inputDict['startDate']
  endDate = inputDict['endDate']
  dateRange = pd.date_range(start = startDate, 
                           end = endDate,
                           freq = 'D')
  dailyTable = DataFrame(index = dateRange)

  # Match crunchbasedata to date dataframe, summarizing daily investments, in this first version I only consider venture capital investments, later a differitation will be possible  
  crunchBaseSub = crunchBase[(crunchBase['funding_round_type'] == 'venture')]
  crunchBaseArt = crunchBaseSub.groupby(['funded_at'])

  # Concate the tables from crunchbase, from Google NEws and Google Trends
  dailyTable = pd.concat([dailyTable,crunchBaseArt.count()['IndustryPresent'], crunchBaseArt.sum()['raised_amount_usd'], googleTrends, googleNews], axis = 1, join = 'outer')
  dailyTable.rename(columns = {'IndustryPresent': 'Count','raised_amount_usd' : 'FundingVolume'}, inplace = True)

  if frequency.lower() in ['y','year','yearly']:
    return dailyTable.groupby([lambda x: x.year]).agg([np.sum, np.mean])
  elif frequency.lower() in ['q','quarter','quarterly']:
    return dailyTable.groupby([lambda x: x.year, lambda x: x.quarter]).agg([np.sum, np.mean])
  elif frequency.lower() in ['m','month','monthly']:
    return dailyTable.groupby([lambda x: x.year, lambda x: x.quarter, lambda x: x.month]).agg([np.sum, np.mean])
  else:
    return None


def statisticDownloader(industry = 'data analytics', 
               startDate = datetime.datetime.now() - datetime.timedelta(365), 
               endDate = datetime.datetime.now(),
               frequency = 'Q'):

  # Transform date to datetime form and check if date inputs are in the right form
  dateForm = lambda x: datetime.datetime.strptime(x, '%Y-%m-%d')
  try:
    startDateFormat = dateForm(str(startDate))
  except:
    print "%s is not a valid start-date format, please enter in format 'yyyy-mm-dd'" % startDate
    return None
  try:
    endDateFormat = dateForm(str(endDate))
  except:
    print "%s is not a valid end-date format, please enter in format 'yyyy-mm-dd'" % endDate
    return None

  # Check for valid date input
  if startDateFormat < datetime.datetime(2008,01,01):
    print "Sorry, earliest possible start date is 2008-01-01 due to the late emerge of CrunchBase"
    return None
  if startDateFormat > endDateFormat:
    print "Sorry, the entered StartDate is after the entered EndDate"
    return None
  if endDateFormat > datetime.datetime.now():
    print "If i could look in the future, I would not program a python script but play lotto. Please enter an earlier EndDate"
    return None

  #Define Dictionaries
  crunchBaseDict = {'crunchBaseKey' : ''}
  googleDict = {'googleUserName' : '', 
                'googlePassword' : ''}
  # I plan to extend the functionality with twitter data (segment and number analysis, if they open up for tweets older than a week)   
  #    twitterDict = {'twitter_consumer_key' : '', 
  #                   'twitter_consumer_secret' : '', 
  #                   'twitter_access_token_key' : '', 
  #                   'twitter_access_token_secret' : ''}
  usedDicts = [crunchBaseDict, googleDict]

  #Load keys
  with open('./keys.txt', 'r') as keyFile: # path to key file
    keys = keyFile.readlines()
    for usedDict in usedDicts:
      usedDict = getKeys(usedDict,keys)

  #Build input dictionary  
    inputDict = {'industry' : industry, 'startDate' : startDateFormat, 'endDate' : endDateFormat}

  #Get data from CrunchBase, GopyGTrendsogle Trends and Google News and return in DataFrame format
  crunchBaseFrame = crunchBaseGrabber(crunchBaseDict, inputDict)
  googleTrendsFrame = googleFramer(googleDict, inputDict, 'trends')
  googleNewsFrame = googleFramer(googleDict, inputDict, 'news')

  #Use the CrunchBase and Google Data to create the final analysis table
  analysisTable = dataSummarizer(inputDict, crunchBaseFrame, googleTrendsFrame, googleNewsFrame, frequency)
  return analysisTable


if __name__ == '__main__':
  # Check if there are enough arguments, require userinput if not
    if len(sys.argv) <=4:
        print "Which data would you like to analyze?"
        industryInput = raw_input("Industry: ")
        if industryInput == "": 
          industry = "big data" 
        else: 
          industry = industryInput
        startDateInput = raw_input("Start date in form yyyy-mm-dd: ")
        if startDateInput == "":
          startDate = "2010-01-01"
        else:
         startDate = startDateInput
        endDateInput = raw_input("End date in form yyyy-mm-dd: ")
        if endDateInput == "":
          endDate = "2014-12-31" 
        else:
         endDate =endDateInput
        frequencyInput = raw_input("Frequency (year, quarter, month): ")
        if frequencyInput == "":
          frequency = "Quarter" 
        else:
         frequency = frequcenyInput
    elif len(sys.argv) >= 6:
      sys.exit("Too many arguments")
    else:
        industry, startDate, endDate, frequency = sys.argv[1:5]

    print "Data is being exported. Please wait, it takes around a minute."
    analysisTable = statisticDownloader(industry, startDate, endDate, frequency) #Start export, and return as dataframe
    filename = "statistics_%s_%s_%s_%s" % (industry, startDate, endDate, frequency)
    analysisTable.to_pickle('%s.pkl' % filename)
    print "Data was successfully saved to %s" % filename