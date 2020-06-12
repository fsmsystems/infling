#!/usr/bin/python3
import subprocess,requests,platform,time,socket
from influxdb import InfluxDBClient

#pip install influxdb
#python3-influxdb

# InfluxDB Parameters
influxdb_host='192.168.1.5'
port=8086
dbname='pyping'

# Ping host
hostping=['8.8.8.8','1.1.1.1']

# http checks
http_urls=['https://www.google.es','https://lo.caixabank.es','http://www.tintaroja.cat','https://m.caixabank.es']
timeout=60

# whoami?
location=platform.node()

print('Testing from: ' +location)

# resolvehost
resolvehost=['www.caixabank.es','www.google.es']


# Influxdb Connection
client = InfluxDBClient(host=influxdb_host, port=port)
client.create_database('pyping')
client.switch_database('pyping')

for r in resolvehost:
   dns_start = time.time()
   ip_address = socket.gethostbyname(r)
   dns_end = time.time()
   dns_dif = dns_end - dns_start
   print('Resolving: '+r+' in: ' + str(dns_dif) +'')
   dnsEvent = [{"measurement":"dns",
           "tags": {
               "Location": location,
               "RemoteHost": r,

           },
           "fields":
           {
           "dnstime":dns_dif
           }
           }
           ]

   client.write_points(dnsEvent)


for host in hostping:
   ping_response = subprocess.Popen(["/bin/ping", "-c1", host], stdout=subprocess.PIPE).stdout.read()
   ping_parse_time = float(str(ping_response).split('time=')[1].split(' ms')[0])
   print('ping: '+host+' time: ' + str(ping_parse_time) +' ms')
   pingEvent = [{"measurement":"pings",
           "tags": {
               "Location": location,
               "RemoteHost": host,

           },
           "fields":
           {
           "pingtime":ping_parse_time
           }
           }
           ]

   client.write_points(pingEvent)

for url in http_urls:
   # Checks with get 
   response = requests.get(url,timeout=timeout)
   # Evalueate if is 200 ok response
   if (response.status_code == requests.codes.ok):
      # Get the elapsed response time 
      rtime = response.elapsed.total_seconds()
      print('http request: '+url+' time: '+str(rtime)+' s')
      # Construct the json for influxdb
      httpEvent = [{"measurement":"http_request",
              "tags": {
                  "Location": location,
                  "Url": url,

              },
              "fields":
              {
              "Response_time":rtime
              }
              }
              ]

      client.write_points(httpEvent)
   else:
      # In case of HTTP response is not 200
      print('Error HTTP')
      httpEvent = [{"measurement":"http_request",
              "tags": {
                  "Location": "BCN",
                  "Url": url,

              },
              "fields":
              {
              "Response_time":'NULL'
              }
              }
              ]

      client.write_points(httpEvent)

