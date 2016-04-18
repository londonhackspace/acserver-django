# -*- mode: ruby -*-
# vi: set ft=ruby :

Vagrant.configure(2) do |config|
  config.vm.box = "debian/jessie64"
  config.vm.network "forwarded_port", guest: 3306, host: 3306
  config.vm.network "forwarded_port", guest: 1234, host: 1234
  config.vm.provision :shell, path: 'bootstrap.sh'
  config.vm.hostname = 'acserver-django-test'
end
