# -*- coding: utf-8 -*-
"""
Created on Fri Jun  5 18:09:02 2015

@author: legitz7
"""
import sys, os, psycopg2, datetime
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


def ppgConn(dbname, user, host="localhost", passwd=""):

    # we need to clean up whatever the user delivers here,
    #since proper syntax requires consistent single quotes around 
    #the arguments for the exec string
    arglist=[dbname, user, host]
    if len(passwd) >0:
        usepasswd = True
        arglist.append(passwd)
    else:
        usepasswd = False
    
    for eacharg in arglist:    
    #First we stringify the required arguments
        eacharg=str(eacharg)        
    #now we strip off any quotes that may have been shipped with the args
        eacharg = eacharg.strip().strip('"').strip("'").strip('"')

    connString="dbname='"
    connString += dbname
    connString += "' user='"
    connString += user
    connString += "' host='"
    connString += host
    connString +="'"
    #connString +="' password=''"
    if (usepasswd == True):
        connString += " password='"
        connString += passwd
        connString +="'"
    print "connString = %s"  % connString
    
    try:
        conn=psycopg2.connect(connString)
        print "Connection Successful!"
        
        return conn
    except:
        print "unable to establish connection"
        return -1
        
def ppgClose(conn):
    try:
        conn.close()
        print "Connection successfully closed"
        return 0
    except:
        print "Error occurred while closing connection"
        return -1
        
def ppgRunSQL(conn, exstring):
    try:    
        cur=conn.cursor()
        cur.execute(exstring)
        rows=cur.fetchall()
        print "SQL query executed: %s" % exstring
        cur.close()        
        return rows
    except:
        print "SQL query execution failed: %s" % exstring
        try:
            cur.close()
        except:
            0
        return -1

def checkExistence(dbname="worddb1", user="biouser", host="localhost", passwd="biouser"):
    ceConn=ppgConn(dbname, user, host, passwd)
    if ceConn is not -1:
        ppgClose(ceConn)
        return True
    else:
        ppgClose(ceConn)
        return False

def makeWordDBDatabase(name="worddb1", rendition=1, password='postgres'):
    wdbConn=ppgConn(dbname='postgres', user='postgres', host='localhost', passwd=password)
    wdbConn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)     
    #thisDB=name+str(rendition)  
    #thisDB=(name,)
    #makeBDBString= """ CREATE DATABASE %s;"""
    #ownString="""ALTER DATABASE %s OWNER TO biouser;"""
    makeWDBString= """ CREATE DATABASE "worddb1";"""
    ownString="""ALTER DATABASE "worddb1" OWNER TO biouser;"""  

    cur = wdbConn.cursor()
    print 'making database'
    
    cur.execute(makeWDBString)
    cur.execute(ownString)
    wdbConn.commit()
    print 'new database made'
    ppgClose(wdbConn)
    return 1
#    except:
#        print 'exception raised creat ng database'
#        psyfuncs.ppgClose(bdbConn)
#        return -1

#propList=['Word', 'ID', 'Length', 'Language', 'Prefix','Part of Speech', 'Synonym', 'Tag']
#propList=["""wordname""", """wordid""", """wordlength""", """language""", """prefix""","""pos""", """synonym""", """tag"""]

def makeWordDBTables(name="worddb1", user='biouser', host='localhost', password='biouser'):
    makeLangEnum="""CREATE TYPE langenum AS ENUM('afrikaans','czech','dutch','english', 'french', 'german' , 'greek', 'hungarian','hindi','italian', 'japanese','latin', 'portuguese','romanian','russian','spanish','turkish', 'ukranian'   );"""
    makePosEnum="""CREATE TYPE posenum AS ENUM('noun','verb','adjective','adverb','preposition','conjunction','pronoun', 'profanity', 'saying', 'salutation') ;"""    
    makeWordTable="""CREATE TABLE wordtable (
    wordid bigserial PRIMARY KEY,
    wordname varchar(400),
    wordlength bigint, 
    language langenum,
    pos posenum,
    prefix varchar(40),
    synonym bigint REFERENCES wordtable(wordid),
    synlist bigint[],
    taglist bigint[],
    bindlist bigint[],
    iskey boolean,
    adddate timestamp);"""
    
    makeTagTable="""CREATE TABLE tags(
    tagid bigserial PRIMARY KEY,
    tagname varchar(400),
    wordlist bigint[],
    bindlist bigint[]
    );"""
    
    makeTagBindTable="""CREATE TABLE tagbinds(
    bindid bigserial PRIMARY KEY,
    tagid bigint REFERENCES tags(tagid),
    tagname varchar(400),
    wordid bigint REFERENCES wordtable(wordid),
    wordname varchar(400)
    );"""    
    

    

    genStrings = (makeLangEnum, makePosEnum, makeWordTable, makeTagTable,
                  makeTagBindTable)
    
    dbConn=ppgConn(name, user, host, password)
    cur=dbConn.cursor()
    for genString in genStrings:
        cur.execute(genString)
        dbConn.commit()
    dbConn.commit()
    ppgClose(dbConn)
    
    
