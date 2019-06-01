####################################################
# Author	: Harshal Kulkarni
# Date 		: 05/05/19
# Functions for 16x2 LCD screen, SW and LED
####################################################
'''
COMMAND
pip install mysql-connector-python-rf
'''
########### Import Section #########################

import RPi.GPIO as gpio
import time
import math
from RPLCD.gpio import CharLCD
from pyfingerprint.pyfingerprint import PyFingerprint

import mysql.connector
########### GPIO PIN Defines ########################

SW1=7
SW2=5
SW3=3

CRANK_LED=11
BOOM_LED=12
BUCKET_LED=36

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
	db = mysql.connector.connect(user='root',password='',host='192.168.43.44',database='operatorpersonalization')
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

########################## LCD Screen Functions ############################################################

def Disp_DefaultScreen():
	lcd.clear()
	lcd.write_string('SCAN FINGERPRINT')
	lcd.cursor_pos=(1,0)
	lcd.write_string('TO CRANK LOADER')

################# Owner Screen ##########################

#if id == Owner load this screen
def Disp_OwnerScreen():
	lcd.clear()
	lcd.write_string('WELCOME OWNER')  
	# For formated string use:  lcd.write_string("Welcome %s" %Var Name) 
	lcd.cursor_pos=(1,0)
	lcd.write_string('ADD OPR')
	lcd.cursor_pos=(1,10)
	lcd.write_string('LOGOUT')
	#if SW2=Pressed Load Default Screen

##################### Operator Screens ####################################

#Load this screen if id == Operator, start opr timer in seconds
def Disp_OprScreen(id):
	lcd.clear()
	lcd.write_string('OPERATOR %s' %id)
	lcd.cursor_pos=(1,0)
	lcd.write_string('OPRTN')
	lcd.cursor_pos=(1,7)
	lcd.write_string('SETT')
	lcd.cursor_pos=(1,13)
	lcd.write_string('YLD')
	#Make crank LED ON

#Load this screen if SW1=Pressed for Opr
def Disp_OprScreen_1(id):
	lcd.clear()
	lcd.write_string('OPERATOR %s' %id)
	lcd.cursor_pos=(1,0)
	lcd.write_string('BOOM')
	lcd.cursor_pos=(1,7)
	lcd.write_string('BKT')
	lcd.cursor_pos=(1,13)
	lcd.write_string('OFF')

	#if SW1= Pressed, Cmd --> Boom, record time in seconds
	#if SW2= Pressed, Cmd --> Bucket, record time in secods

#Load this screen if SW2=Pressed for Sett
def Disp_OprScreen_2(id,boom_spd,bucket_spd):
	lcd.clear()
	lcd.cursor_pos=(0,0)
	lcd.write_string('%s' %boom_spd)
	lcd.cursor_pos=(0,7)
	lcd.write_string('%s' %bucket_spd)
	lcd.cursor_pos=(1,0)
	lcd.write_string('BOOM')
	lcd.cursor_pos=(1,7)
	lcd.write_string('BKT')
	lcd.cursor_pos=(1,12)
	lcd.write_string('SAVE')

	#if SW1= increment duty cycle of Boom +5
	#if SW2= increment duty cycle of Bucket +5
	#if SW3= Save settings of boom bucket and commit to DB for given operator

#Load this screen if SW3=Pressed for Yld
def Disp_OprScreen_3(id,yld,fuel):
	lcd.clear()
	lcd.write_string('OPR%s YLD:' %id)
	lcd.write_string("%s" %yld)
	lcd.cursor_pos=(1,0)
	lcd.write_string('FUEL USE:%sLTR' %fuel)			#Debug

################### Function to check SW pressed ##############################################
def SW1Pressed():
	return gpio.input(SW1) == LO
 

def SW2Pressed():
	return gpio.input(SW2) == LO


def SW3Pressed():
	return gpio.input(SW3) == LO
 
 ################# Function to set Actuatotrs with duty cycle ########################################
def Cmd_Boom(duty_cycle):
	pwm_boom.start(duty_cycle)
	pwm_boom.ChangeDutyCycle(duty_cycle)
	
def Cmd_Bucket(duty_cycle):
	pwm_bucket.start(duty_cycle)
	pwm_bucket.ChangeDutyCycle(duty_cycle)

def Cmd_Crank(crank):
	if crank==1:
		gpio.output(CRANK_LED, gpio.HIGH)
	elif crank==0:
		gpio.output(CRANK_LED, gpio.LOW)

############################  Enrolling finger ############################################################

