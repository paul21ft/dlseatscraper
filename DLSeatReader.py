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
DLSR.setFlightInfo("DL",110,"ATL","LAX","22Apr","09 APR 2015")
seatUrl=DLSR.createSeatUrl()
DLSR.prepCookie(seatUrl)
reqStr=DLSR.createSeatDataString2(seatUrl)
seatData=DLSR.loadSeatDataString2(reqStr)
seatInfo=DLSR.parseSeatDataString2(seatData)
DLSR.prettyPrintSeats2(seatInfo)
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
		
	def setFlightInfo(self,flightCarrier,flightNum,flightOrig,flightDest,flightDate, flightDateLong):
		self.flightInfo={}
		self.flightInfo["NUM"]=str(flightNum)
		self.flightInfo["ORG"]=flightOrig
		self.flightInfo["DST"]=flightDest
		self.flightInfo["DATE"]=flightDate
		self.flightInfo["CARRIER"]=flightCarrier
		self.flightInfo["LONGDATE"]=urllib.quote(flightDateLong, '')
	
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
	
	def createSeatDataString2(self,seatUrl):
		tstr='callCount=1\n'
		tstr += 'page=/seat/RetrieveLSMAction\n'
		tstr += 'httpSessionId='+self.jsesid+'\nscriptSessionId=0\n'
		tstr += 'c0-scriptName=SeatMapGUIDWR\n'
		tstr += 'c0-methodName=retrieveLogicalSeatMapDWR\n'
		tstr += 'c0-id=0\n'
		tstr += 'c0-e2=boolean:false\n'
		tstr += 'c0-e3=string:' + self.flightInfo["CARRIER"] + '\n'
		tstr += 'c0-e4=boolean:false\nc0-e5=boolean:false\nc0-e6=boolean:false\nc0-e7=boolean:false\nc0-e8=boolean:false\n'
		
		tstr += 'c0-e9=string:' + self.flightInfo["DST"] + '\n'
		
		tstr += 'c0-e10=string:' + self.flightInfo["LONGDATE"] + '\n'
		#Time seems unimportant
		tstr += 'c0-e11=string:08%2030%20A\n'
		
		tstr += 'c0-e12=boolean:false\nc0-e13=string:\nc0-e14=string:Y\nc0-e15=string:\nc0-e16=boolean:false\nc0-e17=string:\nc0-e18=string:\nc0-e19=boolean:false\nc0-e20=boolean:false\nc0-e21=string:\n'
		
		tstr += 'c0-e22=string:' + self.flightInfo["ORG"] + '\n'
		tstr += 'c0-e23=string:' + self.flightInfo["LONGDATE"] + '\n'
		#Time seems unimportant
		tstr += 'c0-e24=string:07%2000%20A\n'
		
		tstr += 'c0-e25=boolean:false\nc0-e26=boolean:false\nc0-e27=boolean:false\nc0-e28=string:\nc0-e29=string:\nc0-e30=string:\nc0-e31=string:\n'
		
		tstr += 'c0-e32=string:' + self.flightInfo["NUM"] + '\n'

		tstr += 'c0-e33=string:\nc0-e34=string:\nc0-e35=boolean:false\nc0-e36=string:\nc0-e37=string:\nc0-e38=boolean:false\nc0-e39=string:\nc0-e40=string:\nc0-e41=string:\nc0-e42=string:\nc0-e43=string:\nc0-e44=string:\nc0-e45=string:\nc0-e46=string:\nc0-e47=string:\nc0-e48=boolean:false\nc0-e49=boolean:false\nc0-e50=string:\nc0-e51=boolean:false\nc0-e1=Object_Object:{ETicketPresent:reference:c0-e2, airlineCode:reference:c0-e3, airportGateCheckInProgress:reference:c0-e4, allFlightsDeparted:reference:c0-e5, allowSeatForOACodeshare:reference:c0-e6, allowSeatSelForOa:reference:c0-e7, allowSeatSelectionForKL:reference:c0-e8, arrivalCity:reference:c0-e9, arrivalDate:reference:c0-e10, arrivalTime:reference:c0-e11, basicEconomyDisplayFlag:reference:c0-e12, category:reference:c0-e13, classOfServiceCode:reference:c0-e14, classOfServiceDescription:reference:c0-e15, cleanedFlag:reference:c0-e16, codeshareAirlineName:reference:c0-e17, currentActionCode:reference:c0-e18, decontentedFlight:reference:c0-e19, departedFlight:reference:c0-e20, departureArrivalCityName:reference:c0-e21, departureCity:reference:c0-e22, departureDate:reference:c0-e23, departureTime:reference:c0-e24, displayStaticSeatMap:reference:c0-e25, dlConnectionCarrier:reference:c0-e26, economyCabinOnly:reference:c0-e27, equipmentCode:reference:c0-e28, equipmentType:reference:c0-e29, equipmentUrl:reference:c0-e30, flightInfoIndex:reference:c0-e31, flightNumber:reference:c0-e32, flightTime:reference:c0-e33, flightType:reference:c0-e34, groundHandled:reference:c0-e35, groundHandledBy:reference:c0-e36, imageUrl:reference:c0-e37, iropProtectedBlock:reference:c0-e38, iropTripType:reference:c0-e39, iropType:reference:c0-e40, itineraryDestination:reference:c0-e41, itineraryOrigin:reference:c0-e42, legId:reference:c0-e43, marketingAirlineCode:reference:c0-e44, operatingAirline:reference:c0-e45, operatingFlightNumber:reference:c0-e46, segmentNumber:reference:c0-e47, standbyFlag:reference:c0-e48, transconFlight:reference:c0-e49, type:reference:c0-e50, withinCheckInWindow:reference:c0-e51}\nc0-param0=Array:[reference:c0-e1]\nc0-param1=string:1\nc0-param2=string:USD\nc0-param3=boolean:true\nc0-param4=string:SHOPPING\nbatchId=0'
		
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
	
	def loadSeatDataString2(self,reqStr):
		webservice = httplib.HTTP('www.delta.com')
		webservice.putrequest("POST", '/seat/dwr/call/plaincall/SeatMapGUIDWR.retrieveLogicalSeatMapDWR.dwr')
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
		
		self.varInfo=varInfo
		return seatInfo
	
	def parseSeatDataString2(self,dataStr):
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
			
			seatName=varData.strip('"')
			if len(varPrefix) > 1 and varPrefix[1] == 'id' and seatName != 'null':
				seatInfo[seatName]['varid']=varPrefix[0]


		for key,value in seatInfo.iteritems():
			seatName=key
			varid=seatInfo[seatName]['varid']
			seatParams=varInfo[varid]
			for tkey,tvalue in seatParams.iteritems():
				seatInfo[seatName][tkey]=tvalue
				if tkey == 'seat':
					tparam=varInfo[tvalue]
					for tpkey,tpvalue in tparam.iteritems():
						if tpkey != 'id':
							seatInfo[seatName][tpkey]=tpvalue
		
		
		self.varInfo=varInfo
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
		
	def prettyPrintSeats2(self,seatInfo):
		openstr='O'
		ecstr='E'
		preferredstr='P'
		unavail='X'
		blockstr='B'
		varSeatLetters=['A','B','C','D','E','F','G','H','I','J','K']
		maxRowNum=500
		pstr='FLIFO: %s, %s, %s, %s\n' % (self.flightInfo["CARRIER"]+self.flightInfo["NUM"],self.flightInfo["ORG"],self.flightInfo["DST"],self.flightInfo["DATE"])
		pstr+='O-Open X-Occupied B-Blocked\n Row: A B C D E F G...\n\n'
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
				if tsi['blocked'] == 'true':
					rstr += blockstr + ' '
				elif tsi['available'] == 'true':
					rstr += openstr + ' '
				else:
					rstr += unavail + ' '
				
			if rempty == 0:
				rowname = '%2d' % (i+1)
				pstr += rowname + ': ' + rstr + '\n'

		print pstr
	
