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

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

###################################################

globals()['push_to_s3'] = False
globals()['season'] = env['season']

make_a_trade_link = 'https://tomgsmith99-baseball-trade.herokuapp.com/'

###################################################

def generate_page(subject, item_id=0):

	obj = {
		'page_generated': datetime.datetime.now()
	}

	if subject == 'current':

		season = globals()['season']

		obj['title'] = 'Baseball ' + str(season)
		obj['make_a_trade'] = 'none'
		obj['season_page'] = True
		obj['season_is_current'] = True
		obj['season'] = season
		obj['owner_rows'] = get_owner_rows(season)
		obj['owners'] = get_owners(season)
		obj['teams'] = get_teams(season)
		obj['last_updated'] = get_last_updated()
		obj['leaderboards'] = get_leaderboards(season, True)

		path = ''

	if subject == 'history':

		obj['title'] = 'Baseball: History'
		obj['history'] = True

		with open('./data/history.json') as json_file:
			obj['sections'] = json.load(json_file)

		path = 'history/'

	if subject == 'players':

		season = item_id

		obj['title'] = 'Baseball: ' + str(season) + ' Players'
		obj['players_page'] = True
		obj['season'] = season
		obj['players'] = get_players(season)

		path = f'seasons/{season}/players/'

	if subject == 'season':

		season = item_id

		obj['title'] = 'Baseball: Final Standings ' + str(season)
		obj['season_page'] = True
		obj['season'] = season
		obj['season_is_current'] = False
		obj['owner_rows'] = get_owner_rows(season)
		obj['owners'] = get_owners(season)
		obj['teams'] = get_teams(season)
		obj['leaderboards'] = get_leaderboards(season, False)

		path = f'seasons/{season}/'

	if subject == 'trades':

		season = item_id

		obj['title'] = 'Baseball: Trades ' + str(season)
		obj['trades_page'] = True
		obj['season'] = season
		obj['trades'] = get_trades(season)
		obj['make_a_trade_link'] = make_a_trade_link

		path = f'seasons/{season}/trades/'

	###############################################
	# generate files
	###############################################

	with open('html/templates/base.html', 'r') as f:

		args = {
			'template': f,
			'data': obj,
			'partials_path': 'partials/',
			'partials_ext': 'html'
		}

		page = chevron.render(**args)

	path = path + 'index.html'

	if env['create_local_files']:

		write_local_file(f'{env["local_home"]}{path}', page)

	if globals()['push_to_s3']:

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

def get_command_line_args():

	print ('Number of arguments:' + str(len(sys.argv)))
	print ('Argument List:' + str(sys.argv))

	if len(sys.argv) == 1:
		return False

	if '--push_to_s3' in sys.argv:

		globals()['push_to_s3'] = True

	########################################

	if '--current' in sys.argv:

		generate_page('current')

	if '--help' in sys.argv or '-h' in sys.argv:

		print('available commands: ')
		print('--current: generate current season home page')
		print('--history: generate the narrative history page')
		print('--players [season]: generate the players home page for a season')
		print('--season [season]: generate the season home page for a season')

		exit()

	if '--history' in sys.argv:

		generate_page('history')

	if '--players' in sys.argv:

		index = sys.argv.index('--players')

		season = sys.argv[index + 1]

		generate_page('players', season)

	if '--season' in sys.argv:

		index = sys.argv.index('--season')

		season = sys.argv[index + 1]

		print('the season is: ' + season)

		generate_page('season', season)

	if '--trades' in sys.argv:

		index = sys.argv.index('--trades')

		season = sys.argv[index + 1]

		print('the season is: ' + season)

		generate_page('trades', season)

	for x in range(0, len(sys.argv)):

		arg = sys.argv[x]

		if arg == "--owner":

			owner_id = sys.argv[x + 1]

			print("the owner id is: " + str(owner_id))

			create_owner_page(owner_id)

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

	exit()

def get_last_updated():

	query = f'SELECT update_desc FROM updates ORDER BY time_of_update DESC LIMIT 1'

	row = get_row(query)

	return row['update_desc']

def get_leaderboards(season, is_current):

	current_leaderboards = [
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
		}
	]

	leaderboards = [
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

	if (is_current):
		return current_leaderboards + leaderboards
	else:
		return leaderboards

def get_leaders(col, person_type, season, picked_only=True):

	if person_type == 'owner':
		name_col = 'nickname'
		table = 'ownersXseasons_detail'

	if person_type == 'player':
		name_col = 'fnf'

		if picked_only:
			table = 'player_x_season_leaderboard_rostered_only'
		else:
			table = 'player_x_season_leaderboard_all' 

	query = f'SELECT {name_col} AS name, {col} AS val FROM {table} WHERE season={season} ORDER BY {col} DESC, {name_col} ASC LIMIT 5'

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

def get_trades(season): 

	query = f'SELECT * FROM trades_detail WHERE season = {season} AND owner_id != 63 ORDER BY stamp DESC'

	trades = get_rows(query)

	for x in range(0, len(trades)):

		added_id = trades[x]['added_player_id']

		dropped_id = trades[x]['dropped_player_id']

		query = f'SELECT fnf FROM players WHERE player_id = {added_id}'

		r = get_row(query)

		trades[x]['added_fnf'] = r['fnf']

		query = f'SELECT fnf FROM players WHERE player_id = {dropped_id}'

		r = get_row(query)

		trades[x]['dropped_fnf'] = r['fnf']

		d = trades[x]['stamp'].strftime('%b %-d')

		trades[x]['date'] = trades[x]['stamp'].strftime('%b %-d')

		query = f'SELECT pos FROM playersXseasons WHERE player_id = {dropped_id}'

		r = get_row(query)

		trades[x]['pos'] = r['pos']

	return trades

def make_ordinal(n):
	n = int(n)
	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	return str(n) + suffix

def push_to_s3(path, page):

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

def show_options():

	print('1) current home page')
	print('2) players page')
	print('3) generate history page')

	val = int(input("Which do you want to do? "))

	print(val)

	if val == 1:

		generate_page('current')

	if val == 2:

		val = int(input("Which season? "))

		generate_page('players', val)

	if val == 3:

		generate_page('history')

def write_local_file(path, page):

	f = open(path, "w")

	f.write(page)

	f.close()

##############################################################

if not get_command_line_args():

	print("no command line args.")

else:

	print("some command line args were supplied.")

exit()
