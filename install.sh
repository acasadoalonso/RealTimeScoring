#!/bin/bash 
echo								#
echo " "							#
echo " "							#
echo "========================================================" #
echo "Installing the Real Time Scoring interface ...." 		#
echo "========================================================" #
echo " "							#
echo " "							#
echo								#
if [ ! -f /tmp/commoninstall.sh ]				#
then								#
   echo "Installing the common software"			#
   echo "=============================="			#
   bash commoninstall.sh 					#
   echo "=============================="			#
fi								#
if [ ! -d /etc/local ]						#
then								#
    sudo mkdir /etc/local					#
    sudo chmod 777 /etc/local					#
fi								#
if [ ! -d ~/src  ]						#
then								#
	mkdir ~/src   						#
        if [ ! -d ~/src/RTSsrc  ]				#
        then							#
	   ln -s $(pwd) ~/src/RTSsrc				#
        fi							#
fi								#
echo " "							#
echo "================================================" 	#
echo " "							#
echo "Installing the templates needed  ...." 			#
echo "========================================================" #
echo " "							#
echo								#
sudo cp RTSconfig.ini.sample /etc/local/RTSconfig.ini		#
if [ ! -d /nfs/OGN/SWdata  ]					#
then								#
	echo							#
	echo "Adding user ogn ...	"			#
	echo "=============== ...	"			#
	sudo adduser ogn 					#
	sudo mkdir /nfs						#
	sudo mkdir /nfs/OGN					#
	sudo mkdir /nfs/OGN/SWdata				#
	sudo chown ogn:ogn /nfs/OGN/SWdata			#
	sudo chmod 777 /nfs/OGN/SWdata				#
	cd /var/www/html/					#
        ls -la 							#
fi								#
tail /var/log/syslog						#
touch RTSinstallation.done					#
echo " "							#
sudo apt-get -y dist-upgrade					#
sudo apt-get -y autoremove					#
echo								#
echo "========================================================"	#
echo								#
echo " "							#
echo " "							#
echo " ======================= END ==========================="	#
