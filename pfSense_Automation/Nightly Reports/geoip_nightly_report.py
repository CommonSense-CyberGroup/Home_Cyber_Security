#!/bin/python3
'''
TITLE: GeoIP Blocker Report
BY:
    Common Sense Cyber Group
    Some Guy they call Scooter

Version: 1.0.1

License: MIT

Created: 2/25/2022
Updated: 2/26/2022

Purpose:
    -This script is intended to give a daily report of blocked GeoIPs from a pfSense FW using pfBlockerNG. This script is to be run manually and will email the 
    previous days results along with an HTML map depicting the locations of IPs

Considerations:
    -Log grep string: ydate=$(date -v-1d +"%b %d") && cat /var/log/filter.log | grep "$ydate" | grep "1770008959" > nightly_geoip_log.txt
    -The above command will be run via a bash script, which will then call this python script once it is finished to parse through the data for the report
    -The bash script will be run as a cron job on the FW at 00:01 each night to gather the previous days blocked info
    -The bash script will download a new copy of the MaxMind country and city GeoIP2 DB each time it runs so it is always up to date. This script will delete it after every run so it does not make copies
        https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-City&license_key=YOUR_LICENSE_KEY&suffix=tar.gz
        https://download.maxmind.com/app/geoip_download?edition_id=GeoLite2-Country&license_key=YOUR_LICENSE_KEY&suffix=tar.gz

To Do / Notes:

'''


### IMPORT LIBRARIES ###
import geoip2.database
import folium
import datetime
import requests
import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email import encoders


### DEFINE VARIABLES ###
ip_addr = []    #List of IPs from log to parse through
countries = []  #List of countries that tried to connect to FW
unique_countries = []   #List of unique countries to count
lat_list = []    #Latitude values for mapping
lon_list = []    #Longitude values for mapping
country_count = []  #Final list of coutries and their count
total_blocked = 0  #Total number of blocker connections for the day
current_ip = requests.get('https://api.ipify.org').content.decode('utf8')
log = "nightly_geoip_log.txt"
map_file = f'{((datetime.date.today()) - datetime.timedelta(days=1)).strftime("%b-%d-%Y")}_GeoIP_Log_Map.html'
config_file = "geoip_report.conf"
max_mind_country = "GeoLite2-Country_20220222\\GeoLite2-Country.mmdb"
max_min_city = "GeoLite2-City_20220222\\GeoLite2-City.mmdb"

### CLASSES AND FUNCTIONS ###
#Parse config file to get info needed for alerting
def parse_config():
    with open(config_file) as file:
        rows = file.readlines()

        for row in rows:
            #Pull out the list of people to alert
            if "from_email" in row:
                email = row.split(":")[1]

            #Pull out the alert email and password
            if "alert_email" in row:
                alert_email = row.split(":")[1]

            if "alert_passwd" in row:
                alert_password = row.split(":")[1]

    return email, alert_email, alert_password

#Function for mapping
def map():
    #Define the map object
    map = folium.Map()

    #Loop through all the data we have and map the points
    i = 0
    while i < len(lat_list):

        marker = folium.Marker(location=[lat_list[i],lon_list[i]], popup=f'IP Address: {ip_addr[i]}')
        marker.add_to(map)

        i += 1

    #Save the map
    map.save(map_file)

#Function to email report
def email_report():
    #Make our output a little prettier
    pretty_body = str(country_count).replace("[", "").replace("]", "").replace("', '", "\n").replace("'", "")

    #Create message to send
    message_beginning = """
    -- Aria Daily GeoIP Blocked Report --
    """

    #Set the message up
    message = MIMEMultipart()
    message["From"] = email
    message['To'] = alert_email
    message['Subject'] = "Aria Daily GeoIP Blocked Report"

    #Attach the file and body
    attachment = open(map_file, 'rb')
    obj = MIMEBase('application', 'octet-stream')
    obj.set_payload((attachment).read())
    encoders.encode_base64(obj)
    obj.add_header('Content-Disposition',"attachment; filename= " + map_file)
    message.attach(obj)
    message.attach(MIMEText(f'{message_beginning}Below are the countries and counts of blocked requests for {((datetime.date.today()) - datetime.timedelta(days=1)).strftime("%b-%d-%Y")}:\n\nTotal Blocked: {total_blocked}\n\n{pretty_body}', 'plain', 'utf-8'))
    email_message = message.as_string()

    #Start the email session and sent it
    email_session = smtplib.SMTP('smtp.gmail.com', 587)
    email_session.starttls()
    email_session.login(email, alert_password)
    email_session.sendmail(email, alert_email, email_message)
    email_session.quit()


### THE THING ###
#Parse config
email, alert_email, alert_password = parse_config()

#Open log file and pull out all of the IPs. Add them to a list, and remove any duplicates
with open (log, "r") as log_file:
    for row in log_file:

        if row.split(",")[18] != current_ip:
            if row.split(",")[18] not in ip_addr:
                ip_addr.append(row.split(",")[18])

        else:
            if row.split(",")[19] not in ip_addr:
                ip_addr.append(row.split(",")[19])

#Add all resolved countries to the countries list
with geoip2.database.Reader(max_mind_country) as country_reader:
    with geoip2.database.Reader(max_min_city) as city_reader:
        for ip in ip_addr:
            #Get the country of the ip
            countries.append(country_reader.country(ip).country.names["en"])

            #Pull out the lat/lon of the IP for mapping
            lat_list.append(city_reader.city(ip).location.latitude)
            lon_list.append(city_reader.city(ip).location.longitude)

#Make a list of unique countries seen
for country in countries:
    if country not in unique_countries:
        unique_countries.append(country)

#Loop through unique contries and count their occurrences from the logs
for item in unique_countries:
    country_count.append("{} - {}".format(item, countries.count(item)))

    #Add to the total blocked number
    total_blocked += countries.count(item) 

#Call functions for mapping and sending out the email
map()
email_report()

#Delete the files that were created to stay clean and not take up space on the server
os.remove(log)
os.remove(map_file)
os.remove(max_mind_country)
os.remove(max_min_city)