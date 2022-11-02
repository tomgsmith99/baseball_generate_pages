#!/usr/bin/python3

import datetime

###################################################

from includes.dbconn import get_row, get_rows

from includes.write_files import write_to_local_disk
from includes.write_files import write_to_s3

###################################################

def get_players_page_content(connection, season):

	content = {
		"season": season,
		"page_generated": datetime.datetime.now()
	}

	content["title"] = f'Baseball {season}: Players'

	query = f'SELECT * FROM player_x_season WHERE season={season} ORDER BY points DESC, lnf ASC'

	html = ""

	with open("html/templates/player_in_player_table.html") as file:
		template = file.read()

	rows = get_rows(query)

	for row in rows:

		if row["value"] == -1:
			row["value"] = "0"

		if row["pos"] == "C":
			row["pos"] = "C2"

		row["salary"] = "$" + str(row["salary"])

		player_id = row["player_id"]

		fnf = row["fnf"]

		row["name_with_link"] = f'<a href="/players/{player_id}" target="_blank">{fnf}</a>'

		this_player = template

		vals = ["points", "name_with_link", "pos", "salary", "team", "value", "drafted", "picked"]

		for val in vals:

			this_player = this_player.replace("{" + val + "}", str(row[val]))

		html += this_player + "\n"

	content["player_rows"] = html

	with open("html/templates/base.html") as file:
		base = file.read()

	with open("html/templates/players.html") as file:
		players_page = file.read()

	players_page = base.replace("{main}", players_page)

	for chunk in content:
		players_page = players_page.replace("{" + chunk + "}", str(content[chunk]))

	return players_page

def generate_players_page(connection, season, s3, push_to_s3, create_local_files):

	query = f'SELECT * FROM player_x_season_detail WHERE season={season} ORDER BY lnf'

	print(query)

	rows = get_rows(query)

	with open("html/templates/trade_row.html") as file:
		template = file.read()

	vals = ["added_player_fnf", "date", "dropped_player_fnf", "nickname", "pos"]

	table_rows = ""

	for row in rows:

		print(row)

	content = get_players_page_content(connection, season)

	if create_local_files:
		write_to_local_disk(content, "players", season)

	if push_to_s3:
		write_to_s3(content, "players", season, s3)
