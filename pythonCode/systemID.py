##################################################################################################################################################
# This script sends inputs to the APPJ setup and collects the respective measurements to be used for model identification. 
# Inputs:
# * Sequence of applied power (u1)
# * Sequence of Helium flow rate (u2) 
#
# Outputs:
# * Minimum and maximum surface temperatures
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
import cv2
from datetime import datetime
from APPJPythonFunctions import*

#Generate timestamp
timeStamp = datetime.now().strftime('%Y_%m_%d_%H'+'h%M''m%S'+'s')
##################################################################################################################################################
# USER INPUTS
##################################################################################################################################################
arduinoAddress = '/dev/cu.usbmodem1434401'
# Move constants to APPJConstants.py file so that they are separate!
dutyCycle = 100
tSampling = 0.5		#in seconds
DeltaTimeInput = 30 #in seconds

# Define input sequence for model identification (u1: power; u2: flow)
u1Vec = np.linspace(1.5, 5, 5)
u2Vec = np.linspace(1.5, 5, 5)
uu1, uu2 = np.meshgrid(u1Vec, u2Vec);
u1Vec = uu1.reshape(1,-1)
u2Vec = uu2.reshape(1,-1)

u1Vec = np.repeat(u1Vec, DeltaTimeInput/tSampling).reshape(1,-1)
u2Vec = np.repeat(u2Vec, DeltaTimeInput/tSampling).reshape(1,-1)




##################################################################################################################################################
# MAIN SCRIPT
##################################################################################################################################################

# Print a line to quickly spot the start of the output
print('\n--------------------------------------------')

# Check that the number of arguments is correct
# NUMARG = 2
# if len(sys.argv)!=NUMARG:
# 	print("Function expects "+str(NUMARG-1)+" argument(s). Example: [...]")
# 	exit()

# Define arduino address
arduinoPI = serial.Serial(arduinoAddress, baudrate=38400,timeout=1)

# Obtain the spectrometer object
devices = list_devices()
print(devices)
spec = Spectrometer(devices[0])

# Obtain thermal camera object
dev, ctx = openThermalCamera()

# Initialize arrays in which to save outputs
y1Save = []
y2Save = []

Niter = u1Vec.shape[1]
for i in range(Niter):

	iterString = "\nIteration %d out of %d" %(i, Niter)
	print(iterString)

	# Send inputs
	sendInputsArduino(arduinoPI, u1Vec[0,i],u2Vec[0,i],dutyCycle, arduinoAddress)

	# Obtain and save temperature measurements
	Tmax, Tmin = getSurfaceTemperature()
	y1Save += [Tmax]

	# Obtain and save intensity measurements
	intensitySpectrum=spec.intensities()/NORMALIZATION  #NORMALIZATION is defined in APPJPuthonFunctions.py
	totalIntensity = sum(intensitySpectrum)
	y2Save += [totalIntensity]
	# Pause for the duration of the sampling time to allow the system to evolve
	outString = "Measured Outputs: Temperature:%.2f, Intensity:%.2f" %(Tmax,totalIntensity)
	print(outString)
	time.sleep(tSampling)

# Close devices
closeThermalCamera(dev, ctx)

# Concetenate inputs and outputs into one numpy array to save it as a csv
saveArray = np.vstack((np.array(y1Save).reshape(1,-1), np.array(y2Save).reshape(1,-1), u1Vec, u2Vec))

# Save to CSV
directory=os.getcwd()
np.savetxt( directory+"/ExperimentalData/"+timeStamp+"_systemIdentOutputs.csv", saveArray, delimiter=",")
