#!/usr/bin/python3

import json
import mysql.connector
from mysql.connector import Error

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

print("#######################################")
print("trying mysql connection...")

try:
	connection = mysql.connector.connect(host=env["host"], database=env["database"], user=env["user"], password=env["password"], port=env["port"], auth_plugin='mysql_native_password')

	cursor = connection.cursor(dictionary=True, buffered=True)
	pcursor = connection.cursor(prepared=True)
	tcursor = connection.cursor(dictionary=False)

	print("the mysql db connection worked.")

except mysql.connector.Error as error:
	print("query failed {}".format(error))

def get_row(query):
	try:
		cursor.execute(query)

		row = cursor.fetchone()

		return row

	except mysql.connector.Error as error:
		print("query failed {}".format(error))

def get_rows(query, no_cols = False):
	try:

		if no_cols:
			tcursor.execute(query)
			rows = tcursor.fetchall()
		else:
			cursor.execute(query)
			rows = cursor.fetchall()

		return rows

	except mysql.connector.Error as error:
		print("query failed {}".format(error))
