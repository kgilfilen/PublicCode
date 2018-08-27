#  Filename: SchemaValidation.py
# 
#  Copyright 2017  Kenny Gilfilen
# 
#  Verifies the xml schema of internationally formatted flight plans (ARINC 633,
#    versions 1 & 2.
# 
#  Revision History: 
#    July 24,2017 - Kenny Gilfilen - first version complete
#

import sys
import base64
import lxml
from lxml import etree
from lxml.etree import XMLSyntaxError

# from SchemaValidation import FlightPlan
# f=r[path to xml flight plan]
# fp = FlightPlan(A633_Rev=1)
# fp.validateFile(f)
# fp1=[the xml string to be validated]
# fp.validateStr(fp1)


class XMLSchemaValidation():

    FP = 0
    EFF = 1
    UAD = 2
    AFP = 3
    
    fp1 = '[path to FlightPlan.xsd]'
    fp2 = '[path to FlightPlan.xsd]'
    afp1 = '[FlightPlanAtcStrip.xsd]'
    afp2 = '[FlightPlanAtcStrip.xsd]'
    eff1 = '[path to EFF.xsd]'
    eff2 = '[path to EFF.xsd]'
    uad1 = r'[path to UpperAirData.xsd]'
    uad2 = r'[path to UpperAirData.xsd]'

    logLevel = 3

    def __init__(self,validationType=0,A633_Rev=1):
        self.log("starting xml validation with %s, and %s" % (validationType,A633_Rev),4)
        if A633_Rev == 1:
            if validationType == XMLSchemaValidation.FP:
                self.f =XMLSchemaValidation.fp1
            elif validationType == XMLSchemaValidation.EFF:
                self.f =XMLSchemaValidation.eff1
            elif validationType == XMLSchemaValidation.UAD:
                self.f =XMLSchemaValidation.uad1
            elif validationType == XMLSchemaValidation.AFP:
                self.f =XMLSchemaValidation.afp1
        elif A633_Rev == 2:
            if validationType == XMLSchemaValidation.FP:
                self.f =XMLSchemaValidation.fp2
            elif validationType == XMLSchemaValidation.EFF:
                self.f =XMLSchemaValidation.eff2
            elif validationType == XMLSchemaValidation.UAD:
                self.f =XMLSchemaValidation.uad2
            elif validationType == XMLSchemaValidation.AFP:
                self.f =XMLSchemaValidation.afp2
                
        self.log("XSD validation file is %s" % str(self.f),4)

        with open(self.f) as IF:
            pass
           
    # Methods for Validation Types	
	
    # xmlStr must be a python string.
    def validateStr(self,xmlStr):
        try:
            # reads xsd file
            schema_root = etree.parse(self.f)
            # loads xsd into a tree
            schema = etree.XMLSchema(schema_root)
            # gives the lxml module exactly the string type it wants
            self.log("  In Parm string to validate: %s" % xmlStr[:200],4)
            xml = str(xmlStr)
            self.log("  XML string to validate: %s" % xml[:200],4)
            # creates a parser with the schema
            parser = etree.XMLParser(schema = schema)
            # tries to parse the xml with the schema-checking parser
            root = etree.fromstring(xml.encode("utf8"), parser)
            return True
        except lxml.etree.XMLSyntaxError as e:
            self.log("XSD validation exception: %s" % str(e),3)
            return False

    # must be an xml text file
    def validateFile(self,xmlFile):
        try:
            # reads xsd file
            schema_root = etree.parse(self.f)
            # loads xsd into a tree
            schema = etree.XMLSchema(schema_root)
            
            # creates a parser with the schema
            parser = etree.XMLParser(schema = schema)
            
            root = etree.parse(xmlFile, parser)
            return True
        except lxml.etree.XMLSyntaxError as e:
            self.log("XSD validation exception: %s" % str(e),3)
            return False

    # elem must be lxml element or lxml element tree...
    def validateElementTree(self,elem):
        try:
            # reads xsd file
            schema_root = etree.parse(self.f)
            # loads xsd into a tree
            schema = etree.XMLSchema(schema_root)
            # validates the etree
            result=schema.validate(elem)
            return result
        except lxml.etree.XMLSyntaxError as e:
            self.log("XSD validation exception: %s" % str(e),3)
            return False
    
    # assumes attachment is twice base64 encoded
    def validateAttachment(self,attachment):

        # decodes; the attachments are encoded twice, so this will decode it up to 3 times,
        # if needed. verifies complete decode by trying to coerce it into an xml element
        decodedAttachment = None
        attachmt = base64.b64decode(attachment)
        result = None
        try:
            if etree.iselement(etree.fromstring(attachmt)):
                decodedAttachmentetree = etree.fromstring(attachmt)
                result = self.validateElementTree(decodedAttachmentetree)
                result2 = self.validateStr(attachmt.decode("utf8"))
        except lxml.etree.XMLSyntaxError:
            
            try:
                attachmt = base64.b64decode(attachmt)
                if etree.iselement(etree.fromstring(attachmt)):
                    decodedAttachmentetree = etree.fromstring(attachmt)
                    result = self.validateElementTree(decodedAttachmentetree)
                    result2 = self.validateStr(attachmt.decode("utf8"))
            except:    
                attachmt = base64.b64decode(attachmt)
                try:
                    isElement = etree.iselement(etree.fromstring(attachmt))
                    decodedAttachment = etree.fromstring(attachmt)
                    result = self.validateElementTree(decodedAttachment)
                    result2 = self.validateStr(attachmt.decode("utf8"))
                except:
                    self.assertTrue(0,"Unable to decode attachment")

        if result is True and result2 is True: 
            return True
        else:
            return  False

                    
    def log(self, text, level= 5):
        if XMLSchemaValidation.logLevel >= level:
            print(text)            
    
# usage:  >>> eff=UAD(A633_Rev=1)
# usage:  >>> eff=AFP(A633_Rev=2)
# usage:  >>> eff.validateStr([a legit python string])
# usage:  >>> eff.validateFile([path to an invalid xml file])
# usage:  >>> eff.validateElementTree([an lxml element or element tree])
# usage:  >>> eff.validateAttachment([an encoded (twice) attachment from EF003 response])
class UpperAirData(XMLSchemaValidation):
    
    def __init__(self,validationType=XMLSchemaValidation.UAD,A633_Rev=1):
        XMLSchemaValidation.__init__(self,validationType=validationType,A633_Rev=A633_Rev)

class EFF(XMLSchemaValidation):

    def __init__(self,validationType=XMLSchemaValidation.EFF,A633_Rev=1):
        XMLSchemaValidation.__init__(self,validationType=validationType,A633_Rev=A633_Rev)

class FlightPlan(XMLSchemaValidation):

    def __init__(self,validationType=XMLSchemaValidation.FP,A633_Rev=1):
        XMLSchemaValidation.__init__(self,validationType=validationType,A633_Rev=A633_Rev)

class ATCICAOFlightPlan(XMLSchemaValidation):

    def __init__(self,validationType=XMLSchemaValidation.AFP,A633_Rev=1):
        XMLSchemaValidation.__init__(self,validationType=validationType,A633_Rev=A633_Rev)

