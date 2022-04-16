#!/usr/bin/python3

import boto3
import chevron
import datetime
import json
import mysql.connector
from mysql.connector import Error
import os
import sys

import includes.dbconn
from includes.dbconn import connection, cursor, get_row, get_rows, pcursor

from includes.generate_players_page import generate_players_page
from includes.generate_player_pages import generate_player_pages
# from includes.generate_season_home_page import generate_season_home_page
from includes.generate_season_home_page import generate_season_nav_page
from includes.generate_trades_page import generate_trades_page

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

season = env['season']

###################################################

push_to_s3 = False

###################################################

def generate_page(subject, push_to_s3):

	obj = {
		'page_generated': datetime.datetime.now()
	}

	if subject == 'current':

		obj['title'] = 'Baseball ' + str(season)
		obj['make_a_trade'] = 'none'
		obj['home_current'] = True
		obj['season'] = season
		obj['owner_rows'] = get_owner_rows(season)
		obj['owners'] = get_owners(season)
		obj['teams'] = get_teams(season)
		obj['last_updated'] = get_last_updated()
		obj['page_generated'] = datetime.datetime.now()
		obj['leaderboards'] = get_leaderboards(season)

		path = ''

	if subject == 'history':

		obj['title'] = 'Baseball: History'
		obj['history'] = True

		with open('./data/history.json') as json_file:
			obj['sections'] = json.load(json_file)

		path = 'history/'

	with open('html/templates/base.html', 'r') as f:

		args = {
			'template': f,
			'data': obj,
			'partials_path': 'partials/',
			'partials_ext': 'ms'
		}

		page = chevron.render(**args)

	# print(page)

	# if not os.path.isdir(local_home + 'history'):
	# 	os.mkdir(f'{local_home}history')

	# f = open(f'{local_home}history/index.html', "w")

	path = path + "index.html"

	if env['create_local_files']:

		local_home = env['local_home']

		f = open(f'{local_home}{path}', "w")

		f.write(page)

		f.close()

	if push_to_s3:

		print('pushing page to s3...')

		session = boto3.Session(
			aws_access_key_id=env['accessKeyId'],
			aws_secret_access_key=env['secretAccessKey']
		)

		s3 = session.resource('s3')

		s3_bucket = env["s3_bucket"]

		my_bucket = s3.Bucket(s3_bucket)

		my_bucket.put_object(Key=path, Body=page, ContentType='text/html', ACL='public-read')

		# s3.Bucket(s3_bucket).put_object(Key=path, Body=page, ContentType='text/html', ACL='public-read')

		# if page == "home" or page == "players":
		# 	x = datetime.datetime.now()

		# 	filename_base = x.strftime("%Y_%m_%d_%H_%M_%S")

		# 	filename = filename_base + ".html"

		# 	backup_path = "backup/" + remote_path + filename

		# 	s3.Bucket(s3_bucket).put_object(Key=backup_path, Body=content, ContentType='text/html', ACL='public-read')

	else:
		print('push_to_s3 is false.')

def generate_players_page(season):

	obj = {}

	obj['title'] = 'Baseball: ' + str(season) + ' Players'
	obj['players_page'] = True
	obj['make_a_trade'] = 'none'
	obj['season'] = season
	obj['players'] = get_players(season)
	obj['page_generated'] = datetime.datetime.now()

	with open('html/templates/base.html', 'r') as f:

		args = {
			'template': f,
			'data': obj,
			'partials_path': 'partials/',
			'partials_ext': 'ms'
		}

		page = chevron.render(**args)

		print(page)

		if not os.path.isdir(local_home + "seasons"):
			os.mkdir(f'{local_home}seasons')

		if not os.path.isdir(f'{local_home}seasons/{season}'):
			os.mkdir(f'{local_home}seasons/{season}')

		if not os.path.isdir(f'{local_home}seasons/{season}/players'):
			os.mkdir(f'{local_home}seasons/{season}/players')

		f = open(f'{local_home}seasons/{season}/players/index.html', "w")
		f.write(page)
		f.close()

def get_command_line_args():

	print ('Number of arguments:' + str(len(sys.argv)))
	print ('Argument List:' + str(sys.argv))

	if len(sys.argv) == 1:
		return False

	if '--push_to_s3' in sys.argv:

		push_to_s3 = True

	for x in range(0, len(sys.argv)):

		arg = sys.argv[x]

		# print(sys.argv[x])

		if arg == "--current":

			generate_page('current', push_to_s3)

		if arg == "--history":

			generate_page('history')

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

