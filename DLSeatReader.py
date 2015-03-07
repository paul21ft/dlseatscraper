"""
DL Seat Reader Script
Copyright by paul21 @ flyertalk.com
Free for personal use only

V0.1: Initial seat reading complete for DL

Planned:
Periodic seat alerts
"""

import urllib
import urllib2
import sys, httplib
from StringIO import StringIO
import gzip
import Cookie
from collections import defaultdict

"""
Prep:
Install python 2:
https://www.python.org/downloads/ , get 2.7.9 or similar
When installing, enable the feature "Add python to command line"
Windows key + R , "cmd" , enter to get black command box
cd c:\path\to\my\pythonfiles
python

Then you get a prompt like
>>>
then type the sequence below, copy/paste (by right click on box)
>>>exit()
will quit the python cmd

Test sequence:
from DLSeatReader import DLSeatReader
DLSR=DLSeatReader()
DLSR.setFlightInfo("DL",110,"ATL","LAX","22Apr")
seatUrl=DLSR.createSeatUrl()
DLSR.prepCookie(seatUrl)
reqStr=DLSR.createSeatDataString(seatUrl)
seatData=DLSR.loadSeatDataString(reqStr)
seatInfo=DLSR.parseSeatDataString(seatData)
DLSR.prettyPrintSeats(seatInfo)
"""

