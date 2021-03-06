#!/usr/bin/env python
# -*- coding: utf-8 -*-

from dronekit import connect, VehicleMode, LocationGlobalRelative
import time
import dronekit_sitl

#Set up option parsing to get connection string
import argparse  
parser = argparse.ArgumentParser(description='Commands vehicle using vehicle.simple_goto.')
parser.add_argument('--connect', 
                   help="Vehicle connection target string. If not specified, SITL automatically started and used.")
parser.add_argument('--altitude', 
                   help="Target release altitude defaults to 100m.", default=100,type=int)
parser.add_argument('--hover', 
                   help="Time to hover at release altitude, defaults to 30 seconds.", default=30, type=int)
parser.add_argument('--benchtest', 
                   help="Run as a sitl script", action="store_true");
args = parser.parse_args()

connection_string = args.connect
target_height = args.altitude
benchtest = args.benchtest
hover_time = args.hover

if not target_height:
    target_height = 10

connection_string = "/dev/serial0"

# sitl = dronekit_sitl.start_default()
# connection_string = sitl.connection_string()
if benchtest:
    print("Running benchtest script to connect to SITL")
    connection_string = "udp:127.0.0.1:5769"

# Connect to the Vehicle
print 'Connecting to vehicle on: %s' % connection_string
vehicle = connect(connection_string, wait_ready=True, baud=57600)

def arm_and_takeoff():
    """
    Arms vehicle and fly to aTargetAltitude.
    """

    aTargetAltitude = 120

    print "Basic pre-arm checks"
    # Don't try to arm until autopilot is ready
    while not vehicle.is_armable:
        print " Waiting for vehicle to initialise..."
        time.sleep(1)

    if benchtest:
        vehicle.mode = VehicleMode("GUIDED")

    print " Waiting for mode change ..."
    while not vehicle.mode.name=='GUIDED':  #Wait until mode has changed
        print " Waiting for GUIDED mode..."
        time.sleep(1)

    print("Waiting 15 seconds, just in case in GUIDED mode when safety switch pressed")
    time.sleep(15)

    print "Arming motors"
    vehicle.armed = True    

    # Confirm vehicle armed before attempting to take off
    while not vehicle.armed:      
        print " Waiting for arming..."
        time.sleep(1)

    if True:
        print "Taking off! Aiming for %sm" % aTargetAltitude
        vehicle.simple_takeoff(aTargetAltitude) # Take off to target altitude

        # Wait until the vehicle reaches a safe height before processing the goto (otherwise the command 
        #  after Vehicle.simple_takeoff will execute immediately).
        while True:
            print " Altitude: ", vehicle.location.global_relative_frame.alt 
            #Break and return from function just below target altitude.        
            if vehicle.location.global_relative_frame.alt>=aTargetAltitude*0.95: 
                print("Reached target altitude, hovering for %s seconds" % hover_time)
                time.sleep(hover_time)
                break
            time.sleep(1)

arm_and_takeoff()

print "Returning to Launch"
vehicle.mode = VehicleMode("RTL")

while not vehicle.mode.name=='RTL':
    print " Waiting for RTL mode..."
    time.sleep(1)

#Close vehicle object before exiting script
print "RTL Mode. Closing vehicle object"
vehicle.close()

