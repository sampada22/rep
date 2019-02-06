from __future__ import print_function
import glob
import struct
import time
import numpy as np
import serial

def available_Ports():
	available_ports = glob.glob('dev/ttyACM*')
	print('Available ports:')
	print(available_ports)

	return available_ports

def get_time_millis():
	return(int(round(time.time() * 1000)))

def get_time_seconds():
	return (int(round(time.time() * 1000000)))

def print_Values(self):
	print("-----ONE MORE MEASUREMENT-----")
	print("Humidity:",self.Data[0])
	print("Temperature in C:",self.Data[1])
	print("Tempeature in F:",self.Data[2])
	print("Heat Index in F:",self.Data[3])
	print("Heat Index in C:",self.Data[4])


class read_From_Arduino(object):
	def __init__(self,port,SIZE_STRUCT = 10,verbose = 0):
		self.port = port
		self.millis = get_time_millis()
		self.SIZE_STRUCT = SIZE_STRUCT
		self.verbose = verbose
		self.Data = -1
		self.t_init = get_time_millis()
		self.t = 0

		self.port.flushInput()

	def read_one_value(self):
		read = False

		while not read:
			myByte = self.port.read(1)
			if myByte == 'S':
				#print(myByte)
				packed_data = self.port.read(self.SIZE_STRUCT)
				myByte = self.port.read(1)
				if myByte == 'E':
					#print(myByte)
					self.t = (get_time_millis() - self.t_init) /1000.0
	
					unpacked_data = struct.unpack('<hhhhh',packed_data)
					#print(unpacked_data)
					current_time = get_time_millis()
					time_elapsed = current_time - self.millis
					self.millis = current_time

					read = True

					self.Data = np.array(unpacked_data)
					return(True)
		
		return(False)

	def get_Humidity(self):
		self.read_one_value()
		return self.Data[0]

	def get_Temp_in_C(self):
		self.read_one_value()
		return self.Data[1]

	def get_Temp_in_F(self):
		self.read_one_value()
		return self.Data[2]

	def get_HeatIndex_in_F(self):
		self.read_one_value()
		return self.Data[3]

	def get_HeatIndex_in_C(self):
		self.read_one_value()
		return self.Data[4]

#ports = available_Ports()
#print(ports)
Arduino = serial.Serial(port = '/dev/ttyACM0',baudrate = 9600, timeout = 5 )

read_From_Arduino_Instance = read_From_Arduino(Arduino,verbose = 10)

while True:
	h = read_From_Arduino_Instance.get_Humidity()
	tic = read_From_Arduino_Instance.get_Temp_in_C()
	tif = read_From_Arduino_Instance.get_Temp_in_F()
	hif = read_From_Arduino_Instance.get_HeatIndex_in_F()
	hic = read_From_Arduino_Instance.get_HeatIndex_in_C()
	print("Humidity:",h)
	print("Temperature in C:",tic)
	print("Temperature in F:",tif)
	print("Heat Index in F:",hif)
	print("Heat Index in C:",hic)

