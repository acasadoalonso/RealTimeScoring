#!/usr/bin/python3
# -*- coding: UTF-8 -*-
# This program reads the the records received from the OGN APRS server for a competition
# and generates IGC files for each flight
#
# Author: Angel Casado - May 2021
#
import sys
import json
import os
import socket
import time
import sys
import string
import ephem
import pytz
import os.path
import atexit
import signal
import argparse
from parserfuncs import *               # the ogn/ham parser functions
from ognddbfuncs import *		# the ogn DDB functions
from soa2rts     import *		# the soaringspot to real time scoring function
from datetime    import datetime
from time        import sleep


import config
#-------------------------------------------------------------------------------------------------------------------#

#########################################################################
# shutdown routine, close files and report on activity
#########################################################################

def shutdown(sock):
                                        # shutdown before exit
    sock.shutdown(0)                    # shutdown the connection
    sock.close()                        # close the connection file
    for f in ffd:			# close all the IGC files generated
        f.close()
    local_time = datetime.now() 	# report date and time now
    location.date = ephem.Date(datetime.utcnow())
    print("Local Time (server) now is:", local_time, " and UTC time at location ",
          config.location_name, "is:", location.date, "UTC.\n")
    try:
        os.remove(config.APP+".alive")	# delete the mark of alive
    except:
        print("No SW.live")

    return 

##################################################################
def signal_term_handler(signal, frame):
    print('got SIGTERM ... shutdown orderly')
    shutdown(sock)  			# shutdown orderly
    print("\n\nExit after a SIGTERM now ....\n\n")
    sys.exit(0)
#########################################################################
# ......................................................................#
signal.signal(signal.SIGTERM, signal_term_handler)
# ......................................................................#

###################################################################
#
# ---------- main code ---------------
#
###################################################################
pgmver="V1.0"				    # program version
fid = {}                         	    # FLARM ID list
ffd = {}                      		    # file descriptor list
RTS={}					    # the output from soa2rts
tmp = ''				    # an add to the IGC fine name
prt = False				    # print debugging, false by default  
CCerrors=[]
nerr=0					    # number of errors found
nrecs=0
loopindex=0				    # loop index
cin = 0                                     # input record counter
cout = 0                                    # output file counter
datenow = datetime.now()       	    	    # get the date
dte = datenow.strftime("%y%m%d")            # today's date
paths=[]                                    # paths used
hostname = socket.gethostname()
datapath=config.datapath                    # directory where to store the IGC files
                                            # see if index day is requestedd
# protection against running the same daemon at the same time
if  os.path.exists(config.PIDfile):
    print("RTS already running !!!")
    raise RuntimeError("RTS already running !!!")
    exit(-1)                    	    # exit with an error code
#
# --------------------------------------#
with open(config.PIDfile, "w") as f:        # protect against to running the daemon twice
    f.write(str(os.getpid()))
    f.close()
# remove the lock file at exit
atexit.register(lambda: os.remove(config.PIDfile))

# ---------------------------------------------------------------- #
print("\n\n")
print("Utility to get the api.soaringspot.com data and prepare the RTS  ", pgmver)
print("======================================================================")
# ======================== parsing arguments =======================#
parser = argparse.ArgumentParser(description="Real Time Scoring data gathering daemon")
parser.add_argument('-p', '--print',  required=False, dest='prt',    action='store', default=False)
parser.add_argument('-c', '--client', required=False, dest='client', action='store', default='')
parser.add_argument('-s', '--secret', required=False, dest='secret', action='store', default='')
args 		= parser.parse_args()
prt 		= args.prt		# print on|off
client 		= args.client		# client ID
secretkey	= args.secret		# secret key

# ======================== SETUP parameters =======================#
cwd = os.getcwd()                       # get the current working directory
                                        # where to find the clientid and secretkey files
if client == '' and secret == '':
 if config.clientid == '' or config.secretkey == '':
   if prt:
      print("Reading the clientid/secretkey from the SoaringSpot directory")
   secpath = cwd+"/SoaringSpot/"	# if client/screct keys are not in the config file, read it for SoaringSpot directory
   f = open(secpath+"clientid") 	# open the file with the client id
   client = f.read()                    # read it
   client = client.rstrip() 		# clear the whitespace at the end
   f = open(secpath+"secretkey") 	# open the file with the secret key
   secretkey = f.read()                 # read it
                                        # clear the whitespace at the end
   secretkey = secretkey.rstrip().encode(encoding='utf-8')
 else:
   client = config.clientid
   client = client.rstrip() 		# clear the whitespace at the end
   secretkey = config.secretkey
   secretkey = secretkey.rstrip().encode(encoding='utf-8')
