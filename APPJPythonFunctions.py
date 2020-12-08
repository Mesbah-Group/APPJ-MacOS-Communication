import subprocess
import time
import os
import cv2
import numpy as np
from uvcRadiometry import*

# Define constants
NORMALIZATION = 25000

def sendInputsArduino(arduino,appliedPower,flow,dutyCycle, arduinoAddress):
	#Sends input values to the microcontroller to actuate them
	os.system("echo \"p,"+str(dutyCycle)+"\" > "+ arduinoAddress)
	time.sleep(0.05)
	os.system("echo \"w,"+str(appliedPower)+"\" > " + arduinoAddress)
	time.sleep(0.05)
	os.system("echo \"q,"+str(flow)+"\" > " + arduinoAddress)
	time.sleep(0.05)
	# subprocess.run('echo "w,{:.2f}" > ' + arduinoAddress.format(appliedPower), shell=True) #firmware v14
	# time.sleep(0.0200)
	# subprocess.run('echo "p,{:.2f}" > ' + arduinoAddress.format(dutyCycle), shell=True)
	# time.sleep(0.0200)
	# subprocess.run('echo "q,{:.2f}" > ' + arduinoAddress.format(flow), shell=True)
	# time.sleep(0.0200)
	outString = "Input values: Power:%.2f, Flow:%.2f, Duty Cycle:%.2f" %(appliedPower,flow,dutyCycle)
	print(outString)


def openThermalCamera():
	ctx = POINTER(uvc_context)()
	dev = POINTER(uvc_device)()
	devh = POINTER(uvc_device_handle)()
	ctrl = uvc_stream_ctrl()

	res = libuvc.uvc_init(byref(ctx), 0)
	if res < 0:
		print("uvc_init error")
		exit(1)

	try:
		res = libuvc.uvc_find_device(ctx, byref(dev), PT_USB_VID, PT_USB_PID, 0)
		if res < 0:
			print("uvc_find_device error")
			exit(1)

		try:
			res = libuvc.uvc_open(dev, byref(devh))
			if res < 0:
				print("uvc_open error")
				exit(1)

			print("device opened!")

      # print_device_info(devh)
      # print_device_formats(devh)

			frame_formats = uvc_get_frame_formats_by_guid(devh, VS_FMT_GUID_Y16)
			if len(frame_formats) == 0:
				print("device does not support Y16")
				exit(1)

			libuvc.uvc_get_stream_ctrl_format_size(devh, byref(ctrl), UVC_FRAME_FORMAT_Y16,
			frame_formats[0].wWidth, frame_formats[0].wHeight, int(1e7 / frame_formats[0].dwDefaultFrameInterval)
			)

			res = libuvc.uvc_start_streaming(devh, byref(ctrl), PTR_PY_FRAME_CALLBACK, None, 0)
			if res < 0:
				print("uvc_start_streaming failed: {0}".format(res))
				exit(1)

      # try:
      #   data = q.get(True, 500)
      #   data = cv2.resize(data[:,:], (640, 480))
      #   minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
      #   img = raw_to_8bit(data)
      #   Ts_max = display_temperature(img, maxVal, maxLoc, (0, 0, 255))
      #   Ts_min = display_temperature(img, minVal, minLoc, (255, 0, 0))
			# finally:
			# 	pass
      #   libuvc.uvc_stop_streaming(devh)
		finally:
			pass
			# libuvc.uvc_unref_device(dev)
	finally:
		pass
		# libuvc.uvc_exit(ctx)

	return dev, ctx


def getSurfaceTemperature():
	data = q.get(True, 500)
	data = cv2.resize(data[:,:], (640, 480))
	minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(data)
	img = raw_to_8bit(data)
	Ts_max = display_temperature(img, maxVal, maxLoc, (0, 0, 255))
	Ts_min = display_temperature(img, minVal, minLoc, (255, 0, 0))

	return Ts_max, Ts_min


def closeThermalCamera(dev, ctx):
	libuvc.uvc_unref_device(dev)
	libuvc.uvc_exit(ctx)

	     