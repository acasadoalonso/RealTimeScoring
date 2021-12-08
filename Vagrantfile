# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure("2") do |config|
  config.vm.box = "ubuntu/focal64"
  config.vm.boot_timeout = 600
  config.vm.provision :shell, path: "bootstrap.sh"
  config.vm.network "forwarded_port", guest: 80, host: 8686
  $default_network_interface = `ip route | awk '/^default/ {printf "%s", $5; exit 0}'`
  config.vm.network "public_network", bridge: "#$default_network_interface"

  config.vm.provider "virtualbox" do |vb|
    vb.customize ['modifyvm', :id, '--natdnshostresolver1', 'on']
    vb.customize ['modifyvm', :id, '--ioapic', 'on']
    vb.customize ['modifyvm', :id, '--audio', 'none']
    vb.customize ["modifyvm", :id, "--usb", "on"]
    vb.customize ["modifyvm", :id, "--usbxhci", "on"]
    vb.name = "RTSUBU" 
  end
  # Windows Support
  if Vagrant::Util::Platform.windows?
      config.vm.provision "shell",
      inline: "echo \"Converting Files for Windows\" && sudo apt-get install -y dos2unix && cd /var/www/html && dos2unix  * && dos2unix main/* && dos2unix main/sh/*",
      run: "always", privileged: false
  end
  config.vm.synced_folder "/nfs",   "/nfs/"

end

