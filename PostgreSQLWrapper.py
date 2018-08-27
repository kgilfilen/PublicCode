#  Filename: PostgreSQLWrapper.py
# 
# 
# Purpose: provides access to PostgreSQL database containing test data
#


# Message table
'''"Message_Name",text              Dispatch
"Message_Version",integer           7
"Message_Body",text                 <?xml version="1.0" encoding="UTF-8"?><message body ...
"Message_Response",text             <Status>
"Message_Class",text                REQUEST
"TrackingID",text                   UFT...
"Message_Owner",text                Eng_Int_Test
"Timestamp",time without time zone
"ID",serial NOT NULL                212
"Var1",text                         <notam>
"Var2",text                         DEN
"Var3",text
"Message_UseCase",text              Flight_plan_001
"Active",boolean
"Var4",text
"Var5",text
"Var6",text
"Var7",text
"Var8",text
"Var9",text
"Var10",text
"Var11",text
"Var12",text
"Var13",text
"Var14",text
"Var15",text
"Var16",text
"Var17",text
"Var18",text
"Var19",text
"Var20",text
"Message_Class2",text
"TestType",text #-- EFF and/or FP_PKG webservice....
"RunTest",boolean #-- Determines if row is to be executed in test run....'''

import sys
from io import BytesIO
import psycopg2
import pycurl
import datetime
import time


class DB_Access:

    #conn = psycopg2.connect(host="[server]",port=5432,database="[database name]", user="postgres", password="IntTest2015")
    testHost="[server]"
    testDatabase="[database name]"
    testUser="postgres"
    testPassword="IntTest2015"
	port=5432

    def __init__(self,host=None,port=None,database=None,user=None,pwd=None):
        if host==None and port ==None and database==None and user==None and pwd==None:
            self.host = DB_Access.testHost
            self.db = DB_Access.testDatabase
            self.user = DB_Access.testUser
            self.pwd = DB_Access.testPassword
            self.port = DB_Access.port
        else:
            self.host = host
            self.db = database
            self.user = user
            self.pwd = pwd
            self.port = port
            
        self.conn = psycopg2.connect(host=self.host, port=self.port,database=self.db, user=self.user, password=self.pwd)
        self.cur = self.conn.cursor()
        

    # returns a python list with message ID [0] and message [1]
    # assumes use case field is unique, sends first (and hopefully only) instance it finds
    def getMessageAndID(self,useCase):
        self.cur.execute( """SELECT * FROM "Functional_Test"."Functional_Test_Messages" 
            WHERE "Functional_Test"."Functional_Test_Messages"."Message_UseCase" = (%s) """,(useCase,)) 

        msgType = 0
        msgReq=2
        msgStatus=3
        msgResp=4
        msgID=8
        msgUseCase = 12
        for msg in self.cur.fetchall():
            if msg[msgUseCase] == useCase:
                return [msg[msgID],msg[msgReq]]
    
    def getConnDB(self):
        return self.conn
    
    def getCursor(self,conn):
        return self.cur

    # ID = 121...Use case = Flight_plan_001
    # >>> from PostgreSQLWrapper import DB_Access
    # >>> mydb = DB_Access()
    # >>> ef=r'c:\temp\Dispatch-Original.xml'
    # >>> with open(ef) as EF:
    # >>>   body=EF.read()
    # >>>   EF.close()
    # >>> mydb.insertTest("Dispatch", 5, body, resp, "PUBLISH", "Eng_Int_Test","Incorrect_Owner_Field","PUBLISH")
    
    def insertTest(self,name, version, body, resp, mClass, owner,useCase,mClass2):
        self.cur.execute( """INSERT INTO "Functional_Test"."Functional_Test_Messages" 
        ("Message_Name", "Message_Version", "Message_Body", "Message_Response", "Message_Class", "Message_Owner", "Message_UseCase","Message_Class2")  
            VALUES (%s, %s, %s, %s, %s, %s, %s, %s)""",
            (name, version, body, resp, mClass, owner,useCase,mClass2))
        self.commitDB()
            
    # example: ID = 121...Use case = Flight_plan_001
    # mydb.insertET(msgID='121',etime=12.44,component="FP_UI")
    # etime can be string or numeric or timedelta
    #
    def insertET(self,msgID,etime,component, notes=None):
        year=datetime.datetime.today().year
        month=datetime.datetime.today().month
        day=datetime.datetime.today().day
        
        try:
            # expects a good float coming in, but allows a timedelta type as well.
            float(etime)
        except TypeError:
            try:
                etime = float(str(etime.seconds) + "." + str(etime.microseconds))
            except:
                print("PostgreSQLWrapper.py: trying to write time benchmark to DB; cannot \nfigure out what to do with elapsed time value: \n    %s" % str(etime))            
                return
        try: 
            int(msgID)
        except: 
            print("msgID needs to match a Key in the Messages table (numbers only)")
            return
        if component not in ["FP_Translator","FP_UI","FP_PKG"]: 
            print('Component needs to be "FP_Translator","FP_UI", or "FP_PKG"')
            return
        self.cur.execute( """INSERT INTO "Functional_Test"."Functional_Test_Runs" ("Date_TestRun", "Run_ElapsedTime", "ID", "Notes","Component")  
            VALUES (%s, %s, %s, %s, %s)""",(datetime.date(year,month,day), datetime.timedelta(seconds=etime), msgID, notes,component))
        self.commitDB()
        
    def commitDB(self,conn=None):
        if conn is not None:
            conn.commit()
        else:
            self.conn.commit()
    
    # the quotes matter: sql='SELECT * FROM "Functional_Test"."Functional_Test_Messages";'
    def executeSQL(self,sql):
        self.cur.execute(sql)
        
    def fetchOne(self,cur):
        return cur.fetchone()
        
    def fetchAll(self,cur=None):
        if cur is not None:
            return cur.fetchall()
        else:
            return self.cur.fetchall()
        
    def closeConn(self,conn=None):
        if conn is not None:
            conn.close()
        else:
            self.conn.close()

    def closeCursor(self,cur):
        if cur is not None:
            cur.close()
        else:
            self.cur.close()