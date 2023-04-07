#!/usr/bin/python3

import boto3
import chevron
import copy
import datetime
import json
import os
import sys

from includes.dbconn import get_row, get_rows

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

with open('settings.json') as file:
	settings = json.load(file)

sections = list(settings.keys())

special_args = ['owners_all', 'players_all_seasons', 'seasons_all', 'trades_all_seasons']

valid_args = sections + special_args

###################################################

PUSH_TO_S3 = False

TEST_OWNER_ID = '63'

###################################################

def evaluate_kw(kw):

	global sections

	if kw in sections:

		print("the keyword is in a section.")

		if 'requires_id' in settings[kw] and settings[kw]['requires_id']:

			if len(sys.argv) < 3:
				print("you must supply an id on the command line for this to work.")

			else:
				generate_page(kw, sys.argv[2])

		else:
			generate_page(kw)

		exit()
		
	else:

		print("\nthe keyword is not in a section.")

		# if kw == 'current':

		# 	generate_page('current')

		if kw == 'owners_all':

			query = f'SELECT owner_id FROM owner_valid ORDER BY owner_id ASC'

			owners = get_rows(query)

			for owner in owners:

				generate_page('owner', str(owner['owner_id']))
		
		if kw == 'players_all_seasons':

			for season in range(env['season_last'], env['full_stats_begin'] - 1, -1):

				generate_page('players', str(season))

		if kw == 'seasons_all':

			for season in range(env['season_last'], env['season_first'] - 1, -1):

				generate_page('season', str(season))

		if kw == 'trades_all_seasons':

			for season in range(env['season_last'], env['full_stats_begin'] - 1, -1):

				if is_valid_trade_season(int(season)):

					generate_page('trades', str(season))

		exit()

