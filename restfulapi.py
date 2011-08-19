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

# TODO: POST, PUT and DELETE commands (searchtimer, search)
#       ERROR handling (connection, double timers etc.)
#       EPG search -> HOWTO search quoted strings, regex (missing feature in plugin)
#       searchtimer
#       download channel images
#       infos (used versions and plugins)
#       OSD - relative navigation by defining element to be selected or activated, wrapper to input of Text/IPs

import urllib
import urllib2
from lxml import etree
import httplib
import simplejson
import re

class HttpClient:
    ''' Collection of all needed HTTP-Request methods'''
    def __init__(self):
        redirect_handler= urllib2.HTTPRedirectHandler()
        self._opener = urllib2.build_opener(redirect_handler)

    def GET(self, url):
        return self._opener.open(url).read()

    def POST(self, url,parameters):
        return self._opener.open(url, urllib.urlencode(parameters)).read()

    def POST_raw(self, url, parameters):
        return self._opener.open(url, parameters).read()

    def POST_json(self, url, parameters):
        print simplejson.dumps(parameters)
        return self._opener.open(url, simplejson.dumps(parameters)).read()

    def PUT(self, url="",body='',header='HTTP/1.1'):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        body
        request = urllib2.Request(url, body)
        request.add_header('Content-Type', header)
        request.get_method = lambda: 'PUT'
        return opener.open(request).read()

    def DELETE(self, url="",header='HTTP/1.1'):
        opener = urllib2.build_opener(urllib2.HTTPHandler)
        request = urllib2.Request(url)
        request.add_header('Content-Type', header)
        request.get_method = lambda: 'DELETE'
        return opener.open(request).read()


