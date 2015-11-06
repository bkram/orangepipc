#!/usr/bin/env python
import os
import time
import thread
import daemon

# Define sys files
tempfile = '/sys/devices/virtual/thermal/thermal_zone0/temp'
redled = '/sys/class/gpio_sw/normal_led/data'
greenled = '/sys/class/gpio_sw/standby_led/data'

# Changeable settings
sleeptime = 1
temptreshold = 60
loadtreshold = 1


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
        temp = int(open(tempfile, 'r').readline().strip('\n'))

        if temp >= temptreshold:
            for x in range(0, 1):
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
        time.sleep(1)

if __name__ == "__main__":
    main()