def generate_page(subject, item_id=0):

	obj = copy.deepcopy(settings[subject])

	if subject == 'top_six_finishes':

		obj['seasons'] = []

		query = 'SELECT DISTINCT season FROM owner_x_top_six_finishes ORDER BY season DESC'

		rows = get_rows(query)

		for row in rows:

			season = row['season']

			query = f'SELECT owner_id, nickname, place FROM owner_x_top_six_finishes WHERE season = {season} ORDER BY place'

			owners = get_rows(query)

			obj['seasons'].append({
				'season': season,
				'owners': owners
			})

	if subject == 'history':

		with open('./data/history.json') as json_file:
			obj['sections'] = json.load(json_file)

	if subject == 'owner':

		owner_id = item_id

		query = f'SELECT * FROM owner_stats WHERE owner_id = {owner_id}'

		owner = get_row(query)

		obj['heading'] = owner['nickname']

		owner['best_finish_detail'] = get_best_finish_detail(owner_id, owner['best_finish'])

		owner['best_finish'] = make_ordinal(owner['best_finish'])

		owner['appearances_desc'] = get_desc("appearances_rank", owner['appearances_rank'])
		owner['championships_desc'] = get_desc("championships_rank", owner['championships_rank'])
		owner['top_six_finishes_desc'] = get_desc("top_six_finishes_rank", owner['top_six_finishes_rank'])
		owner['rating_desc'] = get_desc("rating_rank", owner['rating_rank'])

		######################################################
		# Get seasons for this owner

		owner['seasons'] = []

		query = f'SELECT season FROM owner_x_season WHERE owner_id = {owner_id} ORDER BY season DESC'

		owner['seasons'] = get_rows(query)

		######################################################
		# Get list of seasons with rosters
		# Also figure out if owner has appearances prior to 2004

		owner['has-finishes-pre-full-stats'] = False

		owner['seasons_with_rosters'] = []

		for season in owner['seasons']:
			if season['season'] < env['full_stats_begin']:
				owner['has-finishes-pre-full-stats'] = True
			else:
				owner['seasons_with_rosters'].append(season)

		######################################################
		# Get most-picked players for this owner

		query = f'SELECT player_id, drafted, fnf FROM owner_x_player_sums WHERE owner_id = {owner_id} ORDER BY drafted DESC, fnf ASC LIMIT 5'

		players = get_rows(query)

		for x in range(0, len(players)):

			player_id = players[x]['player_id']

			query = f'SELECT season FROM owner_x_player WHERE player_id = {player_id} AND owner_id = {owner_id} AND drafted = 1'

			rows = get_rows(query)

			seasons = ""

			for row in rows:

				seasons = seasons + str(row['season']) + ", "
			
			seasons = seasons[:-2]

			players[x]['desc'] = seasons

		owner['most_picked_players'] = players

		######################################################
		# Get all teams for this owner

		owner['teams'] = []

		for season in owner['seasons']:

			if season['season'] >= int(env['full_stats_begin']):

				team = get_team(owner_id, season['season'])

				owner['teams'].append(team)

		######################################################
		# Get pre-2004 finishes

		if owner['has-finishes-pre-full-stats']:

			query = f'SELECT season, place, points FROM owner_x_season WHERE season < {env["full_stats_begin"]} AND owner_id = {owner_id} ORDER BY season DESC'

			owner['finishes'] = get_rows(query)

			for x in range (0, len(owner['finishes'])):
				owner['finishes'][x]['place'] = make_ordinal(owner['finishes'][x]['place'])

		######################################################

		obj['owner'] = owner

		obj['dirs'][1] = owner_id

	if subject == 'owners':

		query = f'SELECT * FROM owner_stats WHERE owner_id != {TEST_OWNER_ID} ORDER BY nickname ASC'

		obj['owners'] = get_rows(query)

	if subject == 'players':

		season = item_id

		obj['season'] = season

		obj['heading'] = obj['heading'] + ' ' + str(season)

		obj['players'] = get_players(season)

		obj['dirs'][1] = season

	if subject == 'records':

		obj['records'] = True

	if subject == 'season':

		season = item_id

		is_current_season = False

		obj['heading'] = obj['heading'] + ' ' + str(season)

		if int(season) == env['current_season']:

			is_current_season = True

			obj['heading'] = str(season) + ' Standings'
			obj['last_updated'] = get_last_updated()
			obj['season_is_current'] = True

		obj['season'] = season
		obj['owner_rows'] = get_owner_rows(season)
		obj['owners'] = get_owners(season)
		obj['teams'] = get_teams(season)

		if int(season) >= env['full_stats_begin']:
			obj['show_full_stats'] = True

			if is_current_season:
				obj['leaderboards'] = get_leaderboards(season, True)
			else:
				obj['leaderboards'] = get_leaderboards(season, False)

		else:
			obj['show_leaderboards'] = False

		if is_valid_trade_season(int(season)):
			obj['show_trades'] = True
		else:
			obj['show_trades'] = False

		obj['dirs'][1] = season

	if subject == 'seasons_home':

		obj['seasons'] = []

		for x in range(env['season_last'], env['season_first'] -1, -1):

			obj['seasons'].append({"season": x})

			print(str(x))

	if subject == 'trades':

		season = item_id

		obj['season'] = season

		obj['heading'] = obj['heading'] + ' ' + str(season)

		obj['trades'] = get_trades(season)

		obj['make_a_trade_link'] = env['make_a_trade_link']

		obj['show_trade_button'] = not env['offseason']

		obj['dirs'][1] = season

	obj['page_generated'] = datetime.datetime.now()

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

	p = env["local_home"]

	dir_path = ""

	for dir in obj['dirs']:
		print(dir)

		dir_path = dir_path + dir + "/"

		p = p + "/" + dir

		if not os.path.exists(f'{env["local_home"]}/{dir_path}'):

			print("making directory " + p)

			os.makedirs(f'{env["local_home"]}/{dir_path}')

	if env["create_local_files"]:

		local_path = f'{env["local_home"]}/{dir_path}index.html'

		print(local_path)

		write_local_file(local_path, page)

	if PUSH_TO_S3:

		push_page_to_s3(dir_path + "index.html", page)

	else:
		print('push_to_s3 is false.')

