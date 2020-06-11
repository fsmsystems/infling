#!/usr/bin/python3
import subprocess
from influxdb import InfluxDBClient
#pip install influxdb
#python3-influxdb

#InfluxDB Parameters
influxdb_host='192.168.1.5'
port=8086
dbname='pyping'

#Ping host
hostping=['8.8.8.8','1.1.1.1']

for host in hostping:
   client = InfluxDBClient(host=influxdb_host, port=port)
   client.create_database('pyping')
   client.switch_database('pyping')

   ping_response = subprocess.Popen(["/bin/ping", "-c1", host], stdout=subprocess.PIPE).stdout.read()
   ping_parse_time = float(str(ping_response).split('time=')[1].split(' ms')[0])
   print(ping_parse_time)

   #client.write(['time='+ping_parse_time+'host='+host],{'db':dbname},204,'line')
   pingEvent = [{"measurement":"pings",
           "tags": {
               "Location": "BCN",
               "RemoteHost": host,

           },
           "fields":
           {
           "pingtime":ping_parse_time
           }
           }
           ]

   client.write_points(pingEvent)

