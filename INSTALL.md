## Development Setup
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/)

2. Clone and run [Real Time Scoring](https://github.com/acasadoalonso/RealTimeScoring.git)
   ```
   git clone https://github.com/acasadoalonso/RealTimeScoring.git RTSsrc
   cd RTSsrc/VM			# go to the VM provisioning directory
   vagrant up			# create and provision the VM machine
   ```
3. Adjust the configuration file /etc/local/RTSconfig.ini with the directory where to store the IGC files, and the SoaringSpot clientid/secretkey of the competition to run the Real Time Scoring, plus the OGC APRS parameters.
   The program connects with the OGN APRS network and gather all the fixes of all the gliders on the race, generating the IGC files used to score the race 
   ```
   vagrant ssh			# log into the VM machine
   nano /etc/local/RTSconfig.ini  
   ```
4. Execute the RTS script, go into the VM machine and ....

   ```
   vagrant ssh			# log into the VM machine
   cd ~/src/RTSsrc		# go to the directory where the scripts are
   bash RTS.sh 			# execute the RealTimeScoring script
   ```

5. The IGC files will be at the directory defined as root in the RTSconfig.ini file
   ```
