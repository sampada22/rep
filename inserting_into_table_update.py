from __future__ import print_function
import matplotlib
from matplotlib.backends.backend_agg import FigureCanvasAgg as FigureCanvas
from matplotlib.figure import Figure
from io import BytesIO
from flask import Flask,render_template,request,make_response,send_file
import serial
import sqlite3
from sqlite3 import Error
import time
import glob
import numpy as np
import struct
import threading
from datetime import date

dateToday = str(date.today())

app = Flask(__name__)

def get_time_millis():
	return (int(round(time.time() * 1000)))

def get_time_seconds():
	return (int(round(time.time() * 1000000)))

class read_From_Arduino(object):
	def __init__(self,port,SIZE_STRUCT = 10, verbose = 0):
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
				print(myByte)
				packed_data = self.port.read(self.SIZE_STRUCT)
				myByte = self.port.read(1)
				if myByte == 'E':
					self.t = (get_time_millis() - self.t_init)/1000.0
					unpacked_data = struct.unpack('<hhhhh',packed_data)
					print(unpacked_data)
				 	print(myByte)
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

	def get_HeatIndex_in_C(self):
		self.read_one_value()
		return self.Data[3]

	def get_HeatIndex_in_F(self):
		self.read_one_value()
		return self.Data[4]



def create_connection(db_file):
	"""create conenction to the SQLite database:
	:param db_file: database file
	:return: Connection object or None
	"""

	try:
		conn = sqlite3.connect(db_file)
		return conn
	except Error as e:
		print(e)
	return None

def create_data_Log(conn,data_Log):
	"""Create a new data log into the DHT_Data table
	:param conn:
	:param: data_Log
	:return:None
	"""

	try:
		sql = """INSERT INTO DHT_Data(humidity,temp_in_C,temp_in_F,heatIndex_in_C,heatIndex_in_F)
		         VALUES(?,?,?,?,?)"""
		cur = conn.cursor()
		cur.execute(sql,data_Log)
		return None
	except Error as e:
		print(e)
	return None

def get_Data():
	conn = sqlite3.connect("forecast.db")
	curs = conn.cursor()
	for row in curs.execute("SELECT * FROM DHT_Data"):
		humidity = row[1]
		temp_in_C = row[2]
		temp_in_F = row[3]
		heatIndex_in_C = row[4]
		heatIndex_in_F = row[5]
	conn.close()
	return humidity,temp_in_C,temp_in_F,heatIndex_in_C,heatIndex_in_F

def get_HistoricalData():
	conn = sqlite3.connect("forecast.db")
	curs = conn.cursor()
	curs.execute("SELECT * FROM DHT_Data")
	data = curs.fetchall()
	a_Hum = []
	a_Temp = []
	a_heatIndex = []

	for row in reversed(data):
		a_Hum.append(row[1])
		a_Temp.append(row[2])
		a_heatIndex.append(row[5])
	return a_Hum, a_Temp, a_heatIndex

def max_RowsTable():
	conn = sqlite3.connect("forecast.db")
	curs = conn.cursor()
	for row in curs.execute("SELECT COUNT(temp_in_C) FROM DHT_Data"):
		maxNumberRows = row[0]
	return maxNumberRows

global num_Samples
num_Samples = max_RowsTable()
if(num_Samples > 101):
	num_Samples = 100

@app.route('/')
def profile():
	humidity,temp_in_C,temp_in_F,heatIndex_in_C,heatIndex_in_F = get_Data()
	template_Data ={
		'humidity' : humidity,
		'temp_in_C' : temp_in_C,
		'temp_in_F' : temp_in_F,
		'heatIndex_in_C' : heatIndex_in_C,
		'heatIndex_in_F' : heatIndex_in_F,
		'dateToday' : dateToday
	}
	return render_template('profile.html', **template_Data)

@app.route('/plot/hum')
def plot_Hum():
	a_Hum, a_Temp,a_heatIndex = get_HistoricalData()
	ys = a_Hum[:100]
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Humidity")
	axis.set_xlabel("Samples")
	axis.grid(False)
	xs = range(num_Samples)
	axis.plot(xs,ys)
	canvas = FigureCanvas(fig)
	output = BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = "image/png"
	return response

@app.route('/plot/temp')
def plot_Temp():
	a_Hum,a_Temp, a_heatIndex = get_HistoricalData()
	ys = a_Temp[:100]
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Temperature")
	axis.set_xlabel("Samples")
	axis.grid(False)
	xs = range(num_Samples)
	axis.plot(xs,ys)
	canvas = FigureCanvas(fig)
	output = BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = "image.png"
	return response

@app.route('/plot/heatIndex')
def plot_heatIndex():
	a_Hum,a_Temp,a_heatIndex = get_HistoricalData()
	ys = a_heatIndex[:100]
	fig = Figure()
	axis = fig.add_subplot(1,1,1)
	axis.set_title("Heat Index")
	axis.set_xlabel("Samples")
	axis.grid(False)
	xs = range(num_Samples)
	axis.plot(xs,ys)
	canvas = FigureCanvas(fig)
	output = BytesIO()
	canvas.print_png(output)
	response = make_response(output.getvalue())
	response.mimetype = "image.png"
	return response

def update_Database():
	
	time.sleep(0.5)
	Arduino = serial.Serial(port = '/dev/ttyACM0',baudrate = 9600,timeout = 0.5)
	read_From_Arduino_Instance = read_From_Arduino(Arduino,verbose = 10)
	database = "forecast.db"
	#create a database connection
	conn = create_connection(database)
	while True:
		h = read_From_Arduino_Instance.get_Humidity()
		tic = read_From_Arduino_Instance.get_Temp_in_C()
		tif = read_From_Arduino_Instance.get_Temp_in_F()
		hic = read_From_Arduino_Instance.get_HeatIndex_in_C()
		hif = read_From_Arduino_Instance.get_HeatIndex_in_F()
		print("Value assigned")
		#if (Arduino.in_waiting > 0):
		print("Entered while loop")
		with conn:
			#data_Log = ser.readline()
			data_Log = (h,tic,tif,hic,hif)
			create_data_Log(conn,data_Log)
			print("Worked")

	

def run_Server():
	app.run()
	app.debug = True
	
	
#t1 = threading.Thread(target = update_Database,args = '')
#t2 = threading.Thread(target = run_Server(),args = '')

#t1.start()
#t2.start()


if __name__ == '__main__':
	time.sleep(0.5)

	#t1.join()
	#t2.join()

	#app.run()
	#app.debug = True;
	#run_Server()
	update_Database()
	#time.sleep(0.5)
	#main()