class RestfulAPI:
    ''' Provides access to functions of VDR's restfulapi-plugin'''

    def __init__(self,ip="127.0.0.1", port="8002"):
        self.ip = ip
        self.port = port
        self.channels = []
        self.base_url = "http://%s:%s"%(self.ip,self.port)
        self.channels, self.count, self.total = self.get_channels()
        self.HTTP = HttpClient()
        self.JSON = simplejson.JSONDecoder()

    def get_elements(self,req_url): 
        '''extracts elements from xml source'''
        xmltree = etree.fromstring(urllib2.urlopen(req_url).read())
        raw_elements = xmltree.getchildren()
        return raw_elements

    def get_entrys(self,raw_elements,xml_str=None,keyword=None):   
        '''creates a list of elements matching keyword, number of elements, total elements
           as helpe fuction for get_list'''
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
        '''returns a touple of elements as (list, count, total)'''

        if cat == "channels":
            req_url = "%s/%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "channel":
            req_url = "%s/channels/%s.xml"%(self.base_url,arg)
            xml_str = "channels"
            keyword = "channel"
            
        if cat == "groups":
            req_url = "%s/channels/%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "groups"
            keyword = "group"
        if cat == "group":
            req_url = "%s/channels.xml?%s=%s&start=%s&limit=%s"%(self.base_url,cat,arg,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "timers":
            req_url = "%s/%s.xml?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "timers"
            keyword = "timer"
        if cat == "timer":
            req_url = "%s/timers/%s.xml"%(self.base_url,arg)
            xml_str = "timers"
            keyword = "timer"

        if cat == "recordings":
            req_url = "%s/recordings.xml"%(self.base_url)
            xml_str = "recordings"
            keyword = "recording"
        
        elementlist = []
        elementlist, count, total = self.get_entrys(self.get_elements(req_url),xml_str,keyword)
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

    def get_channel_by_number(self, number=None):
        ret_ch = None
        if number != None:
            number = int(re.sub("[^0-9]", "",number))
            if number > 0:
                channel_list,count,total = self.get_category(cat="channels")
                for channel in channel_list:
                    if channel['number'] == number:
                        ret_ch = channel
                        break
            
        return ret_ch

                
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

    def delete_recording(self, rec_number=None):
        if rec_number != None:
            url = "%s/recording/%s"%(self.base_url,rec_number)
            return self.HTTP.DELETE(url)
        

    def get_playing(self):
        cat = "info"
        req_url = "%s/%s.xml"%(self.base_url,cat)
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

    def get_info(self):
        cat = "info"
        req_url = "%s/%s.json"%(self.base_url,cat)
        xml_str = "info"
        keyword = "channel"
        info = self.JSON.decode(self.HTTP.GET(req_url))
        try:
            channel = info['channel']
        except:
            channel = None
        try:
            video = info['video']
        except:
            video = None
        finally:
            return [channel, video]

    def get_channel_image_url(self, channel_id=None, name=None):
        url = ''
        for channel in self.channels:
            if (channel['channel_id'] == channel_id) or (channel['name'] == name):
                if channel['image'] == 'true':
                    url = "%s/channels/image/%s"%(self.base_url,channel['channel_id'])   
                    break    
        return url

    def switch_to_channel(self, channel_id=None, name=None):
        url=''
        for channel in self.channels:
            if channel_id != None:
                if (channel['channel_id'] == channel_id) or (channel['name'] == name):
                    client = HttpClient()
                    ignored_html = self.HTTP.POST("%s/remote/switch/%s"%(self.base_url,channel_id), {})
        return "Switched to %s"%(channel_id)

    def send_remote(self, command):
        '''Supported Commands: "Up", "Down", "Menu", "Ok", "Back", "Left", "Right", "Red", "Green", "Yellow", "Blue",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Info", "Play", "Pause", "Stop", "Record",
            "FastFwd", "FastRew", "Next", "Prev", "Power", "ChanUp", "ChanDn", "ChanPrev", "VolUp", "VolDn",
            "Mute", "Audio", "Subtitles", "Schedule", "Channels", "Timers", "Recordings", "Setup", "Commands",
            "User0", "User1", "User2", "User3", "User4", "User5", "User6", "User7", "User8", "User9", "None", "Kbd"'''
        valid_commands=["Up", "Down", "Menu", "Ok", "Back", "Left", "Right", "Red", "Green", "Yellow", "Blue",
            "0", "1", "2", "3", "4", "5", "6", "7", "8", "9", "Info", "Play", "Pause", "Stop", "Record",
            "FastFwd", "FastRew", "Next", "Prev", "Power", "ChanUp", "ChanDn", "ChanPrev", "VolUp", "VolDn",
            "Mute", "Audio", "Subtitles", "Schedule", "Channels", "Timers", "Recordings", "Setup", "Commands",
            "User0", "User1", "User2", "User3", "User4", "User5", "User6", "User7", "User8", "User9", "None", "Kbd"]
        client = HttpClient()
        ignored_html = self.HTTP.POST("%s/remote/%s"%(self.base_url,command), {})

    def create_timer(self, params={'file':'Test','flags':'1','start':'1200','stop':'1215','day':'2099-08-08','channel':'T-8468-12290-32','weekdays':'-------'}):
        ignored_html = self.HTTP.POST("%s/timers"%(self.base_url), params)

    def create_timer_dict(self, filename='Test', flags='1', start='1200', stop='1215', day='2099-08-08',channel='T-8468-12290-32',weekdays='-------'):
        '''creates a dictionary containung all needed elements to create a timer with create_timer(dictionary)
            please take care to provide ALL needed elements'''
        timerdict = {}
        timerdict['file']=filename
        timerdict['flags']=flags
        timerdict['start']=start
        timerdict['stop']=stop
        timerdict['day']=day
        timerdict['channel']=channel
        timerdict['weekdays']=weekdays
        return timerdict

    def update_timer(self, timer_id, params={}):
        '''updates parameters of an existing timer, needs 'timer_id' which is called 'id' in timer lists aquired by get_timers()'''
        url = "%s/timers.json"%self.base_url
        params['timer_id']=timer_id
        json = simplejson.dumps(params)
        print params
        ignored_html = self.HTTP.PUT(url, json)

    def remove_timer(self, timer_id):
        url = "%s/timers/%s"%(self.base_url,timer_id)
        ignored_html = self.HTTP.DELETE(url)

    def get_category(self,cat=None,arg="",start=0,limit=0):
        '''get tuple of category entries as (dictionary, number of found entries, total number)
           allowed categories: channels, channel [arg="<channel name>"], groups, group [arg="<groupname>"],
           timers, timer [arg="<timer name>"], recordings
           use start=n to begin with n-th entry and limit=m to recieve m entries.
           This function is supposed to replace get_elements(), get_entrys() and get_list() some day'''
        try:
            start = int(start)
        except:
            print "start has to be an integer"

        try:
            limit = int(limit)
        except:
            print "limit has to be an integer"

        if cat == "channels":
            req_url = "%s/%s.json?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "channel":
            req_url = "%s/channels/%s.json"%(self.base_url,arg)
            xml_str = "channels"
            keyword = "channel"
            
        if cat == "groups":
            req_url = "%s/channels/%s.json?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "groups"
            keyword = "group"
        if cat == "group":
            req_url = "%s/channels.json?%s=%s&start=%s&limit=%s"%(self.base_url,cat,arg,start,limit)
            xml_str = "channels"
            keyword = "channel"

        if cat == "timers":
            req_url = "%s/%s.json?start=%s&limit=%s"%(self.base_url,cat,start,limit)
            xml_str = "timers"
            keyword = "timer"
        if cat == "timer":
            req_url = "%s/timers/%s.json"%(self.base_url,arg)
            xml_str = "timers"
            keyword = "timer"

        if cat == "recordings":
            req_url = "%s/recordings.json"%(self.base_url)
            xml_str = "recordings"
            keyword = "recording"

        if cat == "events":
            xml_str = "events"
            if arg:
                req_url = "%s/%s/%s/0.json?start=%s&limit=%s"%(self.base_url,cat,arg,start,limit)
            
                #print req_url
                
            else:
                json = {"count":0, "total":0}

        json = self.JSON.decode(self.HTTP.GET(req_url))
        return json[xml_str], json['count'], json['total']

    def get_epg(self, channel_id=None, start=0, limit=0):
        try:
            events, count, total = self.get_category(cat="events",arg=channel_id,start=start,limit=limit)
        except:
            events = {}
            count = 0
            total = 0
    
        finally:        
            return events, count, total
        

    def epg_search(self, args={"query":"","mode":0}, limit=0, start=0):
        req_url = "%s/events/search.json?start=%s&limit=%s"%(self.base_url,start,limit)
        json = self.JSON.decode(self.HTTP.POST_json(req_url,args))
        return json['events'], json['count'], json['total']

    def create_search_dict(self, query="",mode=0,channel_id="",use_title="true",use_subtitle="false",use_description="false"):
        search_dict = {}
        search_dict["query"] = query
        search_dict["mode"] = mode
        search_dict["channel_id"] = channel_id
        search_dict["use_title"] = use_title
        search_dict["use_subtitle"] = use_subtitle
        search_dict["use_description"] = use_description

    def get_osd(self):
        url = "%s/osd.json"%(self.base_url)
        return_val = {'red':None,'yellow':None,'green':None,'blue':None,'title':None,'channel':None,'items':[]}
        try:
            osd = self.JSON.decode(self.HTTP.GET(url))
        except:
            osd = None
            return [osd,return_val]
        

        if osd.has_key('ChannelOsd'):
            channel_number, channel_name = re.split("\s*",osd['ChannelOsd'],1)
            return_val['channel']=self.get_channel_by_number(channel_number)
            print "Now Playing: ",self.get_channel_by_number(channel_number)

        if osd.has_key('ProgrammeOsd'):

                return_val['title'] = "Now and next:"
                for key in osd['ProgrammeOsd'].keys():

                    return_val['items'].append([key,osd['ProgrammeOsd'][key],False]) 

        
        if (osd.has_key('TextOsd')) and (len(osd['TextOsd']['items']) > 0):
            
            return_val['red'] = osd['TextOsd']['red']
            return_val['yellow'] = osd['TextOsd']['yellow']
            return_val['green'] = osd['TextOsd']['green']
            return_val['blue'] = osd['TextOsd']['blue']
            return_val['title'] = osd['TextOsd']['title']
            
            # check if "normal" OSD menu is displayed (navigation by numbers is possible)
            if re.match("^[0-9]{1,}\s*\w*", osd['TextOsd']['items'][0]['content'].lstrip()):
                #print "Schema: <Nummer> <Eintrag>"
                for item in osd['TextOsd']['items']:
                    number, value = re.split("\s*",item['content'].lstrip(),1)
                    #print number,value
                    return_val['items'].append([number,value,item['is_selected']])
            # check if normal navigation as in EPG
            elif re.match("^\w{1,}\s*.*[0-9]{2}:[0-9]{2}",osd['TextOsd']['items'][0]['content'].lstrip()):

                for item in osd['TextOsd']['items']:
                    print item['content']
                    return_val['items'].append(["",item['content'],item['is_selected']])
                    pass                

            elif re.match("^\w{1,}.*:",osd['TextOsd']['items'][0]['content'].lstrip()):

                for item in osd['TextOsd']['items']:
                    if item['is_selected'] == True:
                        if re.match("^.*:.*[.*].*",item['content']):
                            print "Editing value %s"%(item['content'])
                    return_val['items'].append(["",item['content'],item['is_selected']])

            else:
                for item in osd['TextOsd']['items']:
                    if item['is_selected'] == True:
                        if re.match("^.*:.*[.*].*",item['content']):
                            print "Editing value %s"%(item['content'])
                    return_val['items'].append(["",item['content'],item['is_selected']])

        elif (osd.has_key('TextOsd')) and (len(osd['TextOsd']['items']) == 0):
            
            return_val['red'] = osd['TextOsd']['red']
            return_val['yellow'] = osd['TextOsd']['yellow']
            return_val['green'] = osd['TextOsd']['green']
            return_val['blue'] = osd['TextOsd']['blue']
            return_val['title'] = osd['TextOsd']['title']
                    
                    
        return [osd, return_val]

        
        
        