else:					# use the clientid and secretkey from the arguments
   client = client.rstrip() 		# clear the whitespace at the end
   client = client.replace('\\', '')
   secretkey = secretkey.replace('\\', '')
   secretkey = secretkey.rstrip().encode(encoding='utf-8')
#
#					# call the SOA2RTS function in order to get the competition information
#
RTS=soa2rts(RTS, client, secretkey, prt=prt) # call the SoaringSpot API to gather the competition information
#
jsonfile = open(datapath+"/RTS2IGC.json", 'w') # write the JSON file as a debugging
j = json.dumps(RTS, indent=4)
jsonfile.write(j)			# dump it
jsonfile.close()

devicesid=RTS["Devices"]		# get the list of FlarmsIDs
pilots=RTS['Pilots']			# get the pilots infor from the soa2rts function
if len(devicesid) == 0:            	# if no devices ???
   print ("No devices to score ... Pilots: ", len(pilots), "\n\n")
   exit (-1)				# nothing else to do
location_latitude = config.location_latitude  # get the configuration parameters
location_longitude = config.location_longitude
#
#-----------------------------------------------------------------
# Initialise API for computing sunrise and sunset
#-----------------------------------------------------------------
#
location = ephem.Observer()		# create the ephemerides
location.pressure = 0
location.horizon = '-0:34'              # Adjustments for angle to horizon

location.lat, location.lon = location_latitude, location_longitude
datenow = datetime.now()
next_sunrise = location.next_rising(ephem.Sun(), datenow)
next_sunset = location.next_setting(ephem.Sun(), datenow)
print("Sunrise today is at: ", next_sunrise, " UTC ")
print("Sunset  today is at: ", next_sunset,  " UTC ")
print("Time now is: ", datenow, " Local time")
#
# -----------------Connect with the APRS-------------------------------------------------
#
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM) # create a socket and connect
sock.connect((config.APRS_SERVER_HOST, config.APRS_SERVER_PORT))
print("Socket sock connected")		# report connected to the APRS network

                                        # logon to OGN APRS network
if len(devicesid) > 0:                  # if we have tracker pairing table ???
    filter = "filter b/"+devicesid+" \n"  # prepare the filter param of login
    login = 'user %s pass %s vers Real-Time-Scoring %s %s' % (config.APRS_USER, config.APRS_PASSCODE, pgmver, filter)
else:					# THIS never will be the case !!!!!
    login = 'user %s pass %s vers Real-Time-Scoring %s %s' % (config.APRS_USER, config.APRS_PASSCODE, pgmver, config.APRS_FILTER_DETAILS)
login=login.encode(encoding='utf-8', errors='strict') 
sock.send(login)                        # login into the APRS server
                                        # Make the connection to the server
sock_file = sock.makefile(mode='rw')
sleep(2)				# give it a chance to do the LOGIN
print("APRS Version:", sock_file.readline()) # report the reply
if prt:
   print("APRS Login request:", login)	# report the LOGIN used
print("APRS Login reply:  ", sock_file.readline()) # report the acceptance message
# --------------------------------------------------------------------------------
start_time = time.time()                # get the start and local times
local_time = datetime.now()
fl_date_time = local_time.strftime("%y%m%d")

keepalive_count = 1                     # number of keep alive messages
                                        # every 3 minutees we send a keep alive message to the APRS server
keepalive_time = time.time()
                                        # and we create a RTS.alive file for control that we are alive as well
