import subprocess
import time

NORMALIZATION = 25000

def sendInputsArduino(arduino,appliedPower,flow,dutyCycle):
	#Sends input values to the microcontroller to actuate them
	arduino.reset_input_buffer()
	subprocess.run('echo "" > ' + arduinoAddress, shell=True)
	time.sleep(0.0200)
	subprocess.run(('echo "w,{:.2f}" > ' + arduinoAddress).format(appliedPower), shell=True) #firmware v14
	time.sleep(0.0200)
	subprocess.run(('echo "p,{:.2f}" > ' + arduinoAddress).format(dutyCycle), shell=True)
	time.sleep(0.0200)
	subprocess.run(('echo "q,{:.2f}" > ' + arduinoAddress).format(flow), shell=True)
	time.sleep(0.0200)
	print("input values: Power:{:.2f}, Flow:{:.2f}, Duty Cycle:{:.2f}".format(appliedPower,Flow,dutyCycle))