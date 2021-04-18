#!/usr/bin/python3

import boto3
import datetime
import json
import mysql.connector
from mysql.connector import Error
import os

###################################################

base_path = ""

if os.getcwd() == "/home/tomgsmith99":
	base_path = "/home/tomgsmith99/bin/baseball_generate_pages/"

###################################################

with open(base_path + '.env.json') as json_file:
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

###################################################
# FUNCTION DEFINITIONS
###################################################

season = env["season"]

###################################################

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

def make_ordinal(n):
	n = int(n)
	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	return str(n) + suffix

###################################################

content = {
	"season": season,
	"page_generated": datetime.datetime.now()
}

###################################################
# Get main list of owners

owner_rows_summary = ""

with open(base_path + "html/templates/owner_row_home_page.html") as file:
	template = file.read()

query = "SELECT * FROM ownersXseasons_current_view ORDER BY points DESC, nickname ASC"

print(query)

rows = get_rows(query)

# see if any owners are tied and calculate place accordingly

places = {}

prev_owner_points = 0

i = 0

place = 0

for row in rows:

	i += 1

	owner_id = row["owner_id"]

	if row["points"] == prev_owner_points:
		places[owner_id] = place
	else:
		places[owner_id] = i
		place = i

	prev_owner_points = row["points"]

# now generate owner rows

for row in rows:

	this_row = template

	owner_id = row["owner_id"]

	row["link"] = str(season) + "_" + str(row["owner_id"])

	row["place"] = places[owner_id]

	if row["head_shot"]:
		url = row["head_shot"]
		row["head_shot"] = f'<img src="{url}">'

	fields = ["head_shot", "link", "nickname", "place", "points", "team_name"]

	for field in fields:
		this_row = this_row.replace("{" + field + "}", str(row[field]))

	owner_rows_summary += this_row

content["owner_rows_summary"] = owner_rows_summary

###################################################
# owner drop-down

owner_dropdown = ""

template = "<a class='dropdown-item' href='#{link}'>{nickname}</a>"

query = "SELECT * FROM ownersXseasons_current_view ORDER BY nickname ASC"

print(query)

rows = get_rows(query)

for row in rows:

	this_row = template

	link = str(season) + "_" + str(row["owner_id"])

	this_row = this_row.replace("{link}", link)
	this_row = this_row.replace("{nickname}", row["nickname"])

	owner_dropdown += this_row + "\n"

content["owner_dropdown"] = owner_dropdown

###################################################
# owner detailed teams

teams = ""

with open(base_path + "html/templates/owner_team_detail.html") as file:
	template = file.read()

query = "SELECT * FROM ownersXseasons_current_view ORDER BY points DESC"

print(query)

rows = get_rows(query)

for row in rows:

	owner_id = row["owner_id"]

	place = places[owner_id]

	this_team = template

	row["season"] = season

	row["link"] = str(season) + "_" + str(row["owner_id"])

	row["place"] = make_ordinal(place)

	fields = ["bank", "link", "nickname", "salary", "place", "points", "season", "team_name"]

	for field in fields:
		this_team = this_team.replace("{" + field + "}", str(row[field]))

	query = f'SELECT * FROM oxrcXpos WHERE owner_id={row["owner_id"]}'
	query += " ORDER BY o ASC, salary DESC"

	print(query)

	players = get_rows(query)

	with open(base_path + "html/templates/player_in_team.html") as file:
		player_template = file.read()

	active_html = ""

	bench_html = ""

	for p in players:

		if p["recent"] == -1:
			p["recent"] = "N/A"

		if p["yesterday"] == -1:
			p["yesterday"] = "N/A"

		this_player = player_template

		fields = ["fnf", "pos", "player_id", "points", "recent", "salary", "team", "value", "yesterday"]

		for field in fields:
			this_player = this_player.replace("{" + field + "}", str(p[field]))

		if p["acquired"] == 1:
			this_player = this_player.replace("{font-style}", "italic")
		else:
			this_player = this_player.replace("{font-style}", "normal")

		if p["benched"] == 1:
			bench_html += this_player
		else:
			active_html += this_player

	if bench_html != "":
		bench_html = '<tr><td colspan="10" style="text-align: center;">Benched players</td></tr>\n' + bench_html

	this_team = this_team.replace("{active_html}", active_html)
	this_team = this_team.replace("{bench_html}", bench_html)

	teams += this_team

content["teams"] = teams

###################################################
# most productive players - picked
# {most_productive_players-picked}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, points FROM players_current_view WHERE picked > 0 ORDER BY points DESC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["points"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["most_productive_players-picked"] = html

###################################################
# most productive players - picked
# {most_valuable_players-picked}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, value FROM players_current_view WHERE picked > 0 ORDER BY value DESC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["value"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["most_valuable_players-picked"] = html

###################################################
# most productive players - picked
# {most_popular_players}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, picked FROM players_current_view ORDER BY picked DESC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["picked"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["most_popular_players"] = html

###################################################
# most productive players - all
# {most_productive_players-all}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, points FROM players_current_view ORDER BY points DESC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["points"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["most_productive_players-all"] = html

