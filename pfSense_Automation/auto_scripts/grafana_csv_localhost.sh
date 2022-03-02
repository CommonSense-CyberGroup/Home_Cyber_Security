#!/bin/sh



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
  cd / && python3 -m http.server 8111 --bind 127.0.0.1
fi
