#!/usr/bin/env bash

sudo mkdir /etc/nfc
cp libnfc.conf /etc/nfc/libnfc.conf

sudo apt-get update
sudo apt-get install libusb-dev libpcsclite-dev i2c-tools libnfc-examples
