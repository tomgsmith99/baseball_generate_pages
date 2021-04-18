#!/usr/bin/python3

import boto3
import datetime
import json
# import mysql.connector
# from mysql.connector import Error
# import os

###################################################

import includes.dbconn
from includes.dbconn import get_rows, get_row

with open('.env.json') as json_file:
	env = json.load(json_file)

###################################################
# FUNCTION DEFINITIONS
###################################################

season = env["season"]

###################################################

content = {
	"season": season,
	"page_generated": datetime.datetime.now()
}

###################################################
###################################################
# trades.html

query = "SELECT * FROM trades_view ORDER BY stamp DESC"

print(query)

rows = get_rows(query)

print(rows)

with open("html/templates/trade_row.html") as file:
	template = file.read()

vals = ["added_player_fnf", "date", "dropped_player_fnf", "nickname", "pos"]

table_rows = ""

for row in rows:

	trade_row = template

	added_player_id = row["added_player_id"]
	dropped_player_id = row["dropped_player_id"]

	query = f"SELECT * FROM players_current_view WHERE player_id = {added_player_id}"

	r = get_row(query)

	row["added_player_fnf"] = r["fnf"]

	row["pos"] = r["pos"]

	query = f"SELECT * FROM players WHERE player_id = {dropped_player_id}"

	r = get_row(query)

	row["dropped_player_fnf"] = r["fnf"]

	m = row["stamp"].strftime("%b")
	d = row["stamp"].strftime("%d")

	row["date"] = m + " " + d

	for val in vals:

		trade_row = trade_row.replace("{" + val + "}", row[val])

	table_rows += trade_row

with open("html/templates/trade_table.html") as file:
	template = file.read()

template = template.replace("{trades}", table_rows)

###################################################

with open("html/templates/base.html") as file:
	base = file.read()

base = base.replace("{title}", "trades")

base = base.replace("{page_generated}", str(content["page_generated"]))

base = base.replace("{main}", template)

base = base.replace("{season}", str(season))

###################################################

f = open("html/output/trades.html", "w")
f.write(base)
f.close()

###################################################

s3 = boto3.resource('s3')

x = datetime.datetime.now()

day = str(x.day)
month = str(x.month)

if len(month) == 1:
	month = "0" + month
if len(day) == 1:
	day = "0" + day

filename = str(x.year) + "-" + month + "-" + day + ".html"

s3.Bucket('baseball.tomgsmith.com').put_object(Key='trades/' + str(season) + '/index.html', Body=base, ContentType='text/html', ACL='public-read')
s3.Bucket('baseball.tomgsmith.com').put_object(Key='backup/' + filename, Body=base, ContentType='text/html', ACL='public-read')

