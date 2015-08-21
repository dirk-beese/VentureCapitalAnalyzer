import pandas as pd
import glob
import os
import matplotlib.pyplot as plt
from statisticDownloader import statisticDownloader


def checkUserInput(fileNumber= None):
    '''Asking for the data file that should be analyzed,
    calls the summarizing function if data file does not exist yet'''
    
    # checks all existing pkl files in folder
    fileDict = {}
    for index, fileName in enumerate(glob.glob("*.pkl")):
        fileDict.update({(index+1): fileName})
    fileDict.update({(len(fileDict.keys())+1) : "Something else"})

    if fileNumber is not None:
        fileName = fileDict[fileNumber]
        anaTable = pd.read_pickle(fileName)
        anaTable.name = fileName.split('_')
        print anaTable.name
        return anaTable

    print "Which file would you like to analye?"
    for i, j in fileDict.items():
        print "%s : %s." % (i,j)
    try:
        fileNumber = int(raw_input("Enter a number: "))
    except:
        sys.exit("You did not enter a number. Abort.")

    if fileNumber not in fileDict.keys():
        sys.exit("You did not enter a valid number. Abort.")
    
    #Gets User Input for the data export function
    elif fileNumber == len(fileDict.keys()): 
        print "What data would you like to analyze?"
        industryInput = raw_input("Industry (default is big data): ")
        if industryInput == "": 
              industry = "big data" 
        else: 
              industry = industryInput
        startDateInput = raw_input("Start date in form yyyy-mm-dd (default is 2010-01-01): ")
        if startDateInput == "":
              startDate = "2010-01-01"
        else:
             startDate = startDateInput
        endDateInput = raw_input("End date in form yyyy-mm-dd (default is 2014-12-31): ")
        if endDateInput == "":
              endDate = "2014-12-31" 
        else:
             endDate =endDateInput
        frequencyInput = raw_input("Frequency (year, quarter, month) (default is quarter): ")
        if frequencyInput == "":
              frequency = "quarter" 
        else:
             frequency = frequencyInput
        print "Your data is being exported, please wait."
        anaTable = statisticDownloader(industry, startDate, endDate, frequency)
        anaTable.name = ['statistics', industry, startDate, endDate, frequency]
        print "Your data was successfully downloaded. Save for later use?"
        decision = raw_input("1: Yes\n2: No\n")
        if decision == '1' or decision == 'Yes':
            filename = "statistics_%s_%s_%s_%s" % (industry,
                              startDate, endDate, frequency)
            anaTable.to_pickle('%s.pkl' % filename)
            print "Data was successfully saved to %s" % filename
        return anaTable
    
    # Get the number, open the file and return the table
    else:
        fileName = fileDict[fileNumber]
        anaTable = pd.read_pickle(fileName)
        anaTable.name = fileName.split('_')
        return anaTable

class Analyzer(object):
    '''Class for analyzing the data. Needs a dataframe'''

    def __init__(self, importTable):
        self.table = importTable


    def calc_correlations(self):
      	'''Calculate correlations between the variables'''
       	self.correlations = self.table.corr()
    
    def get_correlations(self):
    	'''Return the correlations. Calculate if necessary'''
        try: 
            self.correlations
        except:
            self.calc_correlations()
        return self.correlations

    def get_columns(self):
    	'''Get the columns of the tabel'''
        return self.table.columns.get_level_values(1)
    
    def get_column_list(self):
    	'''Zip the columns together because they built a multi index '''
        columnList = zip(self.table.columns.get_level_values(0), self.table.columns.get_level_values(1))
        choiceList = [' - '.join(zeile) for zeile in columnList]
        return choiceList

    def make_diagram(self, *args):
        '''Make diagram out of given arguments. Check frequency for the right ticks and datapoints. Safe plot in class'''
        self.fig = plt.figure()
        ax = self.fig.add_subplot(1, 1, 1)
        try:
            frequency_number = len(self.table.index.values[0])
        except:
            frequency_number = 1
        
        if frequency_number == 1: #test the frequency and adjust the ticks and datapoints
            indValues = [int(i) for i in self.table.index.values]
            years = indValues
        elif frequency_number == 2: #1 is years, 2 is quarters, 3 is months
            indValues = [(float(i)+float(j)/4) for i,j in self.table.index.values]
            years = list(set([i for i,_ in self.table.index.values]))
        elif frequency_number == 3:
            indValues = [(float(i)+float(j)/12) for i,_,j in self.table.index.values]
            years = list(set([i for i , _ , _ in self.table.index.values]))
        for line in args[0]:
            ax.plot(indValues, (self.table[line[0]][line[1]]/
                                self.table[line[0]][line[1]].sum()), 
                                marker = '.', label = ' - '.join(line))
        
        #Add attributes to the plot
        ax.set_xticks(years)
        ax.set_xticklabels(years, rotation = 45, fontsize = 'small')
        ax.set_xlabel('Time')
        ax.set_ylabel('Value in Percent')
        ax.legend(loc='center left', bbox_to_anchor=(1, 0.5))
        
    def make_diagram_input(self):
    	'''Ask user for input. Choosable are the variables from the dataframe.
    		Saves the diagram in the class'''
        user_input = None
        col_list = self.get_column_list()
        arg_list = []
        while user_input <> '0':
            print("Which arguments would you like to analyze?")
            print("0 : Thats it.")
            for index, entree in enumerate(col_list):
                print '%s : %s' % (index + 1, entree)
            user_input = raw_input("> ")
            if user_input <> '0':
                try:
                    argument = col_list.pop(int(user_input) -1)
                    arg_list.append(argument)
                except:
                    print "Please enter a valid number"
            print "Chosen arguments: %s\n" % arg_list
        if arg_list:
            self.make_diagram([i.split(' - ') for i in arg_list])

    def print_correlations(self):
    	'''Prints the useful correlation of the table'''
        correlation_list = self.get_correlations()
        print "Relevant correlations:"
        print self.correlations.applymap(lambda x: '%.3f' % float(x))   
        
    def print_summary(self):
    	print "Summary:"
    	print self.table.describe()
    	print ""

    def print_table(self):
    	print "Whole table:"
    	print self.table
    	print ""

    def save_diagram(self):
      	'''Save diagram to disk to the folder ./Images'''
        if not os.path.exists('./Images'):
            os.mkdir('./Images')
        try:
        	self.fig.savefig('./Images/Development of %s.png'% self.table.name[1], dpi = 400, bbox_inches = 'tight')
        	print "Diagram was saved to ./Images/Development of %s.png" % self.table.name[1]
        except:
        	print "No diagram has been created yet. Please create diagram first."

    def show_diagram(self):
        try:
        	plt.show()
        except:
        	print "No diagram has been created yet. Can't show a diagram."
    


if __name__ == '__main__':
    anaTable = Analyzer(checkUserInput())
    anaTable.print_table()
    anaTable.print_correlations()
    anaTable.make_diagram_input()
    anaTable.show_diagram()