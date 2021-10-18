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

push_to_s3 = env["push_to_s3"]

create_local_files = env["create_local_files"]

print ('Number of arguments:' + str(len(sys.argv)))
print ('Argument List:' + str(sys.argv))

for x in range(0, len(sys.argv)):

	arg = sys.argv[x]

	print(sys.argv[x])

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

		season = sys.argv[x + 1]

		print("the season is: " + str(season))

		print("generating home page for season " + str(season))

		if season == env["current_season"]:
			season_is_current = True
		else:
			season_is_current = False

		generate_season_home_page(connection, season, season_is_current, s3, env)

# generate_players_page(connection, season, s3, push_to_s3, create_local_files)

# generate_trades_page(connection, season, s3, push_to_s3, create_local_files)

# generate_player_pages(connection, season, s3, push_to_s3, create_local_files)

exit()