def enrollFinger():
	lcd.clear()
	lcd.write_string('ENROLLING FINGER')
	time.sleep(2)
	lcd.clear()
	print('Waiting for finger...')
	lcd.clear()
	lcd.write_string('PLACE FINGER')
	while ( f.readImage() == False ):
		pass
	f.convertImage(0x01)
	result = f.searchTemplate()
	positionNumber = result[0]
	if ( positionNumber >= 0 ):
		print('Template already exists at position #' + str(positionNumber))
		lcd.clear()
		lcd.write_string('FINGER ALREADY')
		lcd.cursor_pos(1,0)
		lcd.write_string('EXISTS')
		time.sleep(2)
		return
	print('Remove finger...')
	lcd.clear()
	lcd.write_string('REMOVE FINGER')
	time.sleep(2)
	print('Waiting for same finger again...')
	lcd.clear()
	lcd.write_string('PLACE FINGER')
	lcd.cursor_pos(1,0)
	lcd.write_string('AGAIN')
	while ( f.readImage() == False ):
		pass
	f.convertImage(0x02)
	if ( f.compareCharacteristics() == 0 ):
		print ("Fingers do not match")
		lcd.clear()
		lcd.write_string('FINGER DID NOT')
		lcd.cursor_pos(1,0)
		lcd.write_string('MATCHED')
		time.sleep(2)
		return
	f.createTemplate()
	positionNumber = f.storeTemplate()
	print('Finger enrolled successfully!')
	lcd.clear()
	lcd.write_string('OPR')
	lcd.write_string(str(positionNumber))
	lcd.write_string('  ADDED')
	print('New template position #' + str(positionNumber))
	time.sleep(2)
	query = "INSERT INTO operator VALUES(%s,%s,%s,%s,%s,%s)"
	args = (str(position_id), 'operator'+str(position_id), '0', '0', '50', '50')
	try:
		cur.execute(query, args)
		global operators_added
		operators_added = int(operators_added)
		operators_added += 1
		cur.execute ("UPDATE owner SET NumberOfOperatorsAdded=%s", (str(operators_added),))
		db.commit()
	except:
		print("Error in database insert")