alive(config.APP, first="yes")		# first means crete the file, it is the first time
#
#-------------------------- MAIN process ---------------------------------------
#
print ("Number of pilots on the competition:", len(pilots))
print ("Start gathering data from the OGN")
print ("=================================")
sys.stdout.flush()                      # flush the print messages
sys.stderr.flush()                      # flush the print messages
try:					# try to be able to catch exception the ctrl-C 

    while True :			# endless LOOP, until end of day or signal catched 

        # check the localtime for this location...
        location.date = ephem.Date(datetime.utcnow())
        date = datetime.utcnow()        # time of the server
        localdate = datetime.now()      # time of the server
        # if it is past the sunset or 21:00h local time ??
        if location.date > next_sunset or localdate.hour > 21: # until sunset or 21:00h local time

            print("At Sunset now ... Time is (server):", date, "UTC. Location time:",
                  location.date, "UTC ... Next sunset is: ", next_sunset,  " UTC \n================================================================================\n")
            shutdown(sock)		# shutdown in that case
            print("At Sunset ... Exit\n\n", localdate)
            sys.stdout.flush()          # flush the print messages
            sys.stderr.flush()          # flush the print messages
            exit(0)

        current_time = time.time()
        elapsed_time = current_time - keepalive_time
        if (current_time - keepalive_time) > 180:       # keepalives every 3 mins
            try:
                rtn = sock_file.write("# Python RTS App\n\n") # send a comment message to keep it alive
                # Make sure keepalive gets sent. If not flushed then buffered
                sock_file.flush()                       # force to write the data
                alive(config.APP)                       # indicate that we are alive
                run_time = time.time() - start_time     # get the run time
                if prt:
                    print("Send keepalive no#: ", keepalive_count, " After elapsed_time: ", 
                         int((current_time - keepalive_time)), " After runtime: ", int(run_time), " secs")
                keepalive_time = current_time		# start to time again
                keepalive_count += 1                    # keep alive counter and shutdown indicator if -1

            except Exception as e:

                print(('Something\'s wrong with socket write. Exception type is %s' % (repr(e))), file=sys.stderr)
                print("Socket error:", keepalive_count, current_time, file=sys.stderr)
                if keepalive_count != -1:               # check if we are at shutdown now
                    keepalive_count = -1                # indicate shutdown now
                    shutdown(sock)
                print("At socket error ... Exit\n\n")
                exit(-1)
            sys.stdout.flush()                          # flush the print messages
            sys.stderr.flush()                          # flush the print messages


# ------------------------------------------------------- main loop ------------------------------------- #
        if prt:
            print("In main loop. Count= ", loopindex, "Current time: ", localdate)
            loopindex += 1
        try:
            # Read packet string from socket
            packet_str = sock_file.readline()

            if len(packet_str) > 0 and packet_str[0] == "#":
                continue

        except socket.error:
            print("Socket error on readline", file=sys.stderr)
            nerr += 1
            if nerr > 20:
                print("Socket error multiple  Failures.  Orderly closeout, keep alive count:", keepalive_count, file=sys.stderr)
                date = datetime.now()
                print("UTC now is: ", date, "Bye ...\n\n")
                break
            else:
                sleep(5)                                # sleep for 5 seconds and give it another chance
                continue
        # A zero length line should not be return if keepalives are being sent
        # A zero length line will only be returned after ~30m if keepalives are not sent
        if len(packet_str) == 0:
            nerr += 1
            print("zero length", loopindex)
            if nerr > 200:
                print("Multiple Read returns zero length string. Failure.  Orderly closeout, keep alive count:", keepalive_count, file=sys.stderr)
                date = datetime.now()
                print("UTC now is: ", date, "Bye ...\n\n", file=sys.stderr)
                break
            else:
                sleep(5)                                # sleep for 5 seconds and give it another chance
                continue
        if prt:
            print("DATA:", packet_str)                  # print the data received
        ix = packet_str.find('>')                       # convert to uppercase the ID
        cc = packet_str[0:ix]                           # just the ID
        cc = cc.upper()
        packet_str = cc+packet_str[ix:]                 # now with the ID in uppercase
        data = packet_str
        msg = {}                                        # create the dict
