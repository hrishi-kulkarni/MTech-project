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
from RPLCD.gpio import CharLCD
from pyfingerprint.pyfingerprint import PyFingerprint

import mysql.connector
########### GPIO PIN Defines ########################

SW1=7
SW2=5
SW3=3

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
	db = mysql.connector.connect(user='root',password='',host='192.168.43.50',database='operatorpersonalization')
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
	time.sleep(0.002)
	lcd.write_string('Scan Fingerprint')
	time.sleep(0.002)
	lcd.cursor_pos=(1,0)
	time.sleep(0.002)
	lcd.write_string('to Crank machine')

################# Owner Screen ##########################

#if id == Owner load this screen
def Disp_OwnerScreen(id):
	lcd.clear()
	time.sleep(0.003)
	lcd.write_string("Welcome Ownr%s" %id)  
	# For formated string use:  lcd.write_string("Welcome %s" %Var Name) 
	time.sleep(0.003)
	lcd.cursor_pos=(1,0)
	time.sleep(0.003)
	lcd.write_string('Add Opr')
	time.sleep(0.003)
	lcd.cursor_pos=(1,13)
	lcd.write_string('Off')
	#if SW2=Pressed Load Default Screen


#if SW1= pressed, load this screen
def Disp_OwnerScreen_1_1():
	lcd.clear()
	time.sleep(0.003)
	lcd.write_string('Scan Fingergerprint')
	time.sleep(0.003)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Put-Remove-Put')

	#call enroll function in library


#After 1st scan ask to remove finger
def Disp_OwnerScreen_1_2():
	lcd.clear()
	time.sleep(0.003)
	lcd.write_string('Remove')
	

#After remove load this screen
def Disp_OwnerScreen_1_3():
	lcd.clear()
	time.sleep(0.003)
	lcd.write_string('Put Same')
	time.sleep(0.003)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Finger Again')


#After successful enroll show this screen
def Disp_OwnerScreen_1_4():
	lcd.clear()
	time.sleep(0.003)
	lcd.write_string('Opr Add Success')
	time.sleep(0.003)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Default Settings')
	#Jump to Default Screen after this screen


##################### Operator Screens ####################################

#Load this screen if id == Operator, start opr timer in seconds
def Disp_OprScreen(id):
	lcd.clear()
	time.sleep(0.001)
	lcd.write_string("Operator %s" %id)
	time.sleep(0.001)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Opr')
	time.sleep(0.001)
	lcd.cursor_pos=(1,6)
	lcd.write_string('Sett')
	time.sleep(0.001)
	lcd.cursor_pos=(1,13)
	lcd.write_string('Yld')
	#Make crank LED ON

#Load this screen if SW1=Pressed for Opr
def Disp_OprScreen_1(id):
	lcd.clear()
	time.sleep(0.001)
	lcd.write_string("Operator %s" %id)
	time.sleep(0.001)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Boom')
	time.sleep(0.001)
	lcd.cursor_pos=(1,7)
	lcd.write_string('Bkt')
	time.sleep(0.001)
	lcd.cursor_pos=(1,13)
	lcd.write_string('Off')

	#if SW1= Pressed, Cmd --> Boom, record time in seconds
	#if SW2= Pressed, Cmd --> Bucket, record time in secods

#Load this screen if SW2=Pressed for Sett
def Disp_OprScreen_2(id):
	lcd.clear()
	time.sleep(0.001)
	lcd.write_string("Operator %s Sett" %id)
	time.sleep(0.001)
	lcd.cursor_pos=(1,0)
	lcd.write_string('Boom')
	time.sleep(0.001)
	lcd.cursor_pos=(1,7)
	lcd.write_string('Bkt')
	time.sleep(0.001)
	lcd.cursor_pos=(1,12)
	lcd.write_string('Save')

	#if SW1= increment duty cycle of Boom +5
	#if SW2= increment duty cycle of Bucket +5
	#if SW3= Save settings of boom bucket and commit to DB for given operator

