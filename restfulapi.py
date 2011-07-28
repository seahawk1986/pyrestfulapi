#!/usr/bin/env python
# coding: utf-8

#   This is a python-module to access informations using VDR's RESTFULAPI plugin.
#   Copyright (C) 2011  by Alexander Grothe <alexandergrothe@gmx.de>
#
#   This program is free software: you can redistribute it and/or modify
#   it under the terms of the GNU General Public License as published by
#   the Free Software Foundation, either version 3 of the License, or
#   (at your option) any later version.
#
#   This program is distributed in the hope that it will be useful,
#   but WITHOUT ANY WARRANTY; without even the implied warranty of
#   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#   GNU General Public License for more details.
#
#   You should have received a copy of the GNU General Public License
#   along with this program.  If not, see <http://www.gnu.org/licenses/>.

# TODO: POST and DELETE commands

import urllib
import urllib2
from lxml import etree

class RestfulAPI:

    def __init__(self,ip="127.0.0.1", port="8002"):
        self.ip = ip
        self.port = port
        self.channels = []
        self.base_url = "http://%s:%s/"%(self.ip,self.port)

    def get_elements(self,req_url):
            xmltree = etree.fromstring(urllib2.urlopen(req_url).read())
            raw_elements = xmltree.getchildren()
            return raw_elements

    def get_list(self,raw_elements,xml_str=None,keyword=None):    
            entry_list = []    
            for entry in raw_elements:
                if entry.tag == "{http://www.domain.org/restfulapi/2011/%s-xml}%s"%(xml_str,keyword):
                    paramdict = {}
                    if len(entry.getchildren())>0:
                        for param in entry.getchildren():
                            paramdict[param.values()[0]]=param.text
                        # stores elements in a list, as list containing [ {Properties as dict} ]
                        entry_list.append(paramdict)
                    else:
                        entry_list.append(entry.text)
                        
                if entry.tag == "{http://www.domain.org/restfulapi/2011/%s-xml}count"%(xml_str):
                    count = int(entry.text)
                    #print "Counted "+entry.text+" elements."                         
                if entry.tag == "{http://www.domain.org/restfulapi/2011/%s-xml}total"%(xml_str):
                    total = int(entry.text)
                    #print "Total "+entry.text+" elements."
            return entry_list, count, total           

    def get_list(self,cat=None,arg="",start=0,limit=0):

        if cat == "channels":
            req_url = "%s%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "channel":
            req_url = "%s/channels/%s.xml"%(self.base_url,arg)
            xml_str = "channels"
            keyword = "channel"
            
        if cat == "groups":
            req_url = "%schannels/%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "groups"
            keyword = "group"
        if cat == "group":
            req_url = "%schannels.xml?%s=%s&start=%s&limit=%s"%(self.base_url,cat,arg,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "timers":
            req_url = "%s%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "timers"
            keyword = "timer"
        if cat == "timer":
            req_url = "%stimers/%s.xml"%(self.base_url,arg)
            xml_str = "timers"
            keyword = "timer"

        if cat == "recordings":
            req_url = "%srecordings.xml"%(self.base_url)
            xml_str = "recordings"
            keyword = "recording"
        
        elementlist = []

        elementlist, count, total = self.get_list(get_elements(req_url),xml_str,keyword)
        return elementlist, count, total

    def get_channels(self,start=0,limit=0):
        channel_list, count, total = self.get_list(cat="channels",start=start,limit=limit)         
        return channel_list, count, total

    def get_channel(self,channel_id=None):
        if channel_id != None:
            channel_list, count, total = self.get_list(cat="channel",arg=channel_id)
        else:
            channel_list = []
            count = 0
            total = 0
        return channel_list, count, total
                
    def get_groups(self,start=0,limit=0):
        channel_list, count, total = self.get_list(cat="groups",start=start,limit=limit)
        return groups_list, count, total

    def get_group_channels(self,group=None,start=0,limit=0):
        if group != None:
            group = urllib.quote(group)
            channel_list, count, total = self.get_list(cat="group",arg=group,start=start,limit=limit)
        else:
            channel_list = []
            count = 0
            total = 0
        return channel_list, count, total

    def get_timers(self,start=0,limit=0):
        timer_list, count, total = self.get_list(cat="timers",start=start,limit=limit) 
        return timer_list, count, total

    def get_timer(self,timer_id=None):
        if timer_id != None:
            timer_list, count, total = self.get_list(cat="timer",arg=timer_id) 
        else:
            timer_list = []
            count = 0
            total = 0            
        return timer_list, count, total

    def get_recordings(self):
        rec_list, count, total = self.get_list(cat="recordings") 
        return rec_list, count, total

    def get_info(self):
        cat = "info"
        req_url = "%s%s.xml"%(self.base_url,cat)
        xml_str = "info"
        keyword = "channel"
        raw_elements = self.get_elements(req_url)
        for entry in raw_elements:
            if entry.tag == "{http://www.domain.org/restfulapi/2011/%s-xml}%s"%(xml_str,keyword):
                channel = entry.text
                video = None
            if entry.tag == "{http://www.domain.org/restfulapi/2011/%s-xml}%s"%(xml_str,"video"):
                channel = None
                video = entry.text
        return channel, video
