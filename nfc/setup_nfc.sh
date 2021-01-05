#!/usr/bin/env bash

sudo mkdir /etc/nfc
cp libnfc.conf /etc/nfc/libnfc.conf

sudo apt-get update
sudo apt-get install libusb-dev libpcsclite-dev i2c-tools

cd ~
wget http://dl.bintray.com/nfc-tools/sources/libnfc-1.7.1.tar.bz2
tar -xf libnfc-1.7.1.tar.bz2

cd libnfc-1.7.1
./configure --prefix=/usr --sysconfdir=/etc
make
sudo make install

# http://wiki.sunfounder.cc/index.php?title=PN532_NFC_Module_for_Raspberry_Pi
