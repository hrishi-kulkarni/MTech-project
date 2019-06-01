import mysql.connector
#database connectivity
try:
	db = mysql.connector.connect(user='root',password='',host='192.168.43.44',database='operatorpersonalization')
	print('here')
	cur = db.cursor()
	print("2")
	tmp = '1'
	query1 = 'SELECT * FROM owner WHERE ID= %s'
	#cur.execute(query1, (tmp,))
	print("3")
	#cnt = cur.rowcount
	#records = cur.fetchall()
	#for row in records:
	#	print(row[0], row[1], row[2])
	position_id = 2
	#query = "INSERT INTO operator VALUES(%s,%s,%s,%s,%s,%s)"
	#args = (str(position_id), 'operator'+str(position_id), '0', '0', '50', '50')
	#try:
	#	cur.execute(query, args)
	#	db.commit()
	#except:
	#	print("Error in database insert")
	boom_speed = 200
	bucket_speed = 100
	login_time = 60000
	operation_time = 5000
	#operators_added = 11
	
	#cur.execute ("UPDATE owner SET NumberOfOperatorsAdded=%s", (str(operators_added),))
	cur.execute("UPDATE operator SET BoomSpeed=%s WHERE ID=%s", (str(boom_speed),str(position_id),))
	print('Boom Spd updated')
	#cur.execute("UPDATE operator SET BucketSpeed=%s WHERE ID=%s" (str(bucket_speed), str(position_id),))
	#print('Bucket Spd Updated')
	#cur.execute("UPDATE operator SET LoginTime=%s WHERE ID=%s", (str(login_time), str(position_id),))
	#print('Login Time updated')
	#cur.execute("UPDATE operator SET OperationTime=%s WHERE ID=%s", (str(operation_time), str(position_id),))
	db.commit()

except:
	print("database connection error")