#!/usr/bin/python3
# -------------------------------------
# OGN-RTS
# -------------------------------------
#
# -------------------------------------
# Setting values
# -------------------------------------
#
import socket
import os
from configparser import ConfigParser
# check if the environment variable CONFIFDIR is set ?
configdir = os.getenv('CONFIGDIR')
if configdir is  None:
    configdir = '/etc/local/'
configfile = configdir+'RTSconfig.ini'  # name of the configuration file
hostname = socket.gethostname()
processid = str(os.getpid())
if os.path.isfile(configfile):		# check if we have configuration file ???
    cfg = ConfigParser()		# get the configuration parameters
    cfg.read(configfile)		# reading it for the configuration file
else:
    print("Config file: ", configfile, " not found \n")
    exit(-1)			# nothing to do
#
# -------------SERVER-------------------------#
#
datapath = cfg.get('server', 'root').strip("'").strip('"')
try:
    PIDfile = cfg.get('server', 'pid').strip("'").strip('"')
except:
    PIDfile = '/tmp/SWS.pid'

try:
    prttext = cfg.get('server', 'prt').strip("'")
    if (prttext == 'False'):
        prt = False
    else:
        prt = True
except:
    prt = False

try:
    DDBhost = cfg.get('server', 'DDBhost').strip("'")
except:
    DDBhost = 'DDB.glidernet.org'

try:
    DDBport = cfg.get('server', 'DDBport').strip("'")
except:
    DDBport = '80'

try:
    DDBurl1 = cfg.get('server', 'DDBurl1').strip("'")
except:
    DDBurl1 = 'http://DDB.glidernet.org/download/?j=2'

try:
    DDBurl2 = cfg.get('server', 'DDBurl2').strip("'")
except:
    DDBurl2 = 'http://acasado.es:60082/download/?j=2'

try:
    clientid = cfg.get('server', 'clientid').strip("'")
except:
    clientid = ''

try:
    secretkey = cfg.get('server', 'secretkey').strip("'")
except:
    secretkey = ''

#
# -------------APRS-------------------------#
#

APRS_SERVER_HOST = cfg.get('APRS', 'APRS_SERVER_HOST').strip("'").strip('"')
APRS_SERVER_PORT = int(cfg.get('APRS', 'APRS_SERVER_PORT'))
APRS_USER = cfg.get('APRS', 'APRS_USER').strip("'").strip('"')
# See http://www.george-smart.co.uk/wiki/APRS_Callpass
APRS_PASSCODE = int(cfg.get('APRS', 'APRS_PASSCODE'))
APRS_FILTER_DETAILS = cfg.get(
    'APRS', 'APRS_FILTER_DETAILS').strip("'").strip('"')
APRS_FILTER_DETAILS = APRS_FILTER_DETAILS + '\n '

#
# -------------LOCATION-------------------------#
#
location_latitude = cfg.get(
    'location', 'location_latitude').strip("'").strip('"')
location_longitude = cfg.get(
    'location', 'location_longitud').strip("'").strip('"')
try:
    location_name = cfg.get('location', 'location_name').strip("'").strip('"')
except:
    location_name = ' '

# -------------------------------------------------------------------------------#
APP = 'RTS'
# --------------------------------------#
assert len(APRS_USER) > 3 and len(str(APRS_PASSCODE)
                                  ) > 0, 'Please set APRS_USER and APRS_PASSCODE in settings.py.'

# --------------------------------------#
# report the configuration paramenters
if prt:
    print("\n\n")
    print("Config file used:    ",
          configfile, hostname, processid)
    print("Config APRS values:  ",                  APRS_SERVER_HOST,
          APRS_SERVER_PORT, APRS_USER, APRS_PASSCODE, APRS_FILTER_DETAILS)
    print("Config location :    ",                  location_name,
          location_latitude, location_longitude)
# --------------------------------------#
