#!/usr/bin/python3
#
# Copyright (c) 2019, NVIDIA CORPORATION. All rights reserved.
#
# Permission is hereby granted, free of charge, to any person obtaining a
# copy of this software and associated documentation files (the "Software"),
# to deal in the Software without restriction, including without limitation
# the rights to use, copy, modify, merge, publish, distribute, sublicense,
# and/or sell copies of the Software, and to permit persons to whom the
# Software is furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in
# all copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT.  IN NO EVENT SHALL
# THE AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER
# DEALINGS IN THE SOFTWARE.
#

import multiprocessing


import Jetson.GPIO as GPIO
import jetson.inference
import jetson.utils

import sys

import Adafruit_SSD1306   # This is the driver chip for the Adafruit PiOLED

import PIL
from PIL import Image
from PIL import ImageDraw
from PIL import ImageFont
from PIL import ImageOps

import serial.tools.list_ports
import serial

import os
import time

disp2 = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=1, gpio=1)
disp = Adafruit_SSD1306.SSD1306_128_32(rst=None, i2c_bus=0, gpio=1)

# Clear display.
disp.begin()
disp.display()

disp2.begin()
disp2.display()


ports = serial.tools.list_ports.comports()
print("ports")
com_port = ""

for port in ports:
	if port.description == "FT232R USB UART - FT232R USB UART":
		com_port = port.device
	print(port.description, port.device)
	
permission = "sudo chmod 666 " + com_port
os.system(permission)
	
print("arduino comport:", com_port)
print(type(com_port))

ser = serial.Serial(com_port, baudrate=250000, timeout=10)

message = "*test/"
test = ser.write(message.encode())
print(f"test2: {ser.readline().decode().strip()}")

print(f"test: {test}")
cmd = "*home/"
ser.write(cmd.encode())
print(f"test3: {ser.readline().decode().strip()}")

time.sleep(5)

display_on = False
dis_state = input("connected display?")
if(dis_state == "y"):
	display_on = True
elif(dis_state == "n"):
	display_on = False

net = jetson.inference.detectNet(argv=['--model=ssd-mobilenet.onnx', '--labels=labels.txt', '--input-blob=input_0', '--output-cvg=scores', '--output-bbox=boxes', '--overlay=box,labels,conf'], threshold=80)
camera = jetson.utils.videoSource("csi://0")      # '/dev/video0' for V4L2
if(display_on):
	display = jetson.utils.glDisplay() # jetson.utils.videoOutput("display://0") # 'my_video.mp4' for file

global display_width
global display_height

display_width = camera.GetWidth()#jetson.utils.glDisplay().GetWidth()
display_height = camera.GetHeight()#jetson.utils.glDisplay().GetHeight()
print("display-width: " + str(display_width))
print("display-height: " + str(display_height))
camera.Open()


global index
global width
global height
global centerx
global centery
global confidence
global flag
global x
global y
global finish
global elapsed_time
global previous_time
global interval
global detection_time
global prev_detetction_time
global detection_interval
global range_1
global range_2
global count
global flagcenter



GPIO.setmode(GPIO.BOARD) #RaspPi pin numbering


def eyes(emotion, send):
	if(send):
		cmd = f"*{emotion}/"
		ser.write(cmd.encode())
		print(ser.readline().decode().strip())
	path = "/home/daoud/eyes/"
	#if emotion == "happy":
	path = path + emotion + "/"
	range_1 = 0
	for filename in os.listdir(path):
		if filename.lower().endswith('.png'):
			range_1 += 1
	range_2 = range_1 - 1
	path = path + emotion + "-"
		
	image = (Image.open(str(path)+"0.png").resize((disp.width,disp.height), Image.BICUBIC).convert("1"))
	im = (Image.open(str(path)+"0.png").resize((disp2.width,disp2.height), Image.BICUBIC).convert("1"))
	disp.image(image)
	disp.display()
	disp2.image(im)
	disp2.display()

	for i in range(range_1):
		image=Image.open(str(path)+str(i)+".png")#.transpose(PIL.Image.FLIP_TOP_BOTTOM)
		image=image.resize((disp2.width,disp2.height), Image.BICUBIC).convert("1")
		im=Image.open(str(path)+str(i)+".png").rotate(180, PIL.Image.NEAREST, expand = 1).transpose(PIL.Image.FLIP_TOP_BOTTOM)
		im=im.resize((disp.width,disp.height), Image.BICUBIC).convert("1")
		disp.image(im)
		disp.display()
		disp2.image(image)
		disp2.display()
		time.sleep(0.03)
	if(emotion == "blink"):
		#print("closing")
		for i in range(range_2-1, -1, -1):
			image=Image.open(str(path)+str(i)+".png")#.transpose(PIL.Image.FLIP_TOP_BOTTOM)
			image=image.resize((disp2.width,disp2.height), Image.BICUBIC).convert("1")
			im=Image.open(str(path)+str(i)+".png").rotate(180, PIL.Image.NEAREST, expand = 1).transpose(PIL.Image.FLIP_TOP_BOTTOM)
			im=im.resize((disp.width,disp.height), Image.BICUBIC).convert("1")
			disp.image(im)
			disp.display()
			disp2.image(image)
			disp2.display()
			time.sleep(0.03)
		
		

