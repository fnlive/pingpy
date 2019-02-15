#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Mon Feb 11

@author: fredrik
"""
import requests
import time
from influxdb import InfluxDBClient


class Timeit:
    def __init__(self):
        self.start_ts = time.time()
    
    def start(self):
        self.start_ts = time.time()

    def clock(self):
        return time.time()-self.start_ts

# Main
print( "Starting web-pinger...")

ping_url = 'http://annikaochtorkeliberg.se/'
host = 'localhost'
port = '8086'
"""Instantiate a connection to the InfluxDB."""
user = 'root'
password = 'root'
dbname = 'testpingdb'
dbuser = 'smly'
dbuser_password = 'my_secret_password'
t = Timeit()

# Expect db to exist
client = InfluxDBClient(host, port, user, password, dbname)

# Loop forever
while True:
    print("Pinging ", ping_url)
    json_body = [
        {
            "measurement": "pingstatus",
            "tags": {
                "host": ping_url
            },
            "fields": {
                "success": False, 
                "exception": False, 
                "exception_type": 'NA', 
                "status_code": 0, 
                "ping_time": 0.0
            }
        }
    ]
    t.start()
    try:
        r = requests.get(ping_url, timeout= 10)
    except requests.exceptions.ConnectTimeout as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = 'ConnectTimeout'
#        json_body[0]['fields']['exception_type'] = type(err)
        print("Timout error")
        print(type(err))
    except requests.exceptions.ConnectionError as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = "Connection error"
        print("Connection error")
        print(type(err))
    except requests.exceptions.TooManyRedirects as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err)
        print("TooManyRedirects error")
        print(type(err))
    except requests.exceptions.ReadTimeout as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err)
        print("ReadTimeout error")
        print(type(err))
    else:
        json_body[0]['fields']['status_code'] = r.status_code
#        print(r.status_code)
        if r.status_code == requests.codes.ok:
            pingTime = t.clock()
            json_body[0]['fields']['success'] = True
            json_body[0]['fields']['ping_time'] = pingTime
            print( "ping to", ping_url, "OK")
            print(f"Duration: {pingTime} s")
        else:
            print( "ping to", ping_url, "failed with HTTP status code ", r.status_code)
    finally:
        client.write_points(json_body)

    time.sleep(10)

