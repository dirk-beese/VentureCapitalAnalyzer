import pandas as pd
from pandas import DataFrame
import numpy as np

def dataSummarizer(inputDict, crunchBase, googleTrends= None, googleNews = None, frequence = 'Q'):
	
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
	dailyTable.rename(columns = {'IndustryPresent': 'Count','raised_amount_usd' : 'Funding Volume'}, inplace = True)


	if frequence.lower() in ['y','year','yearly']:
		return dailyTable.groupby([lambda x: x.year]).agg([np.sum, np.mean])
	elif frequence.lower() in ['q','quarter','quarterly']:
		return dailyTable.groupby([lambda x: x.year, lambda x: x.quarter]).agg([np.sum, np.mean])
	elif frequence.lower() in ['m','month','monthly']:
		return dailyTable.groupby([lambda x: x.year, lambda x: x.quarter, lambda x: x.month]).agg([np.sum, np.mean])
	else:
		return None