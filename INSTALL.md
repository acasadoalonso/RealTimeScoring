## Development Setup
1. Install [VirtualBox](https://www.virtualbox.org/wiki/Downloads) and [Vagrant](https://www.vagrantup.com/)

2. Clone and run [Real Time Scoring](https://github.com/acasadoalonso/RealTimeScoring.git)
   ```
   git clone https://github.com/acasadoalonso/RealTimeScoring.git RTSsrc
   cd RTSsrc/VM
   vagrant up
   vagrant ssh
   ```
3. Adjust the configuration file /etc/local/RTSconfig.ini with the directory where to store the IGC files, and the SoaringSpot clientid/secretkey of the competition to run the Real Time Scoring, plus the OGC APRS parameters.
   The program connects with the OGN APRS network and gather all the fixes of all the gliders on the race, generating the IGC files used to score the race 
   ```
