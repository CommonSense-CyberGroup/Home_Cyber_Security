#!/bin/sh
#
#By:
# Common Sense Cyber Group
# Some Guy they call Scooter
#
#Version: 1.0.1
#License: MIT
#Created: 3/2/2022
#Updated: 3/2/2022
#
#Purpose:
#This script is intended to open a port on the localhost pfSense box to be used to serve CSV and JSON files to the Infinity Grafana datasource


#Define Variables
open_port=$(netstat -tulpn | grep 8111)
open_var='LISTEN'

#Do the thing
if [[ "$open_port" == *"$open_var"* ]]
  then
  #All is good, so exit
  exit 0

else
  #Port is not open. Open port using python
  cd / && python3.8 -m http.server 8111 --bind 127.0.0.1
fi
