##################################################################################################################################################
# This script sends inputs to the APPJ setup and collects the respective measurements to be used for model identification. 
# Inputs:
# * Sequence of applied power (u1)
# * Sequence of Helium flow rate (u2) 
#
# Outputs:
# * 2D surface temperature distribution
# * Optical intensity spectrum
#
# REQUIREMENTS:
# * Python 3
# * APPJPythonFunctions.py
# * APPJConstants.py
##################################################################################################################################################

# Import libraries
import sys
import argparse
from seabreeze.spectrometers import Spectrometer, list_devices
import numpy as np
import matplotlib.pyplot as plt
import time
import os
from applescript import tell
import subprocess
import serial
from APPJPythonFunctions import*


##################################################################################################################################################
# USER INPUTS
##################################################################################################################################################
arduinoAddress = '/dev/cu.usbmodem1434301'
# Move constants to APPJConstants.py file so that they are separate!
dutyCycle = 100
tSampling = 0.5

# Define input sequence for model identification
#u1Vec = [...]
#u2Vec = [...]

##################################################################################################################################################
# MAIN SCRIPT
##################################################################################################################################################

# Print a line to quickly spot the start of the output
print('\n--------------------------------------------')

# Check that the number of arguments is correct
NUMARG = 2
if len(sys.argv)!=numArg:
	print("Function expects "+str(NUMARG-1)+" argument(s). Example: [...]")
	exit()

# Define arduino address
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400,timeout=1)

# Obtain the spectrometer object
devices = list_devices()
print(devices)
spec = Spectrometer(devices[0])

# Obtain thermal camera object
# !!!!!!!! TO DO !!!!!!!!!!
# [...]
# [...]
# [...]

y1Save = []
y2Save = []

for i in range(len(u1Vec)):

	# Send inputs
	send_inputs_all(arduinoPI(u1Vec[i],u2Vec[i],dutyCycle) 
	
	# Obtain and save temperature measurements
	# !!!!!	TO DO !!!!!
	# [...]
	# [...]
	y1Save += []

	# Obtain and save intensity measurements
	intensitySpectrum=spec.intensities()/NORMALIZATION  #NORMALIZATION is defined in APPJPuthonFunctions.py
	totalIntensity = sum(intensitySpectrum)
	y2Save += []
	# Pause for the duration of the sampling time to allow the system to evolve
	time.sleep(tSampling)
