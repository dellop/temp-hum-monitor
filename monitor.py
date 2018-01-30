#!/usr/bin/env python
import sys
import time
import os
sys.path.insert(0, '/home/pi/Adafruit_Python_BME280')
import requests
from lxml import html
from Adafruit_BME280 import *
import urllib2
import MySQLdb
import RPi.GPIO as GPIO
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('config.ini')

# Pin Definitions:
humPin = int(config.get('Temp','humPin')) # Humidifier Relay
fanPin = int(config.get('Temp','fanPin')) # Fan Relay

# Other Variables
minHum = int(config.get('Temp','minHum'))
maxHum = int(config.get('Temp','maxHum'))



GPIO.setwarnings(False)
GPIO.setmode(GPIO.BCM)
GPIO.setup(humPin, GPIO.OUT)
GPIO.setup(fanPin, GPIO.OUT)

db = MySQLdb.connect(config.get('Mysql','host'), config.get('Mysql','username'), config.get('Mysql','password'), config.get('Mysql','database'))
curs = db.cursor()


USERNAME = config.get('Honeywell','username')
PASSWORD = config.get('Honeywell','password')

LOGIN_URL = config.get('Honeywell','loginURL')
URL = config.get('Honeywell','deviceURL')

#Setup our API and delay
myAPI = config.get('Thingspeak','apiKey')
myDelay = 15 #how many seconds between posting data

sensor = BME280(t_mode=BME280_OSAMPLE_8, p_mode=BME280_OSAMPLE_8, h_mode=BME280_OSAMPLE_8)

degrees = sensor.read_temperature()
degrees = degrees*1.8+32
pascals = sensor.read_pressure()
pascals = pascals*0.00029529980164712
humidity = sensor.read_humidity()
res = int(os.popen('cat /sys/class/thermal/thermal_zone0/temp').readline())
res = res/1000
res = res*1.8+32
print res
print 'Timestamp = {0:0.3f}'.format(sensor.t_fine)
print 'Temp      = {0:0.3f} deg F'.format(degrees)
print 'Pressure  = {0:0.2f} inHg'.format(pascals)
print 'Humidity  = {0:0.2f} %'.format(humidity)



session_requests = requests.session()
payload = {
	"UserName": USERNAME,
	"password": PASSWORD
	}
try:
	result = session_requests.post(LOGIN_URL, data = payload, headers = dict(referer = LOGIN_URL), timeout=10)
	result = session_requests.get(URL, headers = dict(referer = URL), timeout=10)
	tree = html.fromstring(result.content)
	indoor_temp = tree.xpath("//div[@class='DisplayValue']/text()")
	heat_off = tree.xpath("//div[@id='eqStatusHeating']/@class='hidden'")
	heat_on = tree.xpath("//div[@id='eqStatusHeating']/@class=''")

	print heat_off
	print heat_on

	if heat_off == True:
		heat = 0;
	if heat_on == True:
		heat = 1;

	print indoor_temp[0]
	print indoor_temp[1]
	print indoor_temp[2]
	print indoor_temp[3]
	print indoor_temp[4]
	print indoor_temp[5]
except Exception:
	error = 1
	pass

baseURL = 'https://api.thingspeak.com/update?api_key=%s' % myAPI





if humidity < minHum:
	GPIO.output(humPin, GPIO.LOW)
	GPIO.output(fanPin, GPIO.LOW)
	print "LOW"

if humidity >= maxHum:
	GPIO.output(humPin, GPIO.HIGH)
	GPIO.output(fanPin, GPIO.HIGH)
	print "HIGH"

humidifier = GPIO.input(humPin)
print humidifier

curs.execute("INSERT INTO temps values(NOW(), %s, %s, %s, %s, %s, %s, %s)",(degrees,humidity,pascals,indoor_temp[0],humidifier,indoor_temp[4],heat))




db.commit()
db.close()
