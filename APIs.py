'''
Created on Aug 24, 2017

@author: bspar
'''

import requests
import json


myKeyList = ["fc2cd979034828a84fdddf83d2f6edc9",
             "af898f18be0ce56baae06b12f60ba506",
             "9d90233827afd09ecabaa12a609a4a62"]

class SDS:
    def __init__(self, query):
        MY_API_KEY = myKeyList[0]
        self.query = query
        resource = "http://api.elsevier.com/content/search/scidir"
        
        url = (resource
          + "?query="
          + query)
#           + "&apiKey="
#           + self.myKeyList[0])
        
        resp = requests.get(url,
                    headers={'Accept':'application/json',
                             'X-ELS-APIKey': MY_API_KEY})
        
        results = json.loads(resp.text.encode('utf-8'))
        
        self.attrs = {
                      0: [None,  'identifier',               0],
                      1: [None,  'url',                      1],
                      2: [None,  'title',                    2],
                      3: [None,  'publicationName',          3],
                      4: [None,  'issueName',                4],
                      5: [None,  'issn',                     5],
                      6: [None,  'volume',                   6],
                      7: [None,  'issueIdentifier',          7],
                      8: [None,  'coverDisplayDate',         8],
                      9: [None,  'startingPage',             9],
                      10: [None,  'endingPage',              10],
                      11: [None,  'doi',                     11],
                      12: [None,  'pii',                     12],
                      13: [None,  'eid',                     13],
                      14: [None,  'authors',                 14]}
    
                
        refer = self.matchCheck(results)
        self.setAttr(refer)
                
        
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
    def matchCheck(self, results):
        resultList = results['search-results']['entry']
        matchRefer = 'N/A'
        for refer in resultList:
            if refer['dc:title'] == self.query:
                matchRefer = refer
                break
        return matchRefer
    
    def setAuthors(self, refer):
        authorsRaw = refer['authors']['author']
        authors = ''
        for indx, auth in enumerate(authorsRaw):
            authors += (auth['given-name']+' '
                        +auth['surname'])
            if indx != len(authorsRaw)-1:
                authors += ', '
        return authors
        
    
    def setAttr(self, refer):
        self.attrs[0][0] = str(refer['dc:identifier'])
        self.attrs[1][0] = str(refer['prism:url'])
        self.attrs[2][0] = str(refer['dc:title'])
        self.attrs[3][0] = str(refer['prism:publicationName'])
        self.attrs[4][0] = str(refer['prism:issueName'])
        self.attrs[5][0] = str(refer['prism:issn'])
        self.attrs[6][0] = str(refer['prism:volume'])
        self.attrs[7][0] = str(refer['prism:issueIdentifier'])
        self.attrs[8][0] = str(refer['prism:coverDisplayDate'])
        self.attrs[9][0] = str(refer['prism:startingPage'])
        self.attrs[10][0] = str(refer['prism:endingPage'])
        self.attrs[11][0] = str(refer['prism:doi'])
        self.attrs[12][0] = str(refer['pii'])
        self.attrs[13][0] = str(refer['eid'])
        
        author = self.setAuthors(refer)
        self.attrs[14][0] = str(author)
        