class DLSeatReader:
	def __init__(self):
		self.mainUrl='http://www.delta.com'
	
	def prepCookie(self,seatUrl):
		#First start a session
		req = urllib2.Request(self.mainUrl)
		response = urllib2.urlopen(req) 
		new_cookie=response.info().getheader('Set-Cookie')
		C=Cookie.SimpleCookie()
		C.load(new_cookie)
		jsesid=C["JSESSIONID"].value
		cookie_out=C.output(attrs="httponly",header="",sep=";")
		cookie_out=cookie_out + ';'
		
		#Next, view a seat page once to init the DWR session
		req = urllib2.Request(self.mainUrl + seatUrl);
		req.add_header('Cookie',cookie_out)
		response = urllib2.urlopen(req) 
		new_cookie2=response.info().getheader('Set-Cookie')
		C2=Cookie.SimpleCookie(new_cookie2)
		C["cohrISMSessID"]=C2["cohrISMSessID"].value
		C["TLTHID"]=C2["TLTHID"].value
		cookie_out=C.output(attrs="httponly",header="",sep=";")
		cookie_out=cookie_out + ';'
		
		#Save the prepared cookie
		self.cookie_out=cookie_out;
		#Save the jsesid for request string to DWR
		self.jsesid=jsesid
		
	def setFlightInfo(self,flightCarrier,flightNum,flightOrig,flightDest,flightDate):
		self.flightInfo={}
		self.flightInfo["NUM"]=str(flightNum)
		self.flightInfo["ORG"]=flightOrig
		self.flightInfo["DST"]=flightDest
		self.flightInfo["DATE"]=flightDate
		self.flightInfo["CARRIER"]=flightCarrier
	
	def createSeatUrl(self):
		turl='/ism/SeatMapDisplay.action?cmd=LSM&commandContext=na?1?1&flightSegment=1?1?'
		
		turl += self.flightInfo["NUM"] + '?Y?'
		turl += self.flightInfo["ORG"] + '?'
		turl += self.flightInfo["DATE"] + '?'
		turl += '12:01pm?'
		turl += self.flightInfo["DST"] + '?'
		turl += self.flightInfo["DATE"] + '?'
		turl += '12:02pm?0?PREFERRED_PARTY'
		
		return turl
	
	def createSeatDataString(self,seatUrl):
		tstr='callCount=1\npage='+seatUrl+'\nhttpSessionId='+self.jsesid+'\nscriptSessionId=0\nc0-scriptName=SeatMap\nc0-methodName=getLiveSeatMap\nc0-id=0\nc0-param0=string:'
		tstr += self.flightInfo["NUM"]
		tstr += '\nc0-param1=string:' + self.flightInfo["ORG"]
		tstr += '\nc0-param2=string:' + self.flightInfo["DST"]
		tstr += '\nc0-param3=string:' + self.flightInfo["DATE"]
		tstr += '\nc0-param4=string:null\nc0-param5=string:null\nc0-param6=string:null\nc0-param7=string:null\nc0-param8=number:0\n'
		tstr += 'c0-param9=string:' + self.flightInfo["CARRIER"]
		tstr += '\nc0-param10=string:null\nc0-param11=string:0\nc0-param12=boolean:false\nbatchId=0\n'
		
		return tstr
	
	def loadSeatDataString(self,reqStr):
		webservice = httplib.HTTP('www.delta.com')
		webservice.putrequest("POST", '/ism/dwr/call/plaincall/SeatMap.getLiveSeatMap.dwr')
		webservice.putheader("Host", 'www.delta.com')
		webservice.putheader("User-Agent","Mozilla/5.0 (Windows NT 6.1; WOW64; rv:34.0) Gecko/20100101 Firefox/34.0")
		webservice.putheader("Accept","text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8")
		webservice.putheader("Accept-Encoding","gzip, deflate")
		webservice.putheader("Referrer","http://www.delta.com")
		webservice.putheader("Content-type", "text/plain; charset=UTF-8")
		webservice.putheader("Content-length", "%d" % len(reqStr))
		webservice.putheader("Cookie",self.cookie_out)
		webservice.endheaders()
		webservice.send(reqStr)
		statuscode, statusmessage, header = webservice.getreply()
		result = webservice.getfile().read()
		rbuf=StringIO(result)
		f=gzip.GzipFile(fileobj=rbuf)
		uncomdata=f.read()
		return uncomdata
	
	def parseSeatDataString(self,dataStr):
		splitData=dataStr.split(';')
		seatInfo=defaultdict(lambda : defaultdict(str))
		varInfo=defaultdict(lambda : defaultdict(str))
		for i in range(len(splitData)):
			tstr=splitData[i]
			strSplit=tstr.split('=')
			if len(strSplit) == 1:
				continue
			varName=strSplit[0]
			varData=strSplit[1]
			varPrefix=varName.split('.')
			if len(varPrefix) > 1:
				varInfo[varPrefix[0]][varPrefix[1]]=varData.strip('"')
			
			if len(varPrefix) > 1 and varPrefix[1] == 'seat':
				seatName=varData.strip('"')
				seatInfo[seatName]['varid']=varPrefix[0]


		for key,value in seatInfo.iteritems():
			seatName=key
			varid=seatInfo[seatName]['varid']
			seatParams=varInfo[varid]
			for tkey,tvalue in seatParams.iteritems():
				seatInfo[seatName][tkey]=tvalue

		return seatInfo
	
	def prettyPrintSeats(self,seatInfo):
		openstr='O'
		ecstr='E'
		preferredstr='P'
		unavail='X'
		varSeatLetters=['A','B','C','D','E','F','G','H','I','J','K']
		maxRowNum=500
		pstr='FLIFO: %s, %s, %s, %s\n\n' % (self.flightInfo["CARRIER"]+self.flightInfo["NUM"],self.flightInfo["ORG"],self.flightInfo["DST"],self.flightInfo["DATE"])
		for i in range(maxRowNum):
			rstr=''
			rempty=1
			for j in range(len(varSeatLetters)):
				tsname=str(i+1)+varSeatLetters[j]
				tsi=seatInfo[tsname]
				if len(tsi) == 0:
					rstr += '  '
					continue
				rempty=0
				if tsi['seatAvailable'] == 'true':
					rstr += openstr + ' '
				else:
					rstr += unavail + ' '
				
			if rempty == 0:
				rowname = '%2d' % (i+1)
				pstr += rowname + ': ' + rstr + '\n'

		print pstr
	