################################# MAIN #########################################################
while(True):
	Cmd_Crank(0)
	print('Reached at BIG WHILE TRUE, made crank 0')
	Disp_DefaultScreen()
	print('Showing MAIN SCREEN to SCAN FINGERPRINT')
	try:
		print('Waiting for finger...')
		while( f.readImage() == False ):
			#pass
			time.sleep(.25)
			#return
		f.convertImage(0x01)
		result = f.searchTemplate()
		position_id = result[0]
		#accuracyScore = result[1]
		if position_id == -1 :
			Cmd_Crank(0)
			print('No match found!, cant crank')
			lcd.clear()
			lcd.write_string('INVALID LOGIN')
			lcd.cursor_pos=(1,0)
			lcd.write_string('CANNOT CRANK')
			time.sleep(5)
		else:
			Cmd_Crank(1)
			lcd.clear()
			lcd.write_string('LOADER CRANKED')
			print('Success, Loader cranked')
			time.sleep(5)
			query_opr = "SELECT * FROM operator WHERE ID=%s"
			cur.execute(query_opr, (position_id,))
			rows_opr = cur.fetchall()

			#opr found, update global vars
			if cur.rowcount != 0:
				is_opr = True
				is_ownr = False
				#time_parameters
				start_login_time = time.time()
				start_boom = 0
				end_boom = 0
				start_bucket = 0
				end_bucket = 0
				tot_boom = 0
				tot_bucket = 0
				print('Initialized: \nstart_login_time, start_boom, end_boom, start_bucket, end_bucket, tot_boom, tot_bucket')
				print(start_login_time, start_boom, end_boom, start_bucket, end_bucket, tot_boom, tot_bucket)

				for row in rows_opr:
					login_time = row[2]
					operation_time = row[3]
					boom_speed = row[4]
					bucket_speed = row[5]
				
				print('Data fetched from DB\n')
				print('login_time, operation_time, boom_speed, bucket_speed\n')
				print(login_time, operation_time, boom_speed, bucket_speed)

				#collected all parameters of logged in operator
				#call operator main screen
				while True:
					Disp_OprScreen(position_id)
					print('Welcome OPR Main Screen')
					if SW1Pressed():	#GOTO operation screen
						print('SW1 Pressed in OPR Main Screen, came in Boom and Bucket Oerations')
						while True:
							Disp_OprScreen_1(position_id)
							print('Displaying OPR Operation Screen')
							time.sleep(2)
							if SW1Pressed():
								print('In OPR Operation Screen: SW1 Pressed')
								start_boom = time.time()
								print('Started recording Boom Time:',start_boom)
								while SW1Pressed():
									Cmd_Boom(int(boom_speed))
									print('Boom commanded:',int(boom_speed))
								Cmd_Boom(0)
								print('Boom Command Released')
								end_boom = time.time()
								print('Boom End Time:',end_boom)
								tot_boom += (end_boom - start_boom)
								print('tot_boom:',tot_boom)
								
							if SW2Pressed():
								time.sleep(0.5)
								print('In OPR Operation Screen: SW2 Pressed')
								start_bucket = time.time()
								print('Started recording Bucket Time:',start_bucket)
							 	while SW2Pressed():
									Cmd_Bucket(int(bucket_speed))
									print('Bucket Commanded:',int(bucket_speed))
								Cmd_Bucket(0)
								print('Bucket Command Released')
								end_bucket = time.time()
								print('end_bucket:',end_bucket)
								tot_bucket += (end_bucket - start_bucket)
								print('tot_bucket:',tot_bucket)

							if SW3Pressed():
								time.sleep(0.5)
								print('In OPR Operation Screen: SW3 Pressed, Logout NOW, Calculate various times')
								end_login_time = time.time()
								print('end_login_time:',end_login_time)
								time_diff_login_time = math.floor(end_login_time - start_login_time)
								print('time_diff_login_time',time_diff_login_time)
								login_time = int(login_time) + time_diff_login_time
								print('login_time',login_time)
								time.sleep(0.5)
								time_diff_operation_time = math.floor(tot_boom + tot_bucket)
								print('time_diff_operation_time',time_diff_operation_time)
								operation_time = int(operation_time) + time_diff_operation_time
								print('operation_time:',operation_time)
								time.sleep(0.5)
								try:
									print('Trying to commit timings in DB')
									cur.execute("UPDATE operator SET LoginTime=%s WHERE ID=%s", (str(login_time), str(position_id),))
									print('cur.execute: login time',login_time)
									cur.execute("UPDATE operator SET OperationTime=%s WHERE ID=%s", (str(operation_time), str(position_id),))
									print('cur.execute: operation time',operation_time)
									time.sleep(0.3)
									db.commit()
									print('Timings comitted in DB')
								except:
									print("DB UPDATE TIME ERROR")
								break

					elif SW2Pressed():	#Modify settings
						time.sleep(0.5)
						print('SW2 pressed in OPR Main Screen, came into Modify Settings')
						Disp_OprScreen_2(position_id,boom_speed,bucket_speed)
						boom_speed = int(boom_speed)
						bucket_speed = int(bucket_speed)
						while SW3Pressed()==False:		#while settings not saved
							if SW1Pressed():
								print('SW1 Pressed, modifying BOOM SPD')
								boom_speed = (boom_speed+5)%100
								time.sleep(0.5)
								print('Displaying Updated Boom SPD on LCD')
								if boom_speed<5:
									boom_speed = 5
								Disp_OprScreen_2(position_id,boom_speed,bucket_speed)
								print('Updated Boom SPD:',boom_speed)
							#REQUIRES DISPLAY OF CURRENT UNSAVED CHANGES IN SPEED
							elif SW2Pressed():
								print('SW2 Pressed, Modifying BUCKET SPD')
								bucket_speed = (bucket_speed+5)%100
								time.sleep(0.5)
								print('Displaying Updated Bucket SPD on LCD')
								if bucket_speed < 5:
									bucket_speed = 5
								Disp_OprScreen_2(position_id,boom_speed,bucket_speed)
								print('Updated Bucket SPD',bucket_speed)
						print('SW3 Pressed, settings updaated!')
						time.sleep(0.5)
						try:
							print('Trying to commit Updated Boom and Bucket SPD in DB')
							cur.execute("UPDATE operator SET BoomSpeed=%s WHERE ID=%s", (str(boom_speed), str(position_id),))
							print('cur.execute: Boom SPD',boom_speed)
							cur.execute("UPDATE operator SET BucketSpeed=%s WHERE ID=%s", (str(bucket_speed), str(position_id),))
							print('cur.execute: Bucket SPD',bucket_speed)
							time.sleep(0.3)
							db.commit()
							print('Updated Boom and Bucket SPD in DB')
						except:
							print("DB UPDATE SPD ERROR")

					elif SW3Pressed():		#Display yield screen
						time.sleep(0.5)
						print('SW3 pressed in OPR Main Screen, came into YLD Screen for current session')
						operation_time = int(operation_time)
						print('operation_time',operation_time)
						time.sleep(0.2)
						login_time = int(login_time)
						print('login_time',login_time)
						time.sleep(0.2)
						if login_time==0:
							login_time = 1
						Disp_OprScreen_3(position_id, (operation_time*100)//login_time, login_time//60)
						print('YLD:',(operation_time*100)//login_time)
						print('Fuel Used:',login_time//60)
						time.sleep(5)		
									
			else:	#owner
				print('Owner Fingerprint Detected, came into Owner Section')
				query_ownr = "SELECT * FROM owner WHERE ID=%s"
				cur.execute(query_ownr, (position_id,))
				rows_ownr = cur.fetchall()
				is_opr = False
				is_ownr = True
				for row in rows_ownr:
					operators_added = row[2]
				print('collected parameters of owner')
				
				while True:
					print('now displaying main screen of owner')
					Disp_OwnerScreen()

					#check buttons pressed
					if SW1Pressed():	#add new operator
						time.sleep(0.5)
						print('SW1 Pressed to add new Operator with default Settings')
						enrollFinger()
					elif SW2Pressed():	#Goto default screen
						time.sleep(0.5)
						print('OWNER Logout, Goto default screen')
						break
					elif SW3Pressed():	#invalid i/p
						time.sleep(0.5)
						print('Invalid INPUT, Goto default screen')
						break
	except:
		print('Catched Fingerprint Exception!')