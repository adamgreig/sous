# -*- coding: utf-8 -*-

import time
import json
import serial
import struct
import random
import requests
import threading

config = {"food": None, "temp": None, "time": None}
servers = ["http://localhost:5000"]
ct = {'Content-Type': 'application/json'}

def post_data(data):
    for server in servers:
        url = server + "/data"
        try:
            r = requests.post(url, data=data, timeout=3, headers=ct)
        except requests.exceptions.RequestException as e:
            print "ERROR:", url, e
        else:
            print url, r.text

class FakeSerial(object):
    def __init__(*args):
        pass
    def read(self, n):
        time.sleep(1)
        u = config["temp"]
        return "\xFF"+struct.pack("<H", int(random.gauss(u, 0.5)/0.0625))
    def write(self, d):
        return
serial.Serial = FakeSerial

def controller(preheat=False):
    print "Opening serial port to TinyPFC..."
    ser = serial.Serial("/dev/ttyUSB0", 38400)
    while True:
        rx = ser.read(3)
        if rx[0] != "\xFF":
            print "got unexpected byte :( hoping for the best & continuing..."
            ser.write("\xFF\x00")
            continue
        temp = float(struct.unpack("<BH", rx)[1]) * 0.0625
        t = time.time()
        print "Time:", time.strftime("%Y-%m-%dT%H:%M:%SZ")
        print "Temperature:", temp
        error = config["temp"] - temp
        print "Error:", error
        x = int((0.1 * error) * 100)
        if x > 100:
            x = 100
        if x < 0:
            x = 0
        print "Setting:", x
        ser.write("\xFF"+chr(x))
        if not preheat:
            print "Posting to servers..."
            args = [json.dumps([t, temp, x])]
            th = threading.Thread(target=post_data, args=args)
            th.start()
        print
        if preheat and abs(error) < 1.0:
            return

if __name__ == "__main__":
    config["food"] =       raw_input("What cook?         > ")
    config["temp"] = float(raw_input("How hot? (°C)      > "))
    config["time"] =       raw_input("How long? (hr:min) > ")
    hours, mins = config["time"].split(":")
    config["time"] = 3600 * int(hours) + 60 * int(mins)
    print "OK, preheating to {temp}°C. Please wait.".format(**config)
    controller(preheat=True)
    print "OK, posting config to servers..."
    for server in servers:
        url = server + "/config"
        r = requests.post(url, data=json.dumps(config), headers=ct)
        print url, r.text
    raw_input("OK, at temperature. Please insert food and press enter.")
    print "Cooking {food} at {temp}°C for {time}s...".format(**config)
    controller()
