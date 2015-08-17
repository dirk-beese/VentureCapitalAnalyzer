import pandas as pd
import datetime

import sys, os

from googleExport import googleFramer
from crunchBaseFramer import crunchBaseGrabber
from dataSummarizer import dataSummarizer

def getKeys(dictionary,keys):
    for dictKey in dictionary.keys():
        dictionary[dictKey] = [key.split(':')[1].strip(' ,\t\n\r') for key in keys 
            if key.split(':')[0].strip(' ,\t\n\r') == dictKey][0]
    return dictionary


def statisticDownloader(industry = 'data analytics', 
               startDate = datetime.datetime.now() - datetime.timedelta(365), 
               endDate = datetime.datetime.now(),
               frequence = 'Q'):

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

  if startDateFormat < datetime.datetime(2008,01,01):
    print "Sorry, earliest possible start date is 2008-01-01 due to the late emerge of CrunchBase"
    return None
  if startDateFormat > endDateFormat:
    print "Sorry, the entered StartDate is after the entered EndDate"
    return None
  if endDateFormat > datetime.datetime.now():
    print "Unfortunately, no one can look into the future. Not even a programmer :("
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
  analysisTable = dataSummarizer(inputDict, crunchBaseFrame, googleTrendsFrame, googleNewsFrame, frequence)
  analysisTable.to_pickle('statisticTable.pkl')

if __name__ == '__main__':
    statisticDownloader(industry = 'big data', startDate = '2010-01-01', endDate = '2015-01-01', frequence = 'Q')
