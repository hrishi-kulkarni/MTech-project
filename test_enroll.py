import RPi.GPIO as gpio
import time
from RPLCD.gpio import CharLCD
from pyfingerprint.pyfingerprint import PyFingerprint

import mysql.connector
########### GPIO PIN Defines ########################

SW1=3
SW2=5
SW3=7

CRANK_LED=11
BOOM_LED=12
BUCKET_LED=32

HI=1
LO=0

PWM_FREQ=1000

#Global vars
is_opr = False
is_ownr = False
position_id=0 
login_time=0 
operation_time=0
boom_speed=0
bucket_speed =0
operators_added = 0

########## GPIO Pin Configs #########################
gpio.setwarnings(False)
gpio.setmode(gpio.BOARD)	

gpio.setup(SW1, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(SW2, gpio.IN, pull_up_down=gpio.PUD_UP)
gpio.setup(SW3, gpio.IN, pull_up_down=gpio.PUD_UP)

gpio.setup(CRANK_LED, gpio.OUT)
gpio.setup(BOOM_LED, gpio.OUT)
gpio.setup(BUCKET_LED, gpio.OUT)
pwm_boom = gpio.PWM(BOOM_LED,PWM_FREQ)
pwm_bucket = gpio.PWM(BUCKET_LED,PWM_FREQ)

####################### INIT ###########################

#database connectivity
try:
	db = mysql.connector.connect(user='root',password='',host='192.168.43.229',database='operatorpersonalization')
	cur = db.cursor()
except:
	print("database connection error")
#db end

#lcd init
lcd = CharLCD(pin_rs = 37, pin_e = 35, pins_data = [33,31,29,23], numbering_mode = gpio.BOARD, cols = 16, rows =2)
#lcd end

#fingerprint init
try:
	f = PyFingerprint('/dev/ttyUSB0', 57600, 0xFFFFFFFF, 0x00000000)
	if ( f.verifyPassword() == False ):
		raise ValueError('The given fingerprint sensor password is wrong!')
except Exception as e:
	print('Exception message: ' + str(e))
	exit(1)
#fingerprint end


def enrollFinger():
	lcd.write_string("Enrolling Finger")
	time.sleep(2)
	print('Waiting for finger...')
	lcd.write_string("Place Finger")
	while ( f.readImage() == False ):
		pass
	f.convertImage(0x01)
	result = f.searchTemplate()
	positionNumber = result[0]
	if ( positionNumber >= 0 ):
		print('Template already exists at position #' + str(positionNumber))
		lcd.write_string("Finger ALready")
		lcd.cursor_pos(1,0)
		lcd.write_string("   Exists     ")
		time.sleep(2)
		return
	print('Remove finger...')
	lcd.write_string("Remove Finger")
	time.sleep(2)
	print('Waiting for same finger again...')
	lcd.write_string("Place Finger")
	lcd.write_string("   Again    ")
	while ( f.readImage() == False ):
		pass
	f.convertImage(0x02)
	if ( f.compareCharacteristics() == 0 ):
		print ("Fingers do not match")
		lcd.write_string("Finger Did not")
		lcd.write_string("   Mactched   ")
		time.sleep(2)
		return
	f.createTemplate()
	positionNumber = f.storeTemplate()
	print('Finger enrolled successfully!')
	lcd.write_string("Stored at Pos:")
	lcd.write_string(str(positionNumber))
	lcd.write_string("successfully")
	print('New template position #' + str(positionNumber))
	time.sleep(2)
	query = "INSERT INTO operator VALUES(%s,%s,%s,%s,%s,%s)"
	args = (str(position_id), 'operator'+str(position_id), '0', '0', '50', '50')
	try:
		cur.execute(query, args)
		db.commit()
	except:
		print("Error in database insert")

enrollFinger()