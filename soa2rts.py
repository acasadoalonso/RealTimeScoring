#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This module gets that daya from SoaringSpot and prepaeres the infor for the REAL TIME SCORING
#
# Author: Angel Casado - May 2021
#
import sys
import json
import urllib.request, urllib.error, urllib.parse
import base64
import hmac
import hashlib
import base64
import OpenSSL
import uritemplate
import pycountry
import math
import os
import socket
import time
import sys
import socket
import config
import string
import os.path
import ksta                               # import the list on known gliders
from ognddbfuncs import *
from simplehal import HalDocument, Resolver
from pprint import pprint
from time import sleep
from datetime import datetime


#-------------------------------------------------------------------------------------------------------------------#

#########################################################################
#########################################################################


def getapidata(url, auth):                  # get the data from the API server

    req = urllib.request.Request(url)
    req.add_header('Authorization', auth)   # build the authorization header
    req.add_header("Accept", "application/json")
    req.add_header("Content-Type", "application/hal+json")
    r = urllib.request.urlopen(req)         # open the url resource
    j_obj = json.load(r)                    # convert to JSON
    return j_obj                            # return the JSON object

###################################################################

########################################################################
def oksta(station):
    if (station != "FLYMASTER" ):
        return(True)
    else:
        return(False)
#####################


def chkfilati(latitude,  flatil, flatiu):
    if (flatil == 0.0):
        return (False)
    if (flatil > 0):                    # northern hemisphere
        if (latitude < flatil or latitude > flatiu):
            return (True)
    else:                                       # southern hemisfere
        if (latitude > flatil or latitude < flatiu):
            return (True)
    return(False)
########################################################################
                                            # get the data from the soaring spot and return it as a HAL document
def gdata(url, key, prt='no'):
    global auth                             # auth and apiurl are globals
    global apiurl
    j_obj = getapidata(url, auth)           # call the fuction that get it
                                            # convert to HAL
    if prt == 'yes':                        # if print is required
        print(json.dumps(j_obj, indent=4))
    cd = HalDocument.get_data(HalDocument.from_python(
        j_obj), apiurl+'rel/' + key)        # get the data from the HAL document
    return cd


def getemb(base, ctype):
    global apiurl
    return(base['_embedded'][apiurl+'rel/'+ctype])


def getlinks(base, ctype):
    global apiurl
    return (base['_links'][apiurl+'rel/'+ctype]['href'])


###################################################################

#
# ---------- main code ---------------
#
def soa2rts(RTS, client, secretkey, prt=False):	# gather the competition data from SoaringSpot
    pgmver="V1.0"
    fid = {'NONE  ': 0}                         # FLARM ID list
    ffd = {}                      		# file descriptor list
    tmp = ''
    CCerrors=[]
    

    cin = 0                                     # input record counter
    cout = 0                                    # output file counter
    date = datetime.now()              		# get the date
    dte = date.strftime("%y%m%d")               # today's date
    paths=[]                                    # paths used
    hostname = socket.gethostname()
    datapath=config.datapath                    # directory where to store the IGC file
                                                # see if index day is requestedd

# --------------------------------------#
# ===== SETUP parameters =======================#
                                                # where to find the SQLITE3 database
    cwd = os.getcwd()			        # get the current working directory
                                            #     where to find the clientid and secretkey files
    secpath = cwd+"/SoaringSpot/"
    global apiurl
    apiurl = "http://api.soaringspot.com/"      # soaringspot API URL
    rel = "v1"                                  # we use API version 1
    taskType = "SailplaneRacing"                # race type

# ==============================================#
    hostname = socket.gethostname()		# hostname as control
    start_time = time.time()                    # get the time now
    utc = datetime.utcnow()            		# the UTC time
    date = utc.strftime("%Y-%m-%dT%H:%M:%SZ")   # get the UTC time
    local_time = datetime.now()        		# the local time
    fl_date_time = local_time.strftime("%Y%m%d")  # get the local time
                                            	# print the time for information only
    if prt:
         print("Hostname:", hostname)
         print("UTC Time is now:", utc)
         print(date)                                 #

         print("Local Time is now:", local_time)	# print the time for information only
         print("Config params.  SECpath:", secpath)

# nonce=base64.b64encode(OpenSSL.rand.bytes(36))  # get the once base
    nonce = base64.b64encode(os.urandom(36))    # get the once base
    message = nonce+date.encode(encoding='utf-8')+client.encode(encoding='utf-8')   # build the message
                                            	# and the message digest
    digest = hmac.new(secretkey, msg=message, digestmod=hashlib.sha256).digest()
    signature = str(base64.b64encode(digest).decode())   # build the digital signature
                                            	# the AUTHORIZATION ID is built now
    global auth
    auth = apiurl+rel+'/hmac/v1 ClientID="'+client+'",Signature="' + \
        signature+'",Nonce="'+nonce.decode(encoding='utf-8')+'",Created="'+date+'" '
    #print ("URLiauth:", auth)


                                            	# get the initial base of the tree
    url1 = apiurl+rel
                                            	# get the contest data, first instance
    cd = gdata(url1, 'contests', prt='no')[0]

    category = cd['category']                   # get the main data from the contest
    eventname = cd['name']
    compid = cd['id']
    country = cd['country']                     # country code - 2 chars code
    compcountry = country			# contry as defaults for pilots
                                            	# convert the 2 chars ID to the 3 chars ID
    ccc = pycountry.countries.get(alpha_2=country)
    country = ccc.alpha_3
    endate = cd['end_date']
    lc = getemb(cd, 'location')                 # location data
    lcname = lc['name']                         # location name
    print("\n\n= Contest ===============================")
    print("Category:", category, "Comp name:", eventname, "Comp ID:", compid)
    print("Loc Name:", lcname,   "Country: ", country, country, "End date:",  endate)
    print("=========================================\n\n")
    if prt:
       print("Classes:\n========\n\n")

    npil = 0                                    # init the number of pilots
    nwarnings = 0                               # number of warnings ...
    warnings = []                               # warnings glider
    classes = []
    pilots = []
    devicesid=""
