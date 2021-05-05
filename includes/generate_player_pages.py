#!/usr/bin/python3

import datetime

###################################################

from includes.dbconn import get_row, get_rows

from includes.write_files import write_to_local_disk
from includes.write_files import write_to_s3

###################################################

def get_all_time_rows(connection, player_id):

	html_rows = ""

	query = f'SELECT drafted, points, pos, salary, season, team, value FROM playersXseasons WHERE player_id={player_id} ORDER BY season DESC'

	print(query)

	rows = get_rows(query)

	for row in rows:

		row["drafted_by"] = ""

		if row["drafted"] > 0:
			owners = get_owners(player_id, row["season"])

			for owner in owners:
				row["drafted_by"] += owner["nickname"] + ", "

			row["drafted_by"] = row["drafted_by"].rstrip()
			row["drafted_by"] = row["drafted_by"].rstrip(",")

		##########################

		html_row = "<tr><td align='center'>{season}</td><td align='center'>{pos}</td><td align='center'>{team}</td><td align='right'>${salary}</td><td align='right'>{points}</td><td align='center'>{value}</td><td align='center'>{drafted}</td><td>{drafted_by}</td></tr>"

		for val in row:

			html_row = html_row.replace("{" + val + "}", str(row[val]))

		html_rows += html_row + "\n"

	return html_rows

def get_most_drafted_by(connection, player_id):

	owner_string = ""

	query = f'SELECT drafted, owner_id, nickname FROM ownersXplayers_view WHERE player_id={player_id} ORDER BY drafted DESC, nickname LIMIT 5'

	print(query)

	rows = get_rows(query)

	for row in rows:

		years = get_owner_years(row["owner_id"], player_id)

		##############

		this_owner_string = row["nickname"] + " (" + str(len(years)) + " times): "

		for year in years:
			this_owner_string += str(year) + ", "

		this_owner_string = this_owner_string.rstrip()
		this_owner_string = this_owner_string.rstrip(",")

		owner_string += this_owner_string + "<br>\n"

	return owner_string

def get_most_recent_appearance(connection, player_id):

	query = f'SELECT season FROM players_current WHERE player_id={player_id}'

	player = get_row(query)

	if player["season"]:
		return player["season"]

	query = f'SELECT MAX(season) AS season FROM players_all_time WHERE player_id={player_id}'

	player = get_row(query)

	return player["season"]

def get_owner_years(owner_id, player_id):

	query = f'SELECT season FROM ownersXrosters WHERE player_id={player_id} AND owner_id={owner_id} AND drafted = 1 ORDER BY season ASC'

	print(query)

	years = []

	rows = get_rows(query)

	for row in rows:

		years.append(row["season"]) 

	return years

def get_owners(player_id, season):

	query = f'SELECT nickname FROM oXr_AT_view WHERE player_id={player_id} AND drafted=1 AND season={season} ORDER BY nickname'

	print(query)

	rows = get_rows(query)

	return rows

def get_rookie_year(player_id, season):

	query = f'SELECT rookie_year FROM players_rookie_year WHERE player_id={player_id}'

	print(query)

	row = get_row(query)

	if row:
		return row["rookie_year"]

	query = f'SELECT year_added FROM players WHERE player_id={player_id}'

	print(query)

	row = get_row(query)

	return row["year_added"]

	print("could not find a rookie year for this player.")

	exit()

def get_worst_year(player_id):

	obj = {}

	query = f'SELECT MIN(points) AS points, season FROM players_all_time WHERE player_id={player_id} AND season != 2020 GROUP BY player_id'

	print(query)

	row = get_row(query)

	if row:
		obj["points"] = row["points"]
		obj["season"] = row["season"]

		return obj

	query = f'SELECT MIN(points) AS points, season FROM players_all_time WHERE player_id={player_id} GROUP BY player_id'

	print(query)

	row = get_row(query)

	if row:
		obj["points"] = row["points"]
		obj["season"] = row["season"]

		return obj

	obj["points"] = "N/A"
	obj["season"] = "-"

	return obj

def get_player_content(connection, season, s3, push_to_s3, create_local_files, player_id):

	query = f'SELECT * FROM players_view WHERE player_id={player_id}'

	print(query)

	player = get_row(query)

	if not player:

		rookie_year = get_rookie_year(player_id, season)

		print("the rookie year is: " + str(rookie_year))

		query = f'SELECT fnf FROM players WHERE player_id={player_id}'

		print(query)

		row = get_row(query)

		player = {
			"fnf": row["fnf"],
			"most_points": "N/A",
			"most_points_year": "-",
			"rookie_year": rookie_year
		}

	worst_year = get_worst_year(player_id)

	player["least_points"] = worst_year["points"]

	player["least_points_year"] = worst_year["season"]

	player["all_time_rows"] = get_all_time_rows(connection, player_id)

	player["most_often_drafted_by"] = get_most_drafted_by(connection, player_id)

	player["most_recent_appearance"] = get_most_recent_appearance(connection, player_id)

	##################

	with open("html/templates/base.html") as file:
		html = file.read()
		html = html.replace("{page_generated}", str(datetime.datetime.now()))
		html = html.replace("{title}", "Baseball: " + player["fnf"])

	with open("html/templates/player.html") as file:
		player_html = file.read()
		html = html.replace("{main}", player_html)

	for val in player:
		html = html.replace("{" + val + "}", str(player[val]))

	return html

def generate_player_page(connection, season, s3, push_to_s3, create_local_files, player_id):

	content = get_player_content(connection, season, s3, push_to_s3, create_local_files, player_id)

	if create_local_files:
		write_to_local_disk(content, "player", season, player_id)

	if push_to_s3:
		write_to_s3(content, "player", season, s3, player_id)

def generate_player_pages(connection, season, s3, push_to_s3, create_local_files):

	query = f'SELECT * FROM players_current_view WHERE season={season} ORDER BY lnf'

	# query = f'SELECT player_id FROM players_current_view WHERE season={season} AND player_id=5016 ORDER BY lnf'

	# if player_id == 5016:

	# 	exit()

	print(query)

	rows = get_rows(query)

	for player in rows:

		generate_player_page(connection, season, s3, push_to_s3, create_local_files, player["player_id"])

	exit()
