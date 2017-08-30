'''
Created on Aug 24, 2017

@author: bspar
'''
import APIs as api

if __name__ == '__main__':
    startRefer = api.Reference("Using bilateral trading to increase ridership and user permanence in ridesharing systems")
    if startRefer[0] == None:
        print "No reference"
    else:
        startReferPii = startRefer[12]
        
        citationList = api.Citations(startReferPii)
          
        for cite in citationList[0]:
            refer = api.Reference(cite[1])
            print refer