# Build the tracks and turn points, exploring the contestants and task within each class
# go thru the different classes now within the daya


    pilots = []
    for cl in getemb(cd, 'classes'):
        #print "CLCLCL", cl
        classname = cl["type"]                  # search for each class
        if prt:
           print("Class:", classname, "\n\n")   # search for each class
                                                # search for the contestants on each class
        url3 = getlinks(cl, "contestants")
        ctt = gdata(url3,   "contestants")      # get the contestants data
        #print "CTTCTT",ctt
        for contestants in ctt:
        #print "FT", ft, "\n\n"
            fname = getemb(contestants, 'pilot')[0]['first_name']
            lname = getemb(contestants, 'pilot')[0]['last_name']
                                            # convert it to utf8 in order to avoid problems
            pname = fname.encode('utf-8').decode('utf-8')+" "+lname.encode('utf-8').decode('utf-8')
            if 'club' in contestants:
                club = contestants['club'].encode('utf-8').decode('utf-8')
            else:
                club = "club_NOTYET"
            if 'aircraft_model' in contestants:
                ar = contestants['aircraft_model']
            else:
                ar = "am_NOTYET"
            if 'contestant_number' in contestants:
                cn = contestants['contestant_number']
            else:
                cn = "cn_NOTYET"
    
            if 'nationality' in getemb(contestants, 'pilot')[0]:
                nation = getemb(contestants, 'pilot')[0]['nationality']
            else:
    
                if compcountry != '':
                    nation = compcountry
                else:
                    nation = "ES"             # by default is SPAIN
            # convert the 2 chars ID to the 3 chars ID
            ccc = pycountry.countries.get(alpha_2=nation)
            country3 = ccc.alpha_3
            igcid = getemb(contestants, 'pilot')[0]['igc_id']
            idflarm=""
            ognpair=""
            ognid=""
            idfreg=""
            if 'live_track_id' in contestants:      # check if we have the FlarmId from the SoaringSpot
                livetrk = contestants['live_track_id']  # flarmID and OGN pair
                if len(livetrk) == 9:
                   idflarm = livetrk                # case that just the FlarmID, no piaring
                if len(livetrk) == 19:              # format:  FLR123456 OGN654321
                   idflarm = livetrk[0:9]           # case that just the FlarmID and OGN tracker pair
                   ognpair = livetrk[10:]           # OGN trackers paired
                if len(idflarm) == 6:               # in case of missing FLR/ICA/OGN (deprecated)
                    if idflarm[0] == 'D':
                        idflarm="FLR"+idflarm       # assume a Flarm type 
                    elif idflarm[0].isdigit():
                        idflarm="ICA"+idflarm       # assume a ICAO type
                    else:
                        idflarm="OGN"+idflarm       # assume a OGN type

                idfreg=getognreg(idflarm[3:9])      # get the registration from OGN DDB       
            if 'aircraft_registration' in contestants:
                    regi = contestants['aircraft_registration']
                    ognid=getognflarmid(regi)       # get the flarm if from the OGN DDB
            else:
                    regi = "reg_NOTYET"             # if we do not have the registration ID on the soaringspota
            if idflarm != '':
               devicesid+=idflarm+'/'
            if prt:
               print("Pilot:",  pname, "Club:", club, "CompID:", cn, "Nation:", nation, "Country Code", country3,  "IGCID:", igcid, "Reg:", regi, "Flarm:", idflarm, idfreg, ognpair)
            npil += 1
            pil = {"PilotName": pname, "Club": club, "CompID":  cn, "Nation":  nation, "CountryCode": country3, "Registration": regi, "Class": classname,
                   "IgcID":  igcid, "Flarmid": idflarm, "OGNpair": ognpair}
            pilots.append(pil)
        cll = {"Class": classname}
        classes.append(cll)
        if prt:
           print("----------------------------------------------------------------\n\n")
    
    
    # print the number of pilots as a reference and control
    if len(devicesid) > 0:
       devicesid=devicesid[0:-1] 
    if prt:
       print("= Pilots ===========================", npil, "\n\n")
       print (devicesid) 
    RTS = {"Compname": eventname, "Category": category, "Country": country,
               "EndDate": endate, "Location": lcname, "Classes": classes, "Pilots": pilots, "Devices": devicesid}
    return (RTS)
