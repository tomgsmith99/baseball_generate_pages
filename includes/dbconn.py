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
	connection = mysql.connector.connect(host=env["host"], database=env["database"], user=env["user"], password=env["password"], port=env["port"])

	cursor = connection.cursor(dictionary=True)
	pcursor = connection.cursor(prepared=True)

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

def get_rows(query):
	try:
		cursor.execute(query)

		rows = cursor.fetchall()

		return rows

	except mysql.connector.Error as error:
		print("query failed {}".format(error))
