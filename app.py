from flask import Flask,render_template,request

app = Flask(__name__)
import sqlite3

def get_Data():
	conn = sqlite3.connect("forecast.db")
	curs = conn.cursor()
	for row in curs.execute("SELECT * FROM DHT_Data" ):
		humidity = row[1]
		temp_in_C = row[2]
		temp_in_F = row[3]
		heatIndex_in_C = row[4]
		heatIndex_in_F = row[5]
	conn.close()
	return humidity,temp_in_C,temp_in_F,heatIndex_in_C,heatIndex_in_F

@app.route('/')
def profile():
	humidity,temp_in_C,temp_in_F,heatIndex_in_C,heatIndex_in_F = get_Data()
	template_Data = {
	'humidity' : humidity,
	'temp_in_C' : temp_in_C,
	'temp_in_F' : temp_in_F,
	'heatIndex_in_C' : heatIndex_in_C,
	'heatIndex_in_F' : heatIndex_in_F
	}
	return render_template('profile.html',**template_Data)

if __name__ == '__main__':
	app.run(debug = True)