index = 0
width = 0
height = 0
confidence=0
flag=0
flagblink = 0
flagangry=0
flaghappy=0
flagsad = 0
flagsurprised = 0
flagneutral = 0
x=0
y=0
centerx = 0
centery = 0
finish = True
interval = 5
previous_time = 0
detection_interval = 0.1
prev_detection_time = 0
elapsed_time = 0
count = 0
flagcenter = False


happy_timer = None
sad_timer = None
angry_timer = None
neutral_timer = None
surprised_timer = None
blink_timer = None

happy_done = False
sad_done = False
angry_done = False
neutral_done = False
surprised_done = False

current_process = None

eyes("neutral", False)

try:
	while camera.IsStreaming():#display.IsOpen():
		img = camera.Capture()
		#detection_time = time.perf_counter()
		#if(detection_time - prev_detection_time >= detection_interval):
		detections = net.Detect(img)
		#	prev_detection_time = detection_time
		if(display_on):
			display.RenderOnce(img)
			display.SetTitle("Object Detection | Network {:.0f} FPS".format(net.GetNetworkFPS()))
		
		flag = 0

		for detection in detections:
			index = detections[0].ClassID
			width = (detections[0].Width)
			height = (detections[0].Height)
			centerx = (detections[0].Center[0])
			centery = (detections[0].Center[1])
			confidence = (detections[0].Confidence)
			flag = 1
			
		if detections:
			flag = 1


		print(f"confidence: {confidence}")
		
		if (flag == 1):
			if (confidence >= 0.5):
				if (flagcenter == True):
					if (index == 1): #happy
						print(f"happy / happy_timer: {happy_timer} / time: {time.perf_counter()}")
						
						sad_timer = None
						angry_timer = None
						neutral_timer = None
						surprised_timer = None
						blink_timer = None
						
						sad_done = False
						angry_done = False
						neutral_done = False
						surprised_done = False
						
						#cmd = "*happy/"
						#ser.write(cmd.encode())
						#print(ser.readline().decode().strip())
						
						if happy_timer is None:
							happy_timer = time.perf_counter()
						elif time.perf_counter() - happy_timer >= 2 and not happy_done:
							
							print(f"timer: {time.perf_counter() - happy_timer}")
							#eyes("happy")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							kwarg = {"send": True}
							current_process = multiprocessing.Process(target = eyes,args = ("happy", True,))
							current_process.start()
							#current_process.join()
							
							happy_done = True
						flagblink = 0
						flagangry=0
						flagsad = 0
						flagsurprised = 0
						flagneutral = 0
						
					elif (index == 2): #sad
						happy_timer = None
						angry_timer = None
						neutral_timer = None
						surprised_timer = None
						blink_timer = None
						
						happy_done = False
						angry_done = False
						neutral_done = False
						surprised_done = False
						
						#cmd = "*sad/"
						#ser.write(cmd.encode())
						#print(ser.readline().decode().strip())
						
						print(f"sad / sad_timer: {happy_timer} / time: {time.perf_counter()}")
						
						if sad_timer is None:
							sad_timer = time.perf_counter()
						elif time.perf_counter() - sad_timer >= 2 and not sad_done:
							print(f"timer: {time.perf_counter() - sad_timer}")
							#eyes("happy")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							kwarg = {"send": True}
							current_process = multiprocessing.Process(target = eyes,args = ("sad", True,))
							current_process.start()
							#current_process.join()
							
							sad_done = True
							
						print("sad")
						flagblink = 0
						flagangry=0
						flaghappy=0
						flagsurprised = 0
						flagneutral = 0
						
					elif (index == 3): #angry
						happy_timer = None
						sad_timer = None
						neutral_timer = None
						surprised_timer = None
						blink_timer = None
						
						happy_done = False
						sad_done = False
						neutral_done = False
						surprised_done = False
						
						#cmd = "*angry/"
						#ser.write(cmd.encode())
						#print(ser.readline().decode().strip())
						
						print(f"angry / angry_timer: {happy_timer} / time: {time.perf_counter()}")
						
						if angry_timer is None:
							angry_timer = time.perf_counter()
						elif time.perf_counter() - angry_timer >= 2 and not angry_done:
							print(f"timer: {time.perf_counter() - angry_timer}")
							#eyes("happy")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							
							kwarg = {"send": True}
							current_process = multiprocessing.Process(target = eyes,args = ("angry", True,))
							current_process.start()
							#current_process.join()
							
							angry_done = True
							
						print("angry")
						flagblink = 0
						flagsad=0
						flaghappy=0
						flagsurprised = 0
						flagneutral = 0
						
					elif (index == 4): #neutral
						happy_timer = None
						sad_timer = None
						angry_timer = None
						surprised_timer = None
						
						happy_done = False
						sad_done = False
						angry_done = False
						surprised_done = False
						
						#cmd = "*neutral/"
						#ser.write(cmd.encode())
						#print(ser.readline().decode().strip())
						
						print(f"neutral / neutral_timer: {neutral_timer} / time: {time.perf_counter()}")
						
						if neutral_timer is None:
							neutral_timer = time.perf_counter()
						elif time.perf_counter() - neutral_timer >= 2 and not neutral_done:
							print(f"timer: {time.perf_counter() - neutral_timer}")
							#eyes("happy")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							kwarg = {"send": True}
							current_process = multiprocessing.Process(target = eyes,args = ("neutral", True,))
							current_process.start()
							#current_process.join()
							
							neutral_done = True
							
						
						if blink_timer is None:
							blink_timer = time.perf_counter()
						elif time.perf_counter() - blink_timer >= 5:
							print(f"timer: {time.perf_counter() - blink_timer}")
							#eyes("happy")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							current_process = multiprocessing.Process(target = eyes,args = ("blink", False,))
							current_process.start()
							#current_process.join()
							
							blink_timer = None
						
							
						print("neutral")
						flagblink = 0
						flagsad=0
						flaghappy=0
						flagsurprised = 0
						flagangry = 0
						
					elif (index == 5): #surprised
						happy_timer = None
						sad_timer = None
						angry_timer = None
						neutral_timer = None
						blink_timer = None
						
						happy_done = False
						sad_done = False
						angry_done = False
						neutral_done = False
						
						#cmd = "*surprised/"
						#ser.write(cmd.encode())
						#print(ser.readline().decode().strip())
						
						print(f"surprised / surprised_timer: {surprised_timer} / time: {time.perf_counter()}")
						if surprised_timer is None:
							surprised_timer = time.perf_counter()
						elif time.perf_counter() - surprised_timer >= 2 and not surprised_done:
							print(f"timer: {time.perf_counter() - surprised_timer}")
							#eyes("surprised")
							
							if current_process and current_process.is_alive():
								print("terminating prev process")
								current_process.terminate()
								#current_process.join()
							kwarg = {"send": True}
							current_process = multiprocessing.Process(target = eyes,args = ("surprised", True,))
							current_process.start()
							#current_process.join()
							
							surprised_done = True
							
						print("surprised")
						flagblink = 0
						flagsad=0
						flaghappy=0
						flagneutral = 0
						flagangry = 0
						
			else :
				print("confidence less than 70")
				
				cmd = "*low-conf/"
				ser.write(cmd.encode())
				print(ser.readline().decode().strip())
				
				flagblink = 0
				flagsad=0
				flaghappy=0
				flagsurprised = 0
				flagangry = 0
				

			x = display_width/2
			y = display_height/2
			
			#GPIO.output(35, GPIO.HIGH)
			
			if (centerx >= x-75 and centerx <= x+75): #75 old
				print("CENTERX")
				
				if(centery > y-75 and centery < y+75):
					print("CENTERY")
					#print(centery)
					count += 1
					if (count >= 4):
						flagcenter = True
					else:
						flagcenter = False
					
				
					cmd = "*stop/"
					ser.write(cmd.encode())
					print(ser.readline().decode().strip())
					
				else:
					
					if (centery < y-75):
						#up
						print("UP")
						flagcenter = False
						count = 0
						
						cmd = "*up/"
						ser.write(cmd.encode())
						print(ser.readline().decode().strip())
						
					elif (centery > y+75):
						#down
						print("DOWN")
						flagcenter = False
						count = 0
						
						cmd = "*down/"
						ser.write(cmd.encode())
						print(ser.readline().decode().strip())
			else:
				if (centerx < x-75):
					#left
					print("LEFT")
					flagcenter = False
					count = 0
					
					cmd = "*left/"
					ser.write(cmd.encode())
					print(ser.readline().decode().strip())
				
				elif (centerx > x+75):
					#right
					print("RIGHT")
					flagcenter = False
					count = 0
					
					cmd = "*right/"
					ser.write(cmd.encode())
					print(ser.readline().decode().strip())
				
				
		else:
			print("no face-free rom")
			cmd = "*free-roam/"#"*free-roam/" #"*free-roam/"
			ser.write(cmd.encode())
			print(ser.readline().decode().strip())
			
			flagcenter = False
			count = 0
			
			
			
		
			
	print("going home")
	cmd = "*home/"
	ser.write(cmd.encode())
	print(ser.readline().decode().strip())
				
	#if __name__ == '__main__':
	#	main()
except KeyboardInterrupt:
	eyes("neutral", True)
	print("going home")
	cmd = "*home/"
	ser.write(cmd.encode())
	print(ser.readline().decode().strip())
	print("quitting")
	quit()



