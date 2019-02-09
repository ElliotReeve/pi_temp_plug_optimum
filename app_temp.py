from flask import Flask, jsonify, request
import glob
from pyHS100 import SmartPlug
import RPi.GPIO as GPIO
from datetime import datetime
from pytz import timezone

app = Flask(__name__)

gmt = timezone('GMT')
base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28*')[0]
device_file = device_folder + '/w1_slave'

#set board numbering to BCM
GPIO.setmode(GPIO.BCM)

#setup output pins
GPIO.setup(17,GPIO.OUT)
GPIO.setup(27,GPIO.OUT)

def read_temp_raw():
	f = open(device_file, 'r')
	lines = f.readlines()
	f.close()
	return lines

def read_temp():
	lines = read_temp_raw()
	while lines[0].strip()[-3:] != 'YES':
		sleep(0.2)
		lines = read_temp_raw()
	equals_pos = lines[1].find('t=')
	if equals_pos != -1:
		temp_string = lines[1][equals_pos+2:]
		temp_c = float(temp_string) / 1000.0
		return temp_c

@app.route("/get-temp")
def get_temp():
	auth = request.args.get('auth')
	if auth == "cabin":
		plug_log = open("/d1/cabin_log.txt", "a")
		temp = read_temp()
		time_now = datetime.now(gmt)
		string_time = time_now.strftime("%d/%m/%y %H:%M:%S")
		plug_log.write(string_time+" /get-temp temperature is: "+str(temp)+"\n")
		plug_log.close()
		return jsonify({"temperature": temp, "status": "ok"})
	else:
		return jsonify({"message": "unauthorised", "status": "error"})

@app.route("/set-temp")
def set_temp():
	auth = request.args.get('auth')
	if auth == "cabin":
		time_now = datetime.now(gmt)
		string_time = time_now.strftime("%d/%m/%y %H:%M:%S")
		plug_log = open("/d1/cabin_log.txt", "a")
		plug = SmartPlug("192.168.1.144")
		temp = read_temp()
		if temp < 20:
			GPIO.output(17,GPIO.HIGH)
			GPIO.output(27,GPIO.HIGH)
			plug_log.write(string_time+" /set-temp temperature set to reach optimum, current temperature is: "+str(temp)+"\n")
			plug_log.close()
			plug_status_file = open("/d1/webserver/reaching_optimum.txt", "w")
			plug.turn_on()
			plug_status_file.write("1")
			plug_status_file.close()
			return jsonify({"message": "Plug turned on, will turn off when 20C is reached.", "status": "ok"})
		else:
			plug_log.write(string_time+" /set-temp not activating as temperature is: "+str(temp)+"\n")
			plug_log.close()
			return jsonify({"message": "Temperature is already at optimum temperature.", "status": "ok"})
	else:
		return jsonify({"message": "unauthorised", "status": "error"})

if __name__ == '__main__':
	app.run(host='0.0.0.0', port=80)
