import mysql.connector
#database connectivity
try:
	db = mysql.connector.connect(user='root',password='',host='192.168.43.229',database='operatorpersonalization')
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
	position_id = 10
	#query = "INSERT INTO operator VALUES(%s,%s,%s,%s,%s,%s)"
	#args = (str(position_id), 'operator'+str(position_id), '0', '0', '50', '50')
	#try:
	#	cur.execute(query, args)
	#	db.commit()
	#except:
	#	print("Error in database insert")
	operators_added = 11
	cur.execute ("UPDATE owner SET NumberOfOperatorsAdded=%s", (str(operators_added),))
	db.commit()

except:
	print("database connection error")