def get_last_updated():

	query = f'SELECT update_desc FROM updates ORDER BY time_of_update DESC LIMIT 1'

	row = get_row(query)

	return row['update_desc']

def get_leaderboards(season):

	leaderboards = [
		{
			'title': "Yesterday's top owners",
			'href': "#",
			'leaders': get_leaders('yesterday', 'owner', season)
		},
		{
			'title': 'Hot owners',
			'href': "#",
			'leaders': get_leaders('recent', 'owner', season)
		},
		{
			'title': "Yesterday's top players (picked)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('yesterday', 'player', season)
		},
		{
			'title': "Hot players (picked)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('recent', 'player', season)
		},
		{
			'title': "Most Productive Players (picked)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('points', 'player', season)
		},
		{
			'title': "Most Valuable Players (picked)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('value', 'player', season)
		},
		{
			'title': "Most Popular Players",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('drafted', 'player', season)
		},
		{
			'title': "Most Productive Players (all)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('points', 'player', season, False)
		},
		{
			'title': "Most Valuable Players (all)",
			'href': f'/seasons/{season}/players',
			'leaders': get_leaders('value', 'player', season, False)
		}
	]

	return leaderboards

def get_leaders(col, person_type, season, picked_only=True):

	picked_clause = ''

	if person_type == 'owner':
		name_col = 'nickname'
		table = 'ownersXseasons_detail'

	if person_type == 'player':
		name_col = 'fnf'
		table = 'player_x_season_detail'

		if picked_only:
			picked_clause = 'AND (drafted > 0 OR acquired > 0)'

	query = f'SELECT {name_col} AS name, {col} AS val FROM {table} WHERE season={season} {picked_clause} ORDER BY {col} DESC, {name_col} ASC LIMIT 5'

	print(query)

	rows = get_rows(query)

	i = 1

	for x in range(0, len(rows)):
		rows[x]['rank'] = i
		i += 1


	print(rows)

	return rows

def get_owner_rows(season):

	query = f'SELECT * FROM ownersXseasons_detail WHERE season = {season} AND owner_id != 63 ORDER BY place, nickname ASC'

	rows = get_rows(query)

	for row in rows:
		row['place'] = make_ordinal(row['place'])

	return rows

def get_owners(season):

	query = f'SELECT owner_id, nickname, season FROM ownersXseasons_detail WHERE season = {season} ORDER BY nickname ASC'

	rows = get_rows(query)

	return rows

def get_players(season):

	query = f'SELECT * FROM player_x_season_detail WHERE season={season} ORDER BY lnf'

	rows = get_rows(query)

	return rows

def get_roster(owner_id, season, active_or_benched):

	if active_or_benched == "active":
		clause = "benched = 0"
	else:
		clause = "benched > 0"

	query = f'SELECT * FROM owner_x_roster_detail WHERE owner_id = {owner_id} AND season = {season} AND {clause} ORDER BY o ASC, salary DESC'

	players = get_rows(query)

	for x in range(0, len(players)):
		if players[x]['yesterday'] == -1:
			players[x]['yesterday'] = "N/A"
		if players[x]['recent'] == -1:
			players[x]['recent'] = "N/A"

	return players

def get_teams(season):

	query = f'SELECT DISTINCT owner_id FROM ownersXseasons_detail WHERE season = {season} AND owner_id != 63 ORDER BY nickname ASC'

	rows = get_rows(query)

	teams = []

	for row in rows:

		print(row)

		owner_id = row['owner_id']

		query = f'SELECT bank, nickname, owner_id, place, points, recent, salary, season, team_name, yesterday FROM ownersXseasons_detail WHERE owner_id = {owner_id} AND season = {season}'

		team = get_row(query)

		team['place'] = make_ordinal(team['place'])

		team['active_players'] = get_roster(owner_id, season, "active")

		benched_players = get_roster(owner_id, season, "benched")

		if (len(benched_players)) > 0:
			team['has_benched_players'] = True

			team['benched_players'] = benched_players

		teams.append(team)

	return teams

def make_ordinal(n):
	n = int(n)
	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	return str(n) + suffix

##############################################################

if not get_command_line_args():

	print("no command line args.")

else:

	print("some command line args were supplied.")

	exit()

print('1) current home page')
print('2) players page')
print('3) generate history page')

val = int(input("Which do you want to do? "))

print(val)

if val == 1:
	generate_home_page_current()

if val == 2:

	val = int(input("Which season? "))

	generate_players_page(season)

else:
	get_leaderboards(season)


exit()

##############################################################

