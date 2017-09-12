'''
Created on Aug 24, 2017

@author: bspar
'''
import APIs as api

if __name__ == '__main__':
#     startRefer = api.Reference("Laws of accident causation")
    
    startRefer = api.Reference(str('Driver ageing does not cause higher accident rates per km').encode('utf-8', 'ignore'))
    print startRefer[12]
    
    if startRefer[0] == None:
        print "No reference"
    else:
        startReferPii = startRefer[12]

        api.Citations(startReferPii)