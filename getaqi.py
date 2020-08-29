#!/usr/bin/env python3


# python3 -m pip install python-aqi
import aqi
import requests

import json
import subprocess
import sys
import time
import os


"""
The following is a list of the fields and a description of their values contained in the JSON data:

    "ID":1234, // PurpleAir sensor ID
    "ParentID":null, // The PurpleAir sensor ID of the "parent" entry in the case of Channel B
    "THINGSPEAK_PRIMARY_ID":"1234", // The Thingspeak channel ID for primary data of this sensor
    "THINGSPEAK_PRIMARY_ID_READ_KEY":"XXXX", // The Thingspeak read key for primary data of this sensor
    "Label":"name", // The "name" that appears on the map for this sensor
    "Lat":null, // Latitude position info
    "Lon":null, // Longitude position info
    "PM2_5Value":"1.07", // Current PM2.5 value (based on the
            "State":null,  // Unused variable
            "Type":"TYPE",  // Sensor type (PMS5003, PMS1003, BME280 etc)
            "Hidden":"true", // Hide from public view on map: true/false
            "Flag":null, // Data flagged for unusually high readings
            "DEVICE_BRIGHTNESS":"1", // LED brightness (if hardware is present)
            "isOwner":1, // Currently logged in user is the sensor owner
            "A_H":null, // true if the sensor output has been downgraded or marked for attention due to suspected hardware issues
            "temp_f":"xx",  // Current temperature in F
            "humidity":"xx", // Current humidity in %
            "pressure":"xx", // Current pressure in Millibars
            "AGE":29831, // Sensor data age (when data was last received) in minutes
            "THINGSPEAK_SECONDARY_ID":"1234", // The Thingspeak channel ID for secondary data of this sensor
            "THINGSPEAK_SECONDARY_ID_READ_KEY":"XXXX", // The Thingspeak read key for secondary data of this sensor
            "LastSeen":1490309930, // Last seen data time stamp in UTC
            "Version":"2.47c", // Current version of sensor firmware
            "LastUpdateCheck":1490308331, // Last update checked at time stamp in UTC
            "Uptime":"5210", // Sensor uptime in seconds
            "RSSI":"-68", // Sensor's WiFi signal strength in dBm

            "Stats": // Statistics for PM2.5

            "{
            \"v\":1.07, // Real time or current PM2.5 Value
            \"v1\":1.3988595758168765, // Short term (10 minute average)
            \"v2\":10.938131480857114, // 30 minute average
            \"v3\":15.028685608345926, // 1 hour average
            \"v4\":6.290537580116773, // 6 hour average
            \"v5\":1.8393146177050788, // 24 hour average
            \"v6\":0.27522764912064507, // One week average
            \"pm\":1.07, // Real time or current PM2.5 Value
            \"lastModified\":1490309930933, // Last modified time stamp for calculated average statistics
            \"timeSinceModified\":69290 // Time between last two readings in milliseconds
            }"
            }
"""


def convert(s):
    return int(aqi.to_iaqi(aqi.POLLUTANT_PM25, s, algo=aqi.ALGO_EPA))

def getpurpleair(id):
    data = requests.get("https://www.purpleair.com/json?show=%s" % id)
    results = (data.json())['results'][0]

    #if results["AGE"] > 5:  #  Sensor data age (when data was last received) in minutes
    #    print("stale")
    #    return None

    stats = json.loads(results['Stats'])

    aqi = convert(stats["v1"])
    aqi6h = convert(stats["v4"])

    aqirealtime = convert(stats["v"])

    age = results["AGE"]

    if age > 5:
        rows = [
           'cur %s' % aqirealtime,
           '10m %s' % aqi,
           "%sm ago" % results["AGE"],
           results['Label'],
        ]
    else:
        rows = [
            'AQI %s' % aqirealtime,
            '10m avg', 
            '  %s' % aqi,
            '6Hav %s' % aqi6h,
        ]

    return max([aqi, aqirealtime]), rows

def getrows(sensor_id):
    
    aqi, rows = getpurpleair(sensor_id)
    print("%s" % rows)

    return aqi, rows


def main(sensor_id):
    testmode = False
    aqi = 0

    while True:
        if testmode:
            aqi = aqi + 10
            rows = ["aqi %s" % aqi] * 4
            print(aqi)
        else:
            aqi, rows = getrows(sensor_id)

        percent = (100.0 - aqi) / 100
        percent = min([1, percent])
        percent = max([0, percent])

        rgb = min([255, int(255 * (1 - percent))]), min([255, int(255 * percent)]), 0

        current_path = os.path.dirname(os.path.realpath(__file__))

        p = subprocess.Popen(
            [
                os.path.join(current_path, 'text-example'),
                '-f', os.path.join(current_path, '4x6.bdf'),
                '-b', '50',
                '-C', '%s,%s,%s' % rgb,
            ],
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL)
        for r in [" %s" % time.strftime("%I:%M")] + rows:
            p.stdin.write(("%s\n" % r).encode())
        p.stdin.flush()

        if testmode:
            time.sleep(1)
        else:
            time.sleep(60 - int(time.time()) % 60)

        p.communicate()
        p.wait()


if __name__ == "__main__":
    main(sys.argv[1])

