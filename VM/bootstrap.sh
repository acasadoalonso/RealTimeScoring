#!/usr/bin/env bash
echo "============================================================================"
echo " provisioning the VM machine"
echo " ==========================="
echo "============================================================================"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y neofetch git
mkdir -p home/vagrant/src
cd /home/vagrant/src
pwd
rm -r RealTimeScoring RTSsrc
git clone https://github.com/acasadoalonso/RealTimeScoring.git
ln -s RealTimeScoring RTSsrc
cd RTSsrc
sudo chown vagrant:vagrant -R . *
sudo chmod 775 -R . *
bash install.sh
echo "============================================================================"
echo " end of provisioning the VM machine"
echo " =================================="
echo "============================================================================"
