"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: grand_prix_layer2.py

Title: GRAND PRIX!!!!

Author: BWSI Team 4 2024

Purpose: Write a script to enable fully autonomous behavior from the RACECAR. The
RACECAR should automatically identify the color of a line it sees, then drive on the
center of the line throughout the obstacle cour ???se. The RACECAR should also identify
color changes, following colors with higher priority than others. Complete the lines 
of code under the #TODO indicators to complete the lab.

runs as fast as possible to the finish line
"""

########################################################################################
# Imports
########################################################################################

import sys
import cv2 as cv
import numpy as np

# If this file is nested inside a folder in the labs folder, the relative path should
# be [1, ../../library] instead.
sys.path.insert(1, "../../library")
import racecar_core
import racecar_utils as rc_utils

########################################################################################
# Global variables
########################################################################################
totaltime = 0
rc = racecar_core.create_racecar()

# >> Constants
# The smallest contour we will recognize as a valid contour
MIN_CONTOUR_AREA = 30

# A crop window for the floor directly in front of the car
CROP_FLOOR = ((360, 0), (rc.camera.get_height(), rc.camera.get_width()))

BLUE = ((105, 255, 255), (105, 255, 255)) 
GREEN = ((64, 255, 255), (64, 255, 255)) 
RED = ((0, 255, 255), (0, 255, 255))
COLOR_PRIORITY = (GREEN, RED, BLUE)

# >> Variables
speed = 0.0 
angle = 0.0  
contour_center = None  
contour_area = 0  
last_color = ""
cur_color = ""
red = 0
last_time = 0
last_time2 = 0
green = False
greenc = 0
found = False
########################################################################################
# Functions
########################################################################################

def update_contour():
    global COLOR_PRIORITY
    global contour_center
    global contour_area
    global cur_color
    global speed
    global angle
    image = rc.camera.get_color_image()
    if(red >= 2 and cur_color != "red"):
        COLOR_PRIORITY = (GREEN, BLUE)
    if image is None:
        contour_center = None
        contour_area = 0
    else:
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])
        found = False
        for color in COLOR_PRIORITY:
            contours = rc_utils.find_contours(image, color[0], color[1])
            contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
            if contour is not None:
                if not found or cv.contourArea(contour) > contour_area:
                    contour_center = rc_utils.get_contour_center(contour)
                    contour_area = rc_utils.get_contour_area(contour)
                    found = True
                    if color == RED:
                        cur_color = "red"
                    elif color == BLUE and cv.contourArea(contour) > 2000 and cv.contourArea(contour) < 3000:
                        continue
                    elif color == BLUE:
                        cur_color = "blue"
                    elif color == GREEN:
                        cur_color = "green"
                    break
        
        if found:      
            rc_utils.draw_contour(image, contour)
            rc_utils.draw_circle(image, contour_center)
    
        # Display the image to the screen
        rc.display.show_color_image(image)
        

# [FUNCTION] The start function is run once every time the start button is pressed
def start():
    global speed
    global angle
    global totaltime
    totaltime = 0
    # Initialize variables
    speed = 0
    angle = 0

    # Set initial driving speed and angle
    rc.drive.set_speed_angle(speed, angle)

    # Set update_slow to refresh every half second
    rc.set_update_slow_time(0.5)

    # Print start message
    print(
        "BOO NICE TRY"
    )

# [FUNCTION] After start() is run, this function is run once every frame (ideally at
# 60 frames per second or slower depending on processing speed) until the back button
# is pressed  
def remap_range(val: float, old_min: float, old_max: float, new_min: float, new_max: float) -> float:
    old_range = old_max - old_min
    new_range = new_max - new_min
    return new_range * (float(val - old_min) / float(old_range)) + new_min
def update():
    global totaltime
    global last_color
    global red
    global green
    global last_time
    global last_time2
    global COLOR_PRIORITY
    global speed
    global angle
    global contour_area
    global found
    global greenc
    totaltime += rc.get_delta_time()
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    if green and greenc == 1:
        rc.drive.set_max_speed(0.36)
    elif red == 1:
        rc.drive.set_max_speed(0.4)
    else:
        rc.drive.set_max_speed(0.5)
    # Search for contours in the current color image
    contour_area = 0
    update_contour()
    if cur_color != last_color:
        last_color = cur_color
        if cur_color == "red":
            red += 1
        if cur_color == "green":
            green = True
            greenc += 1
        else:
            green = False
    # TODO Part 3: Determine the angle that the RACECAR should receive based on the current 
    # position of the center of line contour on the screen. Hint: The RACECAR should drive in
    # a direction that moves the line back to the center of the screen.

    # Choose an angle based on contour_center
    # If we could not find a contour, keep the previous angle
    if contour_center is not None:
        setpoint = rc.camera.get_width() // 2
        error = -(setpoint - contour_center[1])
        #print(f"ERROR: {error}")
        angle = remap_range(error, -rc.camera.get_width()/2, rc.camera.get_width()/2, -1, 1)
        if((contour_area > 7700 and not found) or (totaltime - 0.7 <= last_time and last_time != 0)):
            if(angle < -0.6 or angle > -0.3):
                angle = abs(angle)
            if contour_area > 7700:
                last_time = totaltime
                found = True
        #print(f"ANGLE: {angle}")

    # Use the triggers to control the car's speed
    if contour_area > 0:
        speed = 1
    else:
        speed = -1
        angle = 1
    rc.drive.set_speed_angle(speed, angle)

    # Print the current speed and angle when the A button is held down
    if rc.controller.is_down(rc.controller.Button.A):
        print("Speed:", speed, "Angle:", angle, "GREEN:", green, "RED:", red, "COLOR:", cur_color)

    # Print the center and area of the largest contour when B is held down
    if rc.controller.is_down(rc.controller.Button.B):
        if contour_center is None:
            print("No contour found")
        else:
            print("Center:", contour_center, "Area:", contour_area)
    

# [FUNCTION] update_slow() is similar to update() but is called once per second by
# default. It is especially useful for printing debug messages, since printing a 
# message every frame in update is computationally expensive and creates clutter
def update_slow():
    ###
    '''
    After start() is run, this function is run at a constant rate that is slower
    than update().  By default, update_slow() is run once per second
    """
    # Print a line of ascii text denoting the contour area and x-position
    if rc.camera.get_color_image() is None:
        # If no image is found, print all X's and don't display an image
        print("X" * 10 + " (No image) " + "X" * 10)
    else:
        # If an image is found but no contour is found, print all dashes
        if contour_center is None:
            print("-" * 32 + " : area = " + str(contour_area))

        # Otherwise, print a line of dashes with a | indicating the contour x-position
        else:
            s = ["-"] * 32
            s[int(contour_center[1] / 20)] = "|"
            print("".join(s) + " : area = " + str(contour_area))
    '''


########################################################################################
# DO NOT MODIFY: Register start and update and begin execution
########################################################################################

if __name__ == "__main__":
    rc.set_start_update(start, update, update_slow)
    rc.go()
