import pandas as pd
import glob
import sys
import matplotlib as mpl
import matplotlib.pyplot as plt
import numpy as np
import scipy as sp
import math
from statisticDownloader import statisticDownloader

def checkUserInput():
    fileDict = {}
    for index, fileName in enumerate(glob.glob("*.pkl")):
        fileDict.update({(index+1): fileName})
    fileDict.update({(len(fileDict.keys())+1) : "Something else"})
    print "Which file would you like to analye?"
    for i, j in fileDict.items():
        print "%s : %s." % (i,j)
    try:
        fileNumber = int(raw_input("Enter a number: "))
    except:
        sys.exit("You did not enter a number. Abort.")

    if fileNumber not in fileDict.keys():
        sys.exit("You did not enter a valid number. Abort.")
    elif fileNumber == len(fileDict.keys()):
        print "Which file would you like to analyze?"
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
        print "Your data is being exported, please wait."
        anaTable = statisticDownloader(industry, startDate, endDate, frequency)
        print "Your data was successfully downloaded. Save for later use?"
        decision = raw_input("1: Yes\n2: No\n")
        if decision == '1' or decision == 'Yes':
            filename = "statistics_%s_%s_%s_%s" % (industry, startDate, endDate, frequency)
            anaTable.to_pickle('%s.pkl' % filename)
            print "Data was successfully saved to %s" % filename
        return anaTable
    else:
        anaTable = pd.read_pickle(fileDict[fileNumber])
        return anaTable

def analyzer(anaTable):
    anaTable = anaTable

if __name__ == '__main__':
    anaTable = checkUserInput()
    analyzer(anaTable)