def get_best_finish_detail(owner_id, best_finish):

	best_finish_detail = ""

	query = f'SELECT season FROM owner_x_season WHERE place = {best_finish} AND owner_id = {owner_id} ORDER BY season ASC'

	rows = get_rows(query)

	for row in rows:

		best_finish_detail += str(row['season']) + ", "

	best_finish_detail = best_finish_detail[:-2]

	return best_finish_detail

def get_desc(column, rank):

	query = f'SELECT COUNT({column}) AS c FROM owner_stats WHERE {column} = {rank}'

	row = get_row(query)

	ordinal_str = make_ordinal(rank)

	owner_count = row['c']

	if owner_count == 1:
		return ordinal_str
	else:
		s = f'Tied for {ordinal_str} with {owner_count - 1} other owner'

		if owner_count > 3:

			s = s + "s"

		return s

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
		table = 'owner_x_season_detail'

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

	query = f'SELECT * FROM owner_x_season_detail WHERE season = {season} AND owner_id != {TEST_OWNER_ID} ORDER BY place, nickname ASC'

	rows = get_rows(query)

	for row in rows:
		row['place'] = make_ordinal(row['place'])

	return rows

def get_owners(season):

	query = f'SELECT owner_id, nickname, season FROM owner_x_season_detail WHERE season = {season} ORDER BY nickname ASC'

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

def get_team(owner_id, season):

	query = f'SELECT bank, nickname, owner_id, place, points, recent, salary, season, team_name, yesterday FROM owner_x_season_detail WHERE owner_id = {owner_id} AND season = {season}'

	team = get_row(query)

	team['place'] = make_ordinal(team['place'])

	team['active_players'] = get_roster(owner_id, season, "active")

	benched_players = get_roster(owner_id, season, "benched")

	if (len(benched_players)) > 0:
		team['has_benched_players'] = True

		team['benched_players'] = benched_players
	
	return team

def get_teams(season):

	query = f'SELECT owner_id FROM owner_x_season_detail WHERE season = {season} AND owner_id != {TEST_OWNER_ID} ORDER BY nickname ASC'

	owners = get_rows(query)

	teams = []

	for owner in owners:

		owner_id = owner['owner_id']

		teams.append(get_team(owner_id, season))

	return teams

def get_trades(season): 

	query = f'SELECT * FROM trades_detail WHERE season = {season} AND owner_id != {TEST_OWNER_ID} ORDER BY stamp, day DESC'

	trades = get_rows(query)

	for x in range(0, len(trades)):

		new_date = datetime.datetime(trades[x]['season'], 1, 1) + datetime.timedelta(trades[x]['day'] - 1)

		trades[x]['date'] = str(new_date)[5:10]

	return trades

def is_valid_trade_season(season):

	if season > 2005:
		if season != 2020 and season != 2019:
			return True

	return False

def make_ordinal(n):
	n = int(n)
	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	return str(n) + suffix

def parse_command_line_args():

	global PUSH_TO_S3

	print(sys.argv)

	global settings, sections, valid_args

	if len(sys.argv) == 1:
		show_error_message()

	keyword = sys.argv[1] # --owner

	kw = keyword[2:] # owner

	if kw in valid_args:

		print(f'the keyword is valid: {kw}')

		if '--push_to_s3' in sys.argv:

			PUSH_TO_S3 = True

			print("we are pushing to s3.")

		else:

			print("we are not pushing to s3.")

		return kw
	else:
		show_error_message()

def push_page_to_s3(path, page):

	print('pushing page to s3...')

	session = boto3.Session(
		aws_access_key_id=env['accessKeyId'],
		aws_secret_access_key=env['secretAccessKey']
	)

	s3 = session.resource('s3')

	s3_bucket = env["s3_bucket"]

	my_bucket = s3.Bucket(s3_bucket)

	my_bucket.put_object(Key=path, Body=page, ContentType='text/html', ACL='public-read')

def show_error_message():

	print('you need to provide a valid keyword.')
	print('the valid keywords are:')

	for a in valid_args:
		print("--" + a)
	
	exit()

def write_local_file(path, page):

	print("writing local file...")
	f = open(path, "w")

	f.write(page)

	f.close()

##############################################################
# main function

kw = parse_command_line_args()

evaluate_kw(kw)
