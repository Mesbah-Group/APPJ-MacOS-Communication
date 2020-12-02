import os
from applescript import tell
import time
import subprocess

#Set directory (in case of drag-and-drop directory will not be already set)
directory = os.getcwd()
os.chdir(directory)


# Define commands here
testCommand = 'ls'
arduinoAddress = '/dev/cu.usbmodem14322401';
arduinoSetUp = 'stty -f '+ arduinoAddress +' raw 38400 -hupcl & cat /dev/cu.usbmodem14322401' #Make sure that the address correspond that shown in the arduino IDE

# Open new terminal window to read the arduino
print("Opening new terminal window to read the arduino...")
time.sleep(1)
tell.app( 'Terminal', 'do script "' + arduinoSetUp + '"')
print("...Done")
time.sleep(0.5)

confirmInput = input(">>> Is the Arduino being read correctly? [y/n]")
while (confirmInput!='y' and confirmInput!='n'):
	print("Invalid answer")
	confirmInput = input(">>> Is the Arduino being read correctly? [y/n]")
	print(confirmInput)

if confirmInput == 'y':
	print('\n')
elif confirmInput == 'n':
	print('\nRESET ARDUINO AND TROUBLESHOOT! (Common cause for not reading the Arduino properly is an incorrectly set baud rate. Make sure it is at 38400)')
	exit()

# Ask user for initial inputs to set up the power
dutyCycleIn = input("Set the duty cycle % (dafault is 100)")
print("echo \"p,"+str(dutyCycleIn)+"\" > "+ arduinoAddress)
os.system("echo \"p,"+str(dutyCycleIn)+"\" > "+ arduinoAddress)
powerIn = input("Set the power in Watts (dafault is 2)")
os.system("echo \"w,"+str(powerIn)+"\" > " + arduinoAddress)

# Check that the oscilloscope is indicating the correct readings
confirmInput = input(">>> Is the oscilloscope showing a waveform? [y/n]")
while (confirmInput!='y' and confirmInput!='n'):
	print("Invalid answer")
	confirmInput = input(">>> Is the oscilloscope showing a waveform? [y/n]")
	print(confirmInput)
if confirmInput == 'y':
	print('\n')
elif confirmInput == 'n':
	os.system("echo \"p,"+str(0)+"\" > "+ arduinoAddress)
	os.system("echo \"w,"+str(0)+"\" > "+ arduinoAddress)
	print('\nRESET ARDUINO AND TROUBLESHOOT!')
	exit()

# Ask user for initial inputs to set up the flow rate
flowIn = input("Set the flow rate in slm (dafault is 1.5)")
os.system("echo \"q,"+str(flowIn)+"\" > /dev/cu.usbmodem14322401")

# Open new terminal window to execute any additional python scripts
os.chdir(directory)
print("############################################################################################################################################################################################")
print("MAKE SURE TO STOP READING THE ARDUINO FROM THE SECOND TERMINAL WINDOW BEFORE EXECUTING ANY PYTHON SCRIPTS (CNTRL+C)! YOU CANNOT READ THE ARDUINO FROM TWO DIFFERENT PLACES AT THE SAME TIME!")
print("############################################################################################################################################################################################")