###################################################
# most valuable players - all
# {most_valuable_players-all}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, value FROM players_current_view ORDER BY value DESC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["value"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["most_valuable_players-all"] = html

###################################################
# yesterday's top owners
# {yesterday_top_owners}

html = ""

with open(base_path + "html/templates/owner_row_tiny.html") as file:
	template = file.read()

query = "SELECT nickname, owner_id, yesterday FROM ownersXseasons_current_view ORDER BY yesterday DESC, nickname ASC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"owner_id": row["owner_id"],
		"nickname": row["nickname"],
		"cat_val": row["yesterday"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["yesterday_top_owners"] = html

###################################################
# hot owners
# {hot_owners}

html = ""

with open(base_path + "html/templates/owner_row_tiny.html") as file:
	template = file.read()

query = "SELECT nickname, owner_id, recent FROM ownersXseasons_current_view ORDER BY recent DESC, nickname ASC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"owner_id": row["owner_id"],
		"nickname": row["nickname"],
		"cat_val": row["recent"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["hot_owners"] = html

###################################################
# yesterday's top players
# {yesterday_top_players}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, yesterday FROM players_current_view ORDER BY yesterday DESC, lnf ASC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["yesterday"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["yesterday_top_players"] = html

###################################################
# hot players
# {hot_players}

html = ""

with open(base_path + "html/templates/player_row_tiny.html") as file:
	template = file.read()

query = "SELECT fnf, player_id, recent FROM players_current_view ORDER BY recent DESC, lnf ASC LIMIT 5"

print(query)

rows = get_rows(query)

i = 0

for row in rows:
	i += 1

	this_player = template

	vals = {
		"rank": i,
		"player_id": row["player_id"],
		"fnf": row["fnf"],
		"cat_val": row["recent"]
	}

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(vals[val]))

	html += this_player + "\n"

content["hot_players"] = html

###################################################
# last updated
# {last_updated}

query = "SELECT update_desc FROM updates ORDER BY time_of_update DESC LIMIT 1"

print(query)

row = get_row(query)

content["last_updated"] = row["update_desc"]

###################################################

content["title"] = "standings"

with open(base_path + "html/templates/base.html") as file:
	base = file.read()

with open(base_path + "html/templates/home.html") as file:
	home = file.read()

home = base.replace("{main}", home)

for chunk in content:
	home = home.replace("{" + chunk + "}", str(content[chunk]))

f = open(base_path + "html/output/index.html", "w")
f.write(home)
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

s3.Bucket('baseball.tomgsmith.com').put_object(Key='index.html', Body=home, ContentType='text/html', ACL='public-read')
s3.Bucket('baseball.tomgsmith.com').put_object(Key='backup/' + filename, Body=home, ContentType='text/html', ACL='public-read')

###################################################
###################################################
# players.html

query = "SELECT * FROM players_current_view ORDER BY points DESC, lnf ASC"

html = ""

with open(base_path + "html/templates/player_in_player_table.html") as file:
	template = file.read()

rows = get_rows(query)

for row in rows:

	if row["recent"] == -1:
		row["recent"] = "N/A"

	if row["yesterday"] == -1:
		row["yesterday"] = "N/A"

	player_id = row["player_id"]

	fnf = row["fnf"]

	row["name_with_link"] = f'<a href="/players/{player_id}" target="_blank">{fnf}</a>'

	this_player = template

	vals = ["points", "name_with_link", "pos", "yesterday", "recent", "salary", "team", "value", "drafted", "picked"]

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(row[val]))

	html += this_player + "\n"

content["player_rows"] = html

###################################################

with open(base_path + "html/templates/base.html") as file:
	base = file.read()

with open(base_path + "html/templates/players.html") as file:
	players_page = file.read()

players_page = base.replace("{main}", players_page)

for chunk in content:
	players_page = players_page.replace("{" + chunk + "}", str(content[chunk]))

f = open(base_path + "html/output/players.html", "w")
f.write(players_page)
f.close()

###################################################

s3.Bucket('baseball.tomgsmith.com').put_object(Key='seasons/' + str(season) + '/players/index.html', Body=players_page, ContentType='text/html', ACL='public-read')
s3.Bucket('baseball.tomgsmith.com').put_object(Key='backup/players/' + filename, Body=players_page, ContentType='text/html', ACL='public-read')

###################################################
###################################################
# trades.html

query = "SELECT * FROM players_current_view ORDER BY points DESC, lnf ASC"

html = ""

with open(base_path + "html/templates/player_in_player_table.html") as file:
	template = file.read()

rows = get_rows(query)

for row in rows:

	if row["recent"] == -1:
		row["recent"] = "N/A"

	if row["yesterday"] == -1:
		row["yesterday"] = "N/A"

	player_id = row["player_id"]

	fnf = row["fnf"]

	row["name_with_link"] = f'<a href="/players/{player_id}" target="_blank">{fnf}</a>'

	this_player = template

	vals = ["points", "name_with_link", "pos", "yesterday", "recent", "salary", "team", "value", "drafted", "picked"]

	for val in vals:
		this_player = this_player.replace("{" + val + "}", str(row[val]))

	html += this_player + "\n"

content["player_rows"] = html
exit()
