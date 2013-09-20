#!/usr/bin/env python
'''
Created on Jun 1, 2013

@author: Tommy Maersk
'''
import sqlite3 as lite
import subprocess
import httplib, urllib

subprocess.call("/home/pi/its-mon/getlog",shell=True)

con = lite.connect('/home/pi/its-mon/thedb.db')
cs = con.cursor()

theFile = open("/home/pi/its-mon/fail2ban.log")
while True:
    theline = str(theFile.readline())
    if theline == "":
        break
    theline = theline.replace("  ", " ")
    theline = theline.replace("'", "")
    theline = theline.replace("`", "")
    theline = theline.strip()
    theline = theline.split(",",1)

    thedate = theline[0]
    thedate = thedate.strip()


    thetext = theline[1]

    thetext = thetext.split(" ",1)
    thetext = thetext[1]
    thetext = thetext.strip()
    if "WARNING [ssh]" in thetext:
        thetext2 = thetext.split("[ssh]",1)
        thetext3 = thetext2[1].strip()
        thetext3 = thetext3.replace("Ban","")
        thetext3 = thetext3.replace("already banned","")
        thetext3 = thetext3.strip()
        print(thetext3)

        cs.execute("SELECT COUNT(thetime) FROM bantable WHERE theip = '"+thetext3+"' AND thetime = '"+thedate+"'")
        result = cs.fetchone()
        tjek = result[0]
        if tjek == 0:
            query = "INSERT INTO bantable (id,thetime,theip,issend) VALUES (NULL,'"+thedate+"','"+thetext3+"','0')"
            cs.execute(query)
            con.commit()
con.commit()
print("DONE FETCHING!")
con.close()

con1 = lite.connect('/home/pi/its-mon/thedb.db')
cs1 = con1.cursor()

data = cs1.execute("SELECT * FROM bantable WHERE issend = 0")
data = data.fetchall()

for i in data:
        theid = i[0]
        theip = i[2]
        thetime = i[1]
        print(theip)
        thestring=theip+" tryed to brute force your ass at "+thetime
        cs1.execute('''UPDATE bantable SET issend = ? WHERE id = ?''', (1,theid))
        conn = httplib.HTTPSConnection("api.pushover.net:443")
        conn.request("POST", "/1/messages.json",
          urllib.urlencode({
            "token": "az5iubCmVPUAD9oBs8zB4ot2y4YMX4",
            "user": "urKFgiwKzgZvtKwxgFzf7EJV9muNq4",
            "message": thestring,
          }), { "Content-type": "application/x-www-form-urlencoded" })
        conn.getresponse()
cs1.close
con1.commit()


print("DONE SENDING!")