def addWordFromDict(wordDict):
    print 'addWord requested for :'
    print wordDict
    #first need to check existence of stated synonym, tags
    goodStatus=1
    dbConn=ppgConn('worddb1','biouser', passwd='biouser')
    dbCursor=dbConn.cursor()
    syncheck = """ SELECT wordid FROM wordtable WHERE wordname = %s ORDER BY wordid DESC;"""
    addSyn = """ INSERT INTO wordtable(wordname, wordlength, pos, adddate,language) VALUES (%s, %s, %s, %s,%s) ;"""
    #add any given synonyms to the database
    synids=[]    
    tagids=[]
    for s in wordDict['synlist']:
        synval=(s,)
        dbCursor.execute(syncheck, synval)
        grab=dbCursor.fetchone()
        if grab is not None:
            idval=grab[0]
        else:
            idval = 0
        if idval > 0:
            thisSynID=idval
        else:
            synVals=(s,len(s),wordDict['pos'],datetime.datetime.now(), 'english')
            dbCursor.execute(addSyn, synVals)
            try:
                dbCursor.execute(syncheck, synval)
                idval=dbCursor.fetchone()[0]
                thisSynID=idval
            except:
                goodStatus=-1
        synids.append(thisSynID)
    #add any given tags to the database
    if goodStatus>0:
        tagcheck = """SELECT tagid FROM tags WHERE tagname = %s;"""
        addTag = """ INSERT INTO tags(tagname) VALUES (%s);"""
   
        for t in wordDict['taglist']:
            if len(t)>0:
                tagval=(t,)
                dbCursor.execute(tagcheck, tagval)
                grab=dbCursor.fetchone()
                if grab is not None:
                    idval=grab[0]
                else:
                    idval = 0
                if idval > 0:
                    thisTagID=idval
                else:
                    dbCursor.execute(addTag, tagval)
                    try:
                        dbCursor.execute(tagcheck, tagval)
                        idval=dbCursor.fetchone()[0]
                        thisTagID=idval
                    except:
                        goodStatus=-2
                tagids.append(thisTagID)
    #ok, now we can add the word, and then update foreign keys
    if goodStatus > 0:
        wordCheck = """ SELECT wordid from wordtable WHERE wordname = %s AND language = %s AND pos = %s;"""
        addWordString = """ INSERT INTO wordtable(wordname, wordlength, language, pos, iskey, adddate) VALUES (%s, %s, %s, %s, %s, %s) ;"""
        addWordPreString = """ INSERT INTO wordtable(wordname, wordlength, language, pos, iskey, adddate, prefix) VALUES (%s, %s, %s, %s, %s, %s, %s) ;"""
        
        checkvals=(wordDict['wordname'], wordDict['language'], wordDict['pos'])
        dbCursor.execute(wordCheck, checkvals)
        grab=dbCursor.fetchone()
        if grab is not None:
            oldid=grab[0]
        else:
            oldid = 0
        #if the word already exists in the database, then we are updating its specs
        if oldid > 0:
            wordDict['id']=oldid
            uparams=[]
            updateString=""" UPDATE wordtable SET """
            if len(wordDict['synlist'])>1:
                updateString += """ synlist=%s,"""
                synarray=[]
                for s in wordDict['synlist']:
                    sv=(s,)
                    dbCursor.execute(syncheck, sv)
                    grab=dbCursor.fetchone()
                    if grab is not None:
                        sid=grab[0]
                    else:
                        sid = 0
                    if sid > 0:
                        synarray.append(sid)
                uparams.append(synarray)
            if len(wordDict['taglist'])>1:
                updateString += """ taglist=%s,"""
                tagarray=[]
                for t in wordDict['taglist']:
                    tv=(t,)
                    dbCursor.execute(tagcheck, tv)
                    grab=dbCursor.fetchone()
                    if grab is not None:
                        tid=grab[0]
                    else:
                        tid = 0                                    
                    if tid > 0:                    
                        tagarray.append(tid)
                uparams.append(tagarray)
            if len(wordDict['synlist'])==1:
                updateString += """synonym=%s,"""
                uparams.append(wordDict['synlist'][0])
            updateString += """ adddate = %s WHERE wordid = %s;"""
            uparams.append(datetime.datetime.now())
            uparams.append(oldid)
            uparams=tuple(uparams)
            dbCursor.execute(updateString, uparams)
            dbConn.commit()
            goodStatus=5
        #otherwise, we have to add fresh
        else:
            if len(wordDict['prefix'])>0:
                addVals=(wordDict['wordname'], len(wordDict['wordname']),wordDict['language'], wordDict['pos'], True, datetime.datetime.now(), wordDict['prefix'])
                dbCursor.execute(addWordPreString,addVals)                
            else:
                addVals=(wordDict['wordname'], len(wordDict['wordname']),wordDict['language'], wordDict['pos'], True, datetime.datetime.now())
                dbCursor.execute(addWordString,addVals)
            getnew="""SELECT max(wordid) FROM wordtable;"""
            dbCursor.execute(getnew)
            newID=dbCursor.fetchone()[0]
            wordDict['id']=newID
            if len(wordDict['synlist'])==1:
                synstring="""UPDATE wordtable SET synonym = %s WHERE wordid = %s;"""
                synvals=(synids[0], newID)
                dbCursor.execute(synstring, synvals)
            elif len(wordDict['synlist'])>1:
                slstring = """UPDATE wordtable SET synlist = %s WHERE wordid = %s;"""
                slvals=(synids, newID)
                dbCursor.execute(slstring, slvals)
            if len(wordDict['taglist'])>0:
                tagstring = """UPDATE wordtable SET taglist = %s WHERE wordid = %s;"""
                tvals=(tagids, newID)
                dbCursor.execute(tagstring, tvals)   
                bindString = """INSERT INTO tagbinds(wordid, wordname, tagid, tagname) VALUES (%s, %s, %s, %s);"""                
                bidString="""SELECT max(bindid) FROM tagbinds;"""                
                bindarray=[]
                addBind=""" UPDATE tags SET bindlist = %s WHERE tagid = %s;"""                
                getBinds="""SELECT bindlist FROM tags WHERE tagid = %s;"""
                tbstring="""UPDATE wordtable SET bindlist = %s WHERE wordid = %s;"""
                for j in range(len(tagids)):
                    tbvals=(newID, wordDict['wordname'], tagids[j], wordDict['taglist'][j] )
                    dbCursor.execute(bindString, tbvals)
                    dbCursor.execute(bidString)
                    bid=dbCursor.fetchone()[0]
                    bindarray.append(bid)
                    #updating bindlist for TAGS
                    tid=(tagids[j],)
                    dbCursor.execute(getBinds, tid )
                    tagsBL=dbCursor.fetchone()[0]
                    try: 
                        tbll = len(tagsBL)
                        if tbll>0:
                            blExists=True
                        else:
                            blExists=False
                    except: blExists=False
                    if blExists:
                        tagsBL.append(bid)
                        newTBL=(tagsBL, tagids[j])
                    else:
                        newTBL=([bid],tagids[j])
                    dbCursor.execute(addBind, newTBL)
                #updating bindlist for WORD
                ba=(bindarray,newID)
                dbCursor.execute(tbstring, ba)
                    
        if goodStatus > 0:
            #finally, we update the .synList of the synonym
            oldRevIdString="""SELECT synlist FROM wordtable WHERE wordid = %s ;"""
            updateRevIdString="""UPDATE wordtable SET synlist = %s WHERE wordid = %s;"""
            for synid in synids:
                s=(synid,)
                dbCursor.execute(oldRevIdString,s)
                grab=dbCursor.fetchone()
                if grab is not None:
                    try:
                        oldids=grab[0]
                        newids=oldids.append(wordDict['id'])
                    except:
                        newids=[wordDict['id']]
                else:
                    newids=[wordDict['id']]
                upvals=(newids, synid)
                dbCursor.execute(updateRevIdString, upvals)
                    
                    
                
            dbConn.commit()            
        ppgClose(dbConn)
        return goodStatus
    
    
    
