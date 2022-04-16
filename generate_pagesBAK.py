#!/usr/bin/python3

import boto3
import datetime
import json
import mysql.connector
from mysql.connector import Error
import os
import sys

import includes.dbconn
from includes.dbconn import connection, cursor, get_row, get_rows, pcursor

# import includes.generate_home_page
# from includes.generate_home_page import generate_home_page
# from includes.generate_home_page import generate_season_page
from includes.generate_players_page import generate_players_page
from includes.generate_player_pages import generate_player_pages
from includes.generate_season_home_page import generate_season_home_page
from includes.generate_season_home_page import generate_season_nav_page
from includes.generate_trades_page import generate_trades_page

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

season = env["season"]

s3 = boto3.resource('s3')

###################################################

def create_owner_page(owner_id):

	with open('html/templates/owner.html') as file:
		page = file.read()

	page = update_owner_stats(owner_id, page)

	page = get_season_links(owner_id, page)

	page = get_most_picked_players(owner_id, page)

	print (page)

def get_most_picked_players(owner_id, page):

	mpp = ""

	query = f'SELECT player_id, drafted, fnf FROM owner_x_player_sums WHERE owner_id = {owner_id} ORDER BY drafted DESC LIMIT 5'

	players = get_rows(query)

	for player in players:

		print(player)

		player_id = player["player_id"]
		drafted = player["drafted"]
		fnf = player["fnf"]

		query = f'SELECT season FROM ownersXrosters WHERE owner_id = {owner_id} AND player_id = {player_id} ORDER BY season ASC'

		rows = get_rows(query)

		if len(rows) > 1:
			s = "s"
		else:
			s = ""

		seasons = ""

		for row in rows:

			season = row['season']

			seasons += str(season) + ", "

		seasons = seasons[:-2]

		print(seasons)

		link = f'/players/{player_id}'

		mpp += f'<a href = "{link}">{fnf}</a> ({drafted} time{s}): {seasons}<br>'

	mpp = mpp[:-4]

	page = page.replace('{most_picked_players}', mpp)

	return page


	# return mpp

	# print (mpp)

	# exit()

def get_season_links(owner_id, page):

	query = f'SELECT season FROM ownersXseasons WHERE owner_id = {owner_id} ORDER BY season DESC'

	rows = get_rows(query)

	season_links = ""

	for row in rows:

		season = row['season']

		season_links = season_links + f'<a class="dropdown-item" href="#{season}_{owner_id}">{season}</a>\n'

	page = page.replace('{season_links}', season_links)

	return page

def update_owner_stats(owner_id, page):

	query = f'SELECT * FROM owner_stats_detail WHERE owner_id = {owner_id}'

	row = get_row(query)

	for key in row:

		val = row[key]

		page = page.replace('{' + key + '}', str(val))

	return page

###################################################

push_to_s3 = env["push_to_s3"]

create_local_files = env["create_local_files"]

print ('Number of arguments:' + str(len(sys.argv)))
print ('Argument List:' + str(sys.argv))

for x in range(0, len(sys.argv)):

	arg = sys.argv[x]

	print(sys.argv[x])

	if arg == "--owner":

		owner_id = sys.argv[x + 1]

		print("the owner id is: " + str(owner_id))

		create_owner_page(owner_id)

	if arg == "--players":

		print("generate all player pages.")

	if arg == "--seasons":

		query = "SELECT * FROM seasons"

		rows = get_rows(query)

		for row in rows:
			season = row['season']

			if season == env["current_season"]:
				season_is_current = True
			else:
				season_is_current = False

			print("generating home page for season " + str(season))

			generate_season_home_page(connection, season, season_is_current, s3, env)

		generate_season_nav_page(connection, s3, env)

	if arg == "--season":

		season = int(sys.argv[x + 1])

		print("the season is: " + str(season))

		print("generating home page for season " + str(season))

		if season == env["current_season"]:
			season_is_current = True
		else:
			season_is_current = False

		generate_season_home_page(connection, season, season_is_current, s3, env)

		generate_players_page(connection, season, s3, push_to_s3, create_local_files)


exit()
