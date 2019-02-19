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
        r = requests.get(ping_url, timeout= 60)
    except requests.exceptions.ConnectTimeout as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err).__name__
    except requests.exceptions.ConnectionError as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err).__name__
    except requests.exceptions.TooManyRedirects as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err).__name__
    except requests.exceptions.ReadTimeout as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err).__name__
    except Exception as err:
        json_body[0]['fields']['exception'] = True
        json_body[0]['fields']['exception_type'] = type(err).__name__
        print("Unknow exception: ", type(err).__name__, err.args)
    else:
        pingTime = t.clock()
        json_body[0]['fields']['status_code'] = r.status_code
        json_body[0]['fields']['ping_time'] = pingTime
        if r.status_code == requests.codes.ok:  # Status = 200
            json_body[0]['fields']['success'] = True
            print( "ping to", ping_url, "OK")
            print("Duration: ", pingTime, "s")
        else:
            json_body[0]['fields']['success'] = False
            print( "ping to", ping_url, "failed with HTTP status code ", r.status_code)
    finally:
        client.write_points(json_body)

    time.sleep(10)
# Or check if to use cron instead of forever-loop: https://www.jetbrains.com/help/pycharm/remote-development-on-raspberry-pi.html
    
