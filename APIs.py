# _*_ coding:utf-8 _*_

import requests
import json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

myKeyList = ["fc2cd979034828a84fdddf83d2f6edc9",
             "af898f18be0ce56baae06b12f60ba506",
             "9d90233827afd09ecabaa12a609a4a62"]

class Citations:
    def __init__(self, pii):
        self.MY_API_KEY = myKeyList[1]
        self.pii = pii
        
        self.attrs = {
                    0:[]
                    }
        
        citationList = self.elsevierRefers(pii)
        self.attrs[0]    = citationList
    
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key]
        
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key] = item
        
        
    def elsevierRefers(self, pii):
        resource = "http://api.elsevier.com/content/article/pii/"
        url = resource + pii
        webPage = requests.get(url)
        soup = BeautifulSoup(webPage.content, "xml")
          
        referList = soup.findAll('ce:bib-reference')
        
        citeList2 = []
        for refer in referList:
            citeList1 = []
#             print refer
        
            if refer.find('sb:edited-book'):
                authors = self.elsAuthor(refer)
#                 print authors
                
                source = self.elsSourceBook(refer)
#                 print source
                
                citeList1.append(authors)
                citeList1.append('')
                citeList1.append(source)
                
            elif refer.find('ce:textref'):
                text = self.elsTextRef(refer)
#                 print text
                
                citeList1.append('')
                citeList1.append(text)
                citeList1.append('')
            else:
                authors = self.elsAuthor(refer)
#                 print authors
                
                title = self.elsTitle(refer)
#                 print title
                
                source = self.elsSource(refer)
#                 print source
        
                citeList1.append(authors)
                citeList1.append(title)
                citeList1.append(source)
            
            citeList2.append(citeList1)
            
        return citeList2
    
    def elsAuthor(self, refer):
        authorStr = ''
        try: 
            authors = refer.findAll('sb:author')
        except(IndexError):
            pass
        else:
            for indx, auth in enumerate(authors):
                authorStr += str(auth.findAll('ce:given-name')[0].getText().encode('ascii', 'ignore'))
                authorStr += ' '
                authorStr += str(auth.findAll('ce:surname')[0].getText().encode('ascii', 'ignore'))
                
                if indx != len(authors)-1:
                    authorStr += ', '
            
        return authorStr
    
    def elsTitle(self, refer):
        maintitle = ''
        try:
            contribution = refer.findAll('sb:contribution')[0]
        except(IndexError):
            pass
        else:
            maintitle = str(contribution.findAll('sb:maintitle')[0].getText().encode('ascii', 'ignore'))
        
        return maintitle
        
    def elsSource(self, refer):
        source = ''
        try:
            host = refer.findAll('sb:host')[0]
        except(IndexError):
            pass
        else:
            maintitle = str(host.findAll('sb:maintitle')[0].getText().encode('ascii', 'ignore'))
            date = str(host.findAll('sb:date')[0].getText().encode('ascii', 'ignore'))
            
            firstPage = ''
            lastPage = ''
            try:
                pages = host.findAll('sb:pages')[0]
            except(IndexError):
                pass
            else:
                firstPage = str(pages.findAll('sb:first-page')[0].getText().encode('ascii', 'ignore'))
                lastPage = str(pages.findAll('sb:last-page')[0].getText().encode('ascii', 'ignore'))
            
            volume = ''
            try:
                volume = str(host.findAll('sb:volume-nr')[0].getText().encode('ascii', 'ignore'))
            except(IndexError):
                pass
            
            source = maintitle + ', ' + volume + ' (' + date + '), pp.' + firstPage + '-' +lastPage
        return source
            
    def elsSourceBook(self, refer):
        source = ''
        try:
            book = refer.findAll('sb:edited-book')[0]
        except(IndexError):
            pass
        else:
            maintitle = str(book.findAll('sb:maintitle')[0].getText().encode('ascii', 'ignore'))
            date = str(book.findAll('sb:date')[0].getText().encode('ascii', 'ignore'))
            publisher = str(book.findAll('sb:name')[0].getText().encode('ascii', 'ignore'))
            
            source = maintitle + ', ' + publisher + ' (' +date+')'
        
        return source 
            
    def elsTextRef(self, refer):
        text = ''
        try:
            textRef = refer.findAll('ce:textref')[0]
        except(IndexError):
            pass
        else:
            text = str(textRef.getText().encode('ascii', 'ignore'))
        return text
             
        
        
