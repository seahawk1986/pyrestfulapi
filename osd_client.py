#!/bin/env python
# * coding: utf-8 *

import time
import restfulapi
import os
import datetime

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
            #print "No OSD, fetching epg for now and next:"
            channel, playing =  R.get_info()
            events, count, total = R.get_epg(channel,start=0,limit=2)
            
            if channel: 
                chan, c, t = R.get_channel(channel)
                title = "%s"%(chan[0]['name'])
                
                try:
                    now = "%s\t%s\n\t%s" %(datetime.datetime.fromtimestamp(events[0]['start_time']).strftime("%H:%M"),events[0]['title'],events[0]['short_text'])
                    next = "%s\t%s\n\t%s" %(datetime.datetime.fromtimestamp(events[1]['start_time']).strftime("%H:%M"),events[1]['title'],events[1]['short_text'])
                    
                except: 
                    print "Channel %s has no epg"%channel
                    now = ''
                    next = ''
                finally:
                    width = max(len(title),len(now),len(next))
                    print title
                    print "-"*width
                    print now
                    print "-"*width
                    print next
                    

            elif playing: print "Playing Recording: %s"%(playing)
            else:
                "Nothing to show!"
            #print events
        time.sleep(0.25)
        #time.sleep(0.5)
        if os.name == "posix":
            os.system('clear')
        if os.name in ("nt","dos","ce"):
            os.system('CLS')
