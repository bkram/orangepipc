#!/usr/bin/env python
# (c) 2016 bkram, GPL see LICENSE file
import os
import thread
import time
import daemon
import sys

'''
Use the Orange Pi PC onboard LEDs to monitor system load and cpu temperature.
The red LED lights up when the system load exceeds 1.
The green LED will light up when the daemon is run and it will blink when the temperature exceeds 60 degrees Celsius.
Changeable settings below.
'''

# Changeable settings
sleeptime = 1
temptreshold = 60
loadtreshold = 1

# Define sys files
tempzonea = '/sys/devices/virtual/thermal/thermal_zone0/temp'
tempzoneb = '/sys/devices/virtual/thermal/thermal_zone1/temp'
redled = '/sys/class/gpio_sw/normal_led/data'
greenled = '/sys/class/gpio_sw/standby_led/data'


def checkroot():
    # check if we are being run as root
    if not os.geteuid() == 0:
        print 'leddaemon.py requires to be run as root'
        sys.exit(1)


def setled(led, state):
    # Turn on / off a LED
    f = open(led, 'w')
    f.write(str(state))
    f.close()


def setup():
    # Turn off all LED'S first
    setled(greenled, 0)
    setled(redled, 0)


def check_load(lock, *args):
    # Check load, and turn on red led if treshold is exceeded.
    while True:
        if os.getloadavg()[0] >= loadtreshold:
            setled(redled, 1)
        else:
            setled(redled, 0)
        time.sleep(sleeptime)


def check_temp(lock, *args):
    # Check temperature, and blink green led if treshold is exceeded.
    while True:
        tempa = int(open(tempzonea, 'r').readline().strip('\n'))
        tempb = int(open(tempzoneb, 'r').readline().strip('\n'))
        temp = (tempa + tempb) / 2

        if temp >= temptreshold:
            setled(greenled, 0)
            time.sleep(.6)
            setled(greenled, 1)
            time.sleep(.6)
        else:
            setled(greenled, 1)
        time.sleep(sleeptime)


def main():
    # Launch daemonized.
    setup()
    with daemon.DaemonContext():
        monitor()


def monitor():
    # Start Threads..
    lock = thread.allocate_lock()
    thread.start_new_thread(check_load, (1, lock))
    thread.start_new_thread(check_temp, (1, lock))
    while True:
        time.sleep(60)


if __name__ == "__main__":
    checkroot()
    main()