# ---------------------------------------------------------------------------------------------------------------------------------------------------------- #
        msg = parseraprs(data, msg)             	# parser the data
        if msg == -1:                           	# parser error
            if cc not in CCerrors:
                 print("Parser error:", data)
                 CCerrors.append(cc)
            continue
        ident 	    = msg['id']                       	# id
                                            		# get the information once parsed
        ptype       = msg['aprstype']
        longitude   = msg['longitude']
        latitude    = msg['latitude']
        altitude    = msg['altitude']
        if altitude == None:
           altitude = 0
        path        = msg['path']
        if path not in paths:
           paths.append(path)
        speed       = 0
        course      = 0
        if path == 'aprs_aircraft' or path == 'flarm' or path == 'tracker':
            if 'speed' in msg :
                speed   = msg['speed']
            if 'course' in msg :
                course  = msg['course']
        source      = msg['source']
        if len(source) > 4:
            source = source[0:3]
        otime       = msg['otime']


        if longitude == -1 or latitude == -1:
            continue
        callsign = ident                        # get the call sign FLARM ID

        if (data.find('TCPIP*') != -1) or path == 'aprs_receiver':         # ignore the APRS lines
            ident = callsign.upper()            # station ID
            continue                            # go for the next record
        idname = data[0:9]                      # exclude the FLR part
        if idname[0:3] == 'RND':
            continue
        station = msg['station']                # get the station ID
        if ptype == 'status':                   # if OGN status report
            continue
        if not ident in fid:                # if we did not see the FLARM ID
            for pil in pilots:
                if pil['Flarmid'] == ident:
                   pilotname=pil['PilotName']
                   compid=pil['CompID']
                   classg=pil['Class']
                   regis=pil['Registration']
                   break
            fid[ident] = 0                  # init the counter
            cout += 1                       # one more file to create
                                            # prepare the IGC header
            fd = open(datapath+tmp+'FD'+dte+'.' +
                          station+'.'+idname+'.IGC', 'w')
            fd.write('AGNE001GLIDER\n')     # write the IGC header
            fd.write('HFDTE'+dte+'\n')      # write the date on the header
            fd.write('AHFDTM100DATUM:WGS-1984\n')     # write the IGC header - the datum 
            #HFGIDGLIDERID:D2520
            fd.write('HFGIDGLIDERID:'+regis+'\n')
            #HFGTYGLIDERTYPE:Janus_CE
            if getognmodel(ident[3:9]):     # write the model
                fd.write('HFGTYGLIDERTYPE:'+getognmodel(ident[3:9])+'\n')
            #HFCIDCOMPETITIONID:K5
            fd.write('HFIDCOMPETITION:'+compid+'\n')
            fd.write('HFCCLCOMPETITIONCLASS:'+classg+'\n')
            fd.write('HFPLTPILOTINCHARGE:'+pilotname+'\n')
            fd.write('LLXVFLARM:'+ident+'\n')
            ffd[ident] = fd                 # save the file descriptor
                                            # increase the number of records read
        fid[ident] += 1
#       ==============================================================================================================================
                                            # scan for the body of the APRS messag and generate the IGC B record    
        p1 = data.find(':/')+2
        if data[p1+6] == 'z':               # if date is Z with date
            hora = data[p1+2:p1+6]+'00'     # get HHMM
        else:
            hora = data[p1:p1+6]            # get the GPS time in UTC
        ep=data.find('!W')
        if (ep != -1):                      # get the extended position !Wxy!
            elat=data[ep+2]
            elon=data[ep+3] 
        else:                               # if not extended position, make it zero
            elat='0'
            elon='0'   
        lati = data[p1+7:p1+11]+data[p1+12:p1+14] + \
            elat+data[p1+14]                # get the latitude
        longi = data[p1+16:p1+21]+data[p1+22:p1+24] + \
            elon+data[p1+24]                # get the longitude
        altim = altitude                    # convert the altitude in meters
        if altim == None or (altim > 15000 or altim < 0):
            altim = 0
        alti = '%05d' % altim               # convert it to an string
        ffd[ident].write('B'+hora+lati+longi+'A00000'+alti + '\n')  # format the IGC B record
                                            # include the original APRS record for documentation
        ffd[ident].write('LGNE '+data)
#       ==============================================================================================================================

                                            # if we do not have the take off time ??
        cin += 1                            # one more record read
        nrecs += 1                          # one more record written
#-----------------------------------------------------------------
# end of while loop
#-----------------------------------------------------------------
except KeyboardInterrupt:		    # catching the ctrl-C 
    print("Keyboard input received, ignore and shutdown")
    pass
#                                          # if break of the while loop ... exit
                                           # report number of records read and files generated
shutdown(sock)
location.date = ephem.Date(datetime.utcnow())
if nerr > 0:
    print("\nNumber of errors:", nerr,"<<<<<\n")
print("Exit now ...", location.date, "\n=================================================================================================\n")
exit(0)
#
