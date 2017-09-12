# _*_ coding:utf-8 _*_

# encoding=utf8
import sys
reload(sys)
sys.setdefaultencoding('utf8')


import urllib2
import requests
import json
from bs4 import BeautifulSoup
from difflib import SequenceMatcher

from selenium import webdriver
from bs4 import BeautifulSoup

from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.firefox.firefox_binary import FirefoxBinary
from selenium.common.exceptions import TimeoutException

myKeyList = ["fc2cd979034828a84fdddf83d2f6edc9",
             "af898f18be0ce56baae06b12f60ba506",
             "9d90233827afd09ecabaa12a609a4a62"]

class Citations:
    def __init__(self, pii):
        self.MY_API_KEY = myKeyList[0]
        self.pii = pii
        
        self.attrs = {
                    0:[]
                    }
        
        sciDir = self.getSciDir(pii)
        referList = self.getReferenceList(sciDir)
        print referList
        
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key]
        
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key] = item
            
    def getSciDir(self, pii):
        resource = "http://api.elsevier.com/content/article/pii/"
        url = resource + pii
        
        webPage = requests.get(url)
        soup = BeautifulSoup(webPage.content.decode('utf-8'), "xml")
        
        try:
            sciDir = soup.find('link',{'rel':'scidir'}).get('href')
        except:
            sciDir = 'N/A'
        return sciDir
        
    def getReferenceList(self, sciDir):
        driver = webdriver.Firefox(executable_path=r'geckodriver.exe')
        driver.get(sciDir)
        driver.maximize_window()
        
        url = sciDir
        literatureList = []
        try:
            element = WebDriverWait(driver, 30).until(EC.presence_of_element_located((By.CLASS_NAME, 'references')))
            print "Page Ready"
        except(TimeoutException):
            print "Fail to load"
        else:
            soup = BeautifulSoup(driver.page_source.decode('utf-8'),"lxml")
            driver.quit()
            
            references = soup.find('dl', {'class':'references'})
            reference = references.findAll('dd', {'class':'reference'})
            
            
            for refer in reference:
#                 print refer
                try:
                    contribution = refer.find('div', {'class':'contribution'})
                    authors = contribution.getText().encode('utf-8', 'ignore')
                    try:
                        title = contribution.find('strong', {'class':'title'}).getText().encode('utf-8', 'ignore')
                    except:
                        title = ''
                    host = refer.find('div', {'class':'host'}).getText().encode('utf-8', 'ignore')                     
                except:
                    literature = refer.find('span').getText().encode('utf-8', 'ignore')
                else:
                    literature = authors + ', ' + title + ', ' + host
                
                print literature
                literatureList.append(literature)
        return literatureList

        
class Reference:
    #Science Direct Search
    def __init__(self, title):
        MY_API_KEY = myKeyList[2]
        self.title = title
        resource = "http://api.elsevier.com/content/search/scidir"
        
        url = (resource
          + "?query="
          + title)
#           + "&apiKey="
#           + self.myKeyList[0])
        
        resp = requests.get(url,
                    headers={'Accept':'application/json',
                             'X-ELS-APIKey': MY_API_KEY})
        
        print '(Input title)' + str(title)
        
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
        
        if refer != 'N/A':
            self.setAttr(refer)
                
        
    def __getitem__(self, key):
        if key in self.attrs:
            return self.attrs[key][0]
        
    def __setitem__(self, key, item):
        if key in self.attrs:
            self.attrs[key][0] = item
            
    def matchCheck(self, results):
        matchRefer = 'N/A'
        try:
            resultList = results['search-results']['entry']
        except(KeyError):
            pass
        else:
            for refer in resultList:
                similarity = self.similar(refer['dc:title'], self.title)
                print 'Similarity score = ' + str(similarity) + '(/1.0)'
                
                if  similarity> 0.8:
                    matchRefer = refer
                    print "(matched to) "+str(matchRefer['dc:title'].encode('utf-8', 'ignore'))
                    break
        if matchRefer == 'N/A':
            print "No matched reference"
        return matchRefer
    
    
    def similar(self, a, b):
        return SequenceMatcher(None, a, b).ratio()
    
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
        attrList = ['dc:identifier', 'prism:url', 'dc:title', 'prism:publicationName', 'prism:issueName', 'prism:issn', 'prism:volume', 'prism:issueIdentifier', 'prism:coverDisplayDate', 'prism:startingPage', 'prism:endingPage', 'prism:doi', 'pii', 'eid']
        
        for indx, attr in enumerate(attrList):
            try:
                refer[attr]
            except(KeyError):
                pass
            else:
                self.attrs[indx][0] = str(refer[attr]).encode('utf-8', 'ignore')

        try:
            author = self.setAuthors(refer)
        except(KeyError):
            pass
        else:
            self.attrs[14][0] = str(author).encode('utf-8', 'ignore')
        