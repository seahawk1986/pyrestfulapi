#!/bin/env python
# * coding: utf-8 *

import time
import restfulapi
import os

### Settings ###
ip = "192.168.1.121"

R = restfulapi.RestfulAPI(ip)

while True:
        osd, extract = R.get_osd()
        #print "OSD:",osd
        #print "extracted", extract
        if osd != None:
            if len(extract['items']) >0:
                #print "-"*len(extract['title'])
                print extract['title']
                print "*"*len(extract['title'])
                for item in extract['items']:
                    #print type(item[2])
                    if item[2] == True:
                            a = '>>'
                    else:
                            a = '  '
                    if item[0] == "":             
                        print a,item[0], item[1]
                    else:
                        print "%s%s: %s"%(a,item[0], item[1])
                #print osd
            else:
                print extract['title']
                print "*"*len(extract['title'])
                print "No Content"
            line =  "RED: %s YELLOW: %s GREEN: %s BLUE: %s"%(extract['red'],extract['yellow'],extract['green'],extract['blue'])
            print "-"*len(line)
            print line
                
        else:
            print "No OSD"
        time.sleep(0.25)
        if os.name == "posix":
            os.system('clear')
        if os.name in ("nt","dos","ce"):
            os.system('CLS')
