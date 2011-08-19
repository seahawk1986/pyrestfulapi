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
                    # replace private unicode characters by chars
                    if type(item[1]) == str or type(item[1]) == unicode:
                        item[1] = item[1].replace(u'\ue000',u'[W]').replace(u'\ue002',u'[F]').replace(u'\ue003',u'').replace(u"\ue00f",u'[TV]').replace(u"\ue00e",u"[R]").replace(u'\ue00c',u'[T]  ').replace(u'\ue00b',u'[REC]').replace(u' \t',u'    \t')
                    #print item
                    if item[2] == True:
                            a = '>>'
                    else:
                            a = '  '
                    if item[0] == "":             
                        print a,item[0], item[1]
                    else:
                        print "%s%s: %s"%(a,item[0], item[1])
                print osd
            else:
                print extract['title']
                if extract['title'] != None:
                    print "*"*len(extract['title'])
                else: print "*"*20
                print "No Content"
            line =  "RED: %s | YELLOW: %s | GREEN: %s | BLUE: %s"%(extract['red'],extract['yellow'],extract['green'],extract['blue'])
            print "-"*len(line)
            print line
                
        else:
            print "No OSD"
            channel, playing =  R.get_info()
            events, count, total = R.get_epg(channel,start=0,limit=2)
            print events
            if channel: print "Aktueller Kanal: %s"%(channel)
            if playing: print "Spiele: %s"%(playing)
            try:
                print "Now playing: %s" %(events[0]['title'])
            except:
                print "Channel %s has no epg"%channel
        time.sleep(0.25)
        #time.sleep(0.5)
        if os.name == "posix":
            os.system('clear')
        if os.name in ("nt","dos","ce"):
            os.system('CLS')
