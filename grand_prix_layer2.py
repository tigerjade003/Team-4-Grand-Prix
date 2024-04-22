"""
MIT BWSI Autonomous RACECAR
MIT License
racecar-neo-outreach-labs

File Name: lab_f.py

Title: Lab F - Line Follower

Author: Jaden Tang << [Write your name or team name here]

Purpose: Write a script to enable fully autonomous behavior from the RACECAR. The
RACECAR should automatically identify the color of a line it sees, then drive on the
center of the line throughout the obstacle cour ???se. The RACECAR should also identify
color changes, following colors with higher priority than others. Complete the lines 
of code under the #TODO indicators to complete the lab.

Expected Outcome: When the user runs the script, they are able to control the RACECAR
using the following keys:
- When the right trigger is pressed, the RACECAR moves forward at full speed
- When the left trigger is pressed, the RACECAR, moves backwards at full speed
- The angle of the RACECAR should only be controlled by the center of the line contour
- The RACECAR sees the color RED as the highest priority, then GREEN, then BLUE
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

# TODO Part 1: Determine the HSV color threshold pairs for GREEN and RED
# Colors, stored as a pair (hsv_min, hsv_max) Hint: Lab E!
BLUE = ((90, 100, 100), (120, 255, 255))  # The HSV range for the color blue
GREEN = ((40, 100, 100), (80, 255, 255))  # The HSV range for the color green
RED = ((0, 100, 100), (10, 255, 255))  # The HSV range for the color red
RED2 = ((165, 100, 100), (179, 255, 255))

# Color priority: Red >> GREEN >> BLUE
COLOR_PRIORITY = (GREEN, RED, RED2, BLUE)

# >> Variables
speed = 0.0  # The current speed of the car
angle = 0.0  # The current angle of the car's wheels
contour_center = None  # The (pixel row, pixel column) of contour
contour_area = 0  # The area of contour
last_color = ""
cur_color = ""
red = 0
last_time = 0
green = False
found = False
########################################################################################
# Functions
########################################################################################

# [FUNCTION] Finds contours in the current color image and uses them to update 
# contour_center and contour_area
def update_contour():
    global COLOR_PRIORITY
    global contour_center
    global contour_area
    global cur_color
    global speed
    global angle
    image = rc.camera.get_color_image()
    if(red >= 2):
        COLOR_PRIORITY = (GREEN, BLUE)
    if image is None:
        contour_center = None
        contour_area = 0
    else:
        # Crop the image to the floor directly in front of the car
        image = rc_utils.crop(image, CROP_FLOOR[0], CROP_FLOOR[1])

        # TODO Part 2: Search for line colors, and update the global variables
        # contour_center and contour_area with the largest contour found
        found = False
        for color in COLOR_PRIORITY:
            contours = rc_utils.find_contours(image, color[0], color[1])
            contour = rc_utils.get_largest_contour(contours, MIN_CONTOUR_AREA)
            if contour is not None:
                if not found or cv.contourArea(contour) > contour_area:
                    contour_center = rc_utils.get_contour_center(contour)
                    contour_area = rc_utils.get_contour_area(contour)
                    found = True
                    if color == RED or color == RED2:
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
    totaltime += rc.get_delta_time()
    """
    After start() is run, this function is run every frame until the back button
    is pressed
    """
    if not green:
        rc.drive.set_max_speed(0.5)
    elif red >= 2:
        rc.drive.set_max_speed(0.5)
    else:
        rc.drive.set_max_speed(0.36)
    global COLOR_PRIORITY
    global speed
    global angle
    global contour_area
    global found
    # Search for contours in the current color image
    contour_area = 0
    update_contour()
    if cur_color != last_color:
        last_color = cur_color
        if cur_color == "red":
            red += 1
        if cur_color == "green":
            green = True
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
        if((contour_area > 8000 and not found) or (totaltime - 0.6 <= last_time and last_time != 0)):
            angle = abs(angle)
            if contour_area > 8000:
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
        print("Speed:", speed, "Angle:", angle)

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
