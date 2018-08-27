#  Filename: FP_TranslatorRestAPI.py
# 
#  Copyright 2016  Kenny Gilfilen.  All Rights Reserved
# 
#  Revision History: 
#   Nov 28, 2016 - added ability to track elapsed time, and the 
#                  getElapsedTime() method, cleaned module up some
#   Dec 22, 2016 - added new translator (url) due to running out of space on the old one.
#
#  Future needs:
#   change from pycurl to python requests lib
#   change from elementTree to lxml lib

import sys
import datetime
import time
from io import BytesIO
import xml.etree.ElementTree as ET

import pycurl


class FP_TranslatorRestAPI:

    logLevel = 1
    translatorUrl = 'http://oldTranslator.com:8580/translator/services/FormatBuilder'
    translatorUrl = 'http://newTranslator.com:8380/translator/services/FormatBuilder'


	# Mostly flight plans will be passed in as xml strings in inString
    def __init__(self, inFile = None, outFile=None, url=None, inString = None):
    
        if url is None:
           self.url = FP_TranslatorRestAPI.translatorUrl
        else:
            self.url = url
       
        if inFile is None:
            if inString is None: 
                self.log("No input translator message given, stopping FP_TranslatorRestAPI",1)
                sys.exit()
            else:
                self.EF_req_data = inString
        else:
            self.inFile = inFile
            with open(self.inFile) as inFileH:
                self.EF_req_data = inFileH.read()
                inFileH.close()
        
        # gets outFile squared away
        if outFile is not None:
            self.outFile = outFile

        self.buffer = BytesIO()
        headers = 'SOAPAction: Header|Accept: application/json'
        self.hdrs = headers.split("|")

        self.soapEnv = '''<?xml version="1.0" encoding="UTF-8"?>
        <soapenv:Envelope xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/" xmlns:xsd="http://www.w3.org/2001/XMLSchema" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">
         <soapenv:Body>%s</soapenv:Body>
        </soapenv:Envelope>'''

        self.body = self.soapEnv % self.EF_req_data
        self.elapsed_time = None

    # returns the translator rquest message as string, no soap envelope
    def getEF003_ReqBody(self):
        return self.EF_req_data
        
    def getElapsedTime(self):
        return self.elapsed_time
    
    # sets the translator request message, and puts in soap envelope
    def setBody(self,body):
        self.body = self.soapEnv % body
       
    def setBodyFromFile(self,inFile):
        with open(self.inFile) as inFileH:
            body = inFileH.read()
            inFileH.close()
        self.body = self.soapEnv % body
    
    def writeRespToFile(self,body=None,respFile=None):
        if body is None:
            print("FP_TranslatorRestAPI: message body not included with Write request.")
            return 
        if respFile is None:
            print("FP_TranslatorRestAPI: new file name not included with Write request.")
            return 
        with open(respFile,'w') as outFileH:
            outFileH.write(body)
            outFileH.close()
    
    def sendFlightPlan(self):
        # sets up curl object
        c = pycurl.Curl()
        c.setopt(pycurl.HTTPHEADER, self.hdrs)
        c.setopt(pycurl.POST, 1)
        c.setopt(pycurl.VERBOSE, 1)
        c.setopt(pycurl.URL, self.url)
        c.setopt(pycurl.POSTFIELDS, self.body)
        c.setopt(c.WRITEDATA, self.buffer)
        # sets up holder for curl command response
        self.buffer.truncate(0)
        self.buffer.seek(0)
        # runs the curl command

        sent_time = time.time()
        c.perform()
        self.elapsed_time = time.time() - sent_time
        status = c.getinfo(pycurl.RESPONSE_CODE)
        if status != 200: 
            self.log( "\n***** PYCURL HTTP STATUS CODE: %d *****\n" % status,2)
        del c
        # extracts the response as string, from the soap envelope 
        result = self.buffer.getvalue().decode('iso-8859-1')
        body = result[result.find("<xml_Flight_Plan"):]
        body = body[:body.find("</soapenv:Body>")]
        # writes the EF003 response as a file locally for someone to play with
        # if we didn't get a response, this writes the sent body to the file.
        # returns the EF003 response to the user As String
        return body

    def log(self, text, level= 5):
        if FP_TranslatorRestAPI.logLevel >= level:
            print(text)