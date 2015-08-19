# VentureCapitalAnalyzer
A tool to analyze Venture Capital Data exported from CrunchBase

# Manual
First, the keys.txt file has to be filled with keys. 
The crunchBase key can be requested on this site (http://data.crunchbase.com/v3/page/accessing-the-dataset)
The google keys just needs the gmail username and pw.
Twitter access is not necessary by now.

After filling the keys file, the program is started with either the statisticsDownloader to export data to a pkl file, or directly with the investDataAnalyzer file. Userinput is requested after starting the script.

#Description of files
dataBaseExporter.py: 	Export databases from Google Trends, Google News and Crunchbase. Returns a pandas dataframe for the searched for the attributes industry, starting date, end date and frequency.

investDataAnalyzer.py:	Does the main analysis work. Main script, will return descriptive statistics and diagrams.

keys.py: Text file for keeping the keys for the databases.

statisticsDownloader.py: Calls the export files. Collect the files and summarizes them according the input. Returns a the summarized data frame when calles or saves the dataframe when started directly.

#Required packages
pyGTrends - pip install pytrends