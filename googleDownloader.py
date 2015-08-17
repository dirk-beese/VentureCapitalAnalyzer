import httplib
import urllib
import urllib2 
import re
import csv
import logging
from cookielib import CookieJar

class pyGTrends(object):
    """
    Google Trends API
    
    Recommended usage:
    r = pyGTrends(username, password)
    trends_data = r.download_report(('pants', 'skirt'))
    """
    def __init__(self, username, password):
        """
        provide login and password to be used to connect to Google Analytics
        all immutable system variables are also defined here
        website_id is the ID of the specific site on google analytics
        """        
        self.login_params = {
            "continue": 'http://www.google.com/trends',
            "PersistentCookie": "yes",
            "Email": username,
            "Passwd": password,
        }
        self.headers = [("Referrer", "https://www.google.com/accounts/ServiceLoginBoxAuth"),
                        ("Content-type", "application/x-www-form-urlencoded"),
                        ('User-Agent', 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/535.21 (KHTML, like Gecko) Chrome/19.0.1042.0 Safari/535.21'),
                        ("Accept", "text/plain")]
        self.url_ServiceLoginBoxAuth = 'https://accounts.google.com/ServiceLoginBoxAuth'
        self.url_Export = 'http://www.google.com/accounts/ServiceLoginBoxAuth'
        self.url_CookieCheck = 'https://www.google.com/accounts/CheckCookie?chtml=LoginDoneHtml'
        self.url_PrefCookie = 'http://www.google.com'
        self.header_dictionary = {}
        self._connect()
        
    def _connect(self):
        """
        connect to Google Trends
        """
        self.cj = CookieJar()
        cook = urllib2.HTTPCookieProcessor(self.cj)
        self.opener = urllib2.build_opener(cook)
        self.opener.addheaders = self.headers
        
        #galx = re.compile('<input type="hidden"[\s]+name="GALX"[\s]+value="(?P<galx>[a-zA-Z0-9_-]+)">')        
        galx=re.compile('<input name="GALX"[\s]+type="hidden"[\s]+value="(?P<galx>[a-zA-Z0-9_-]+)">')
        resp = self.opener.open(self.url_ServiceLoginBoxAuth).read()
        resp = re.sub(r'\s\s+', ' ', resp)
        m = galx.search(resp)
        #    if not m:
        #         raise Exception("Cannot parse GALX out of login page")
        self.login_params['GALX'] = m.group('galx')
        params = urllib.urlencode(self.login_params)
        self.opener.open(self.url_ServiceLoginBoxAuth, params)
        self.opener.open(self.url_CookieCheck)
        self.opener.open(self.url_PrefCookie)

        
    def download_report(self, keywords, cmpt='q', date='all', geo='US', geor='all', gprop = 'trends', graph = 'all_csv', hl = 'en-US', sort=0, scale=0, sa='N'):
        """
        download a specific report
        date, geo, geor, graph, sort, scale and sa
        are all Google Trends specific ways to slice the data
        """
        if type(keywords) not in (type([]), type(('tuple',))):
            keywords = [keywords]
        
        params = urllib.urlencode({
            'cmpt' : cmpt,
            'q': ",".join(keywords),
            'date': date,
            'graph': graph,
            'geo': geo,
            'geor': geor,
            'gprop' : gprop,
            'hl': hl,
            'sort': str(sort),
            'scale': str(scale),
            'sa': sa
        })                            
        self.raw_data = self.opener.open('http://www.google.com/trends/viz?' + params).read()
        #self.raw_data = self.opener.open('https://www.google.com/trends/trendsReport?hl=en-US&content=1&q=foo&hl=en-US&content=1').read()
        
        if self.raw_data in ['You must be signed in to export data from Google Trends']:
            logging.error('You must be signed in to export data from Google Trends')
            raise Exception(self.raw_data)
        return self.raw_data    