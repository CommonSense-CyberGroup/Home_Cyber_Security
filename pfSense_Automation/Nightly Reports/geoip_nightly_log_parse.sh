#!/bin/sh
#
#By:
# Common Sense Cyber Group
# Some Guy they call Scooter
#
#Version: 1.0.1
#License: MIT
#Created: 2/26/2022
#Updated: 3/1/2022
#
#Purpose:
#This script is intended to pull out the pfBolckerNG logs (by FW rule ID) from the FW log file. This will pull out the previous days
#logs for parsing and reporting on by the geoip_nightly_report.py script. 
#This script will also auto-download the MaxMing GeoIP2 databases so they are always up to date for creating our map.

#Download the country and city MaxMind Databases
#curl https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_LICENSE_KEY&suffix=tar.gz
#curl https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key=YOUR_LICENSE_KEY&suffix=tar.gz

#Unzip the MaxMind DB files

#Remove the downloaded tarballs to stay clean and not take up space

#Define yesterdays date
ydate=$(date -v-1d +"%b %d")

#Create geoip file from yesterdays logs
cat /var/log/filter.log | grep "$ydate" | grep -E "1770008959|1770009276" > nightly_geoip_log.txt

#Create the snort log file from yesterdays logs
cat /var/log/system.log | grep "$ydate" | grep "snort" > nightly_snort_log.txt

#Call the geoip_nightly_report.py script to create the report and email out
python ./geoip_nightly_report.py

#Rotate the log files so we have a backup of them to gather over time
mv nightly_geoip_log.txt rotated_logs/"ydate"_nightly_geoip_log.txt
mv nightly_snort_log.txt rotated_logs/"ydate"_nightly_snort_log.txt

#Delete rotated logs if they are older than 31 days
