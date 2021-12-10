#!/usr/bin/env bash
echo "============================================================================"
echo " provisioning the VM machine"
echo " ==========================="
echo "============================================================================"
sudo apt-get update
sudo apt-get upgrade -y
sudo apt-get install -y neofetch git
mkdir -p /home/vagrant/src
cd       /home/vagrant/src
pwd
if [ -d RealTimeScoring ]
then
    rm -r RealTimeScoring RTSsrc
fi
echo "Clone the RTS repo"
git clone https://github.com/acasadoalonso/RealTimeScoring.git
ln -s RealTimeScoring RTSsrc
cd RTSsrc
sudo chown vagrant:vagrant -R . *
sudo chmod 775 -R . *
echo "Install now the RTS software"
echo "============================"
echo " "
bash install.sh
echo "============================================================================"
echo " end of provisioning the VM machine"
echo " =================================="
echo "============================================================================"
hostnamectl
echo "reboot now to get the version of the operating system"
sudo reboot