#Load this screen if SW3=Pressed for Yld
def Disp_OprScreen_3(id,yld,fuel):
	lcd.clear()
	time.sleep(0.001)
	lcd.write_string("Opr%s Yld:" %id)
	time.sleep(0.001)
	lcd.write_string("%s" %yld)
	lcd.cursor_pos=(1,0)
	#lcd.write_string("Fuel Use:%sltr", %fuel)			#Debug

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
	
def Cmd_Bucket(duty_cycle):
	pwm_bucket.start(duty_cycle)

def Insert_Operator():
	pass

def Insert_Owner():
	pass

def Update_Settings():
	pass

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
		global operators_added
		operators_added = int(operators_added)
		operators_added += 1
		cur.execute ("UPDATE owner SET NumberOfOperatorsAdded=%s", (str(operators_added),))
		db.commit()
	except:
		print("Error in database insert")



#main________________________
while(True):
	Disp_DefaultScreen()
	print("hello")
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
			print('No match found!')
			lcd.write_string('No match found')
		else:
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

				for row in rows_opr:
					login_time = row[2]
					operation_time = row[3]
					boom_speed = row[4]
					bucket_speed = row[5]

				#collected all parameters of logged in operator
				#call operator main screen
				while (is_opr == True)
				{
					Disp_OprScreen(position_id)
					print(login_time, operation_time, boom_speed, bucket_speed)
					if SW1Pressed():	#GOTO operation screen
						while(True)
						{
							Disp_OprScreen_1(position_id)
							if SW1Pressed():
								start_boom = time.time()
								while SW1Pressed():
									Cmd_Boom(int(boom_speed))
								end_boom = time.time()
								tot_boom += (end_boom - start_boom)
							if SW2Pressed():
								start_bucket = time.time()
								while SW2Pressed():
									Cmd_Bucket(int(bucket_speed))
								end_bucket = time.time()
								tot_bucket += (end_bucket - start_bucket)
							if SW3Pressed():
								end_login_time = time.time()
								login_time += (end_login_time - start_login_time)
								operation_time += (tot_boom + tot_bucket)
								try:
									cur.execute("UPDATE operator SET LoginTime=%s WHERE ID=%s", (str(login_time), str(position_id),))
									cur.execute("UPDATE operator SET OperationTime=%s WHERE ID=%s", (str(operation_time), str(position_id),))
									db.commit()
								except:
									print("DB UPDATE TIME ERROR")
						}

					elif SW2Pressed():	#Modify settings
						Disp_OprScreen_2(position_id)
						boom_speed = int(boom_speed)
						bucket_speed = int(bucket_speed)
						while SW3Pressed()==False:		#while settings not saved
							if SW1Pressed():
								boom_speed = (boom_speed+5)%100
								if boom_speed<5:
									boom_speed = 5
							#REQUIRES DISPLAY OF CURRENT UNSAVED CHANGES IN SPEED
							elif SW2Pressed():
								bucket_speed = (bucket_speed+5)%100
								if bucket_speed < 5:
									bucket_speed = 5
						try:
							cur.execute("UPDATE operator SET BoomSpeed=%s WHERE ID=%s" (str(boom_speed), str(position_id),))
							cur.execute("UPDATE operator SET BucketSpeed=%s WHERE ID=%s" (str(bucket_speed), str(position_id),))
							db.commit()
						except:
							print("DB UPDATE SETTING ERROR")
					
					elif SW3Pressed():		#Display yield screen
						operation_time = int(operation_time)
						login_time = int(login_time)
						Disp_OprScreen_3(position_id, (operation_time*100)//login_time, login_time//60)
				}		
									
			else:	#owner
				query_ownr = "SELECT * FROM owner WHERE ID=%s"
				cur.execute(query_ownr, (position_id,))
				rows_ownr = cur.fetchall()
				is_opr = False
				is_ownr = True
				for row in rows_ownr:
					operators_added = row[2]
				#collected parameters of owner
				#now display basic screen of owner

				while(is_ownr == True)
				{
					Disp_OwnerScreen(position_id)

					#check buttons pressed
					if SW1Pressed():	#add new operator
						enrollFinger()
					elif SW2Pressed():	#Goto default screen
						break
					elif SW3Pressed():	#invalid i/p
						break
				}
	except:
		print('Operation failed!')
		print('Exception message: ')