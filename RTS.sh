#!/bin/sh
if [ -z $CONFIGDIR ]
then 
     export CONFIGDIR=/etc/local/
fi
DBpath=$(echo    `grep '^root '   $CONFIGDIR/RTSconfig.ini` | sed 's/=//g' | sed 's/^root //g' | sed 's/ //g' )
# DBpath point to the directory where the IGC filess generated will be stored ....
SCRIPT=$(readlink -f $0)
SCRIPTPATH=`dirname $SCRIPT`


if [ ! -d $DBpath ]
then
	echo "... no SWdata directory yet ..."
	sleep 180
	ls -la $DBpath
fi
cd $DBpath
pwd
echo $(hostname)" running RTS.sh:" 		>>RTSproc.log
python3 $SCRIPTPATH/RTS.py			>>RTSproc.log &