def dropDatabase(name="worddb1", password='biouser'):
    ddbConn=ppgConn(dbname='postgres', user='biouser', host='localhost', passwd=password)
    ddbConn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)    
    
    #thisDB=(name,)
    dropDBString= """ DROP DATABASE "worddb1";""" 
    #makeDBString="""CREATE DATABASE ghg;"""
    #testString="""SELECT datname FROM pg_database;"""
    cur = ddbConn.cursor()

    #curstring = cur.mogrify(dropDBString, thisDB)
    #print curstring
    try:
        cur.execute(dropDBString )
        ppgClose(ddbConn)
        return 1
    except:
        ppgClose(ddbConn)
        return -1    

def checkAndReplace(dName="worddb1"):
    checkStatus = checkExistence(dbname=dName)
    if checkStatus:
        print 'db exists. killing now'
        killStat = dropDatabase(name=dName)
        print "killStatus: %s" % (killStat)
    else:
        print 'db does not exist. creating now.'
    makeWordDBDatabase()
    makeWordDBTables()
        
#checkAndReplace()


"""
Next up on the to-do list for wordQuery: 
---DONE---1) write tagBinds  routine for addWords
---DONE---2) write query -> sql (and result parsing) loop

# Debug that shit

---DONE---3) write results display table, 
---DONE---with autosorting enabled
---DONE---3,5 finish regexes
4) write word expansion tabs (w editing option...)
5) flash cards
5) enable root specification

"""