class Reference:
    def __init__(self, title):
        self.MY_API_KEY = myKeyList[1]
        self.title = title
        
        self.attrs = {
                      0: [None,  'scopusUrl',                    0],
                      1: [None,  'identifier',                   1],
                      2: [None,  'eid',                          2],
                      3: [None,  'title',                        3],
                      4: [None,  'publicationName',              4],
                      5: [None,  'issn',                         5],
                      6: [None,  'eIssn',                        6],
                      7: [None,  'volume',                       7],
                      8: [None,  'pageRange',                    8],
                      9: [None,  'coverDate',                    9],
                      10: [None,  'coverDisplayDate',            10],
                      11: [None,  'doi',                         11],
                      12: [None,  'pii',                         12],
                      13: [None,  'citedby-count',               13],
                      14: [None,  'authors',                     14],
                      15: [None,  'authorsList',                 15]}
        
        self.scorpusSearch(title)
        
        scopusUrl = self.attrs[0][0]
        if scopusUrl != None:
            self.scorpusAuthors(str(self.attrs[0][0]))
        
        
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
            
    def scorpusSearch(self, title):
        resource = "https://api.elsevier.com/content/search/scopus"
        url = (resource + "?query=" + title)
        resp = requests.get(url,
                    headers={'Accept':'application/json',
                             'X-ELS-APIKey': self.MY_API_KEY})
        results = json.loads(resp.text.encode('utf-8'))
        
        refer = self.matchCheck(results)
        
        print refer
        
        if refer != 'N/A':
            self.setAttr(refer)
        
    def matchCheck(self, results):
        matchRefer = 'N/A'
        try:
            resultList = results['search-results']['entry']
        except(KeyError):
            pass
        else:
            for refer in resultList:
                similarity = self.similar(refer['dc:title'], self.title)
                 
                if  similarity> 0.8:
                    matchRefer = refer
                    break
        return matchRefer
    
    
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
    
    def setAttr(self, refer):
        attrList = ['prism:url', 'dc:identifier', 'eid', 'dc:title', 'prism:publicationName', 'prism:issn', 'prism:eIssn', 'prism:volume', 'prism:pageRange', 'prism:coverDate', 'prism:coverDisplayDate', 'prism:doi', 'pii', 'citedby-count']
        
        for indx, attr in enumerate(attrList):
            try:
                refer[attr]
            except(KeyError):
                pass
            else:
                self.attrs[indx][0] = str(refer[attr])
            
#         self.attrs[0][0] = str(refer['prism:url'])
#         self.attrs[1][0] = str(refer['dc:identifier'])
#         self.attrs[2][0] = str(refer['eid'])
#         self.attrs[3][0] = str(refer['dc:title'])
#         self.attrs[4][0] = str(refer['prism:publicationName'])
#         self.attrs[5][0] = str(refer['prism:issn'])
#         self.attrs[6][0] = str(refer['prism:eIssn'])
#         self.attrs[7][0] = str(refer['prism:volume'])
#         self.attrs[8][0] = str(refer['prism:pageRange'])
#         self.attrs[9][0] = str(refer['prism:coverDate'])
#         self.attrs[10][0] = str(refer['prism:coverDisplayDate'])
#         self.attrs[11][0] = str(refer['prism:doi'])
#         self.attrs[12][0] = str(refer['pii'])
#         self.attrs[13][0] = str(refer['citedby-count'])
        
    
    def scorpusAuthors(self, scopusUrl):
        authors = self.scorpusAbstract(scopusUrl)
        authorList = authors['abstracts-retrieval-response']['authors']['author']
        
        auth = ''
        authList = []
        for indx, author in enumerate(authorList):
            auth += str(author['ce:indexed-name'])
            authList.append(str(author['@auid']))
            if indx != len(authorList)-1:
                auth += ', '
                
        self.attrs[14][0]= auth
        self.attrs[15][0]= authList
        
    def scorpusAbstract(self, scopusUrl):
        url = (scopusUrl + "?field=authors")
        resp = requests.get(url,
                    headers={'Accept':'application/json',
                             'X-ELS-APIKey': self.MY_API_KEY})
        results = json.loads(resp.text.encode('utf-8'))
        return results
                 
        
class SDS:
    #Science Direct Search
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
        print matchRefer
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
        