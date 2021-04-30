#!/usr/bin/python3

import datetime

###################################################

from includes.dbconn import get_row, get_rows

from includes.write_files import write_to_local_disk
from includes.write_files import write_to_s3

###################################################

def get_trades_content(connection, season):

	content = {
		"season": season,
		"page_generated": datetime.datetime.now()
	}

	query = f'SELECT * FROM trades_view WHERE season={season} ORDER BY stamp DESC'

	print(query)

	rows = get_rows(query)

	with open("html/templates/trade_row.html") as file:
		template = file.read()

	vals = ["added_player_fnf", "date", "dropped_player_fnf", "nickname", "pos"]

	table_rows = ""

	for row in rows:

		trade_row = template

		added_player_id = row["added_player_id"]
		dropped_player_id = row["dropped_player_id"]

		query = f'SELECT * FROM players_current_view WHERE player_id = {added_player_id}'

		r = get_row(query)

		row["added_player_fnf"] = r["fnf"]

		row["pos"] = r["pos"]

		query = f'SELECT * FROM players WHERE player_id = {dropped_player_id}'

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

	###################################################

	template = template.replace("{trades}", table_rows)

	with open("html/templates/base.html") as file:
		base = file.read()

	base = base.replace("{title}", "Trades")

	base = base.replace("{page_generated}", str(content["page_generated"]))

	base = base.replace("{main}", template)

	base = base.replace("{season}", str(season))

	return base

def generate_trades_page(connection, season, s3, push_to_s3, create_local_files):

	content = get_trades_content(connection, season)

	if create_local_files:
		write_to_local_disk(content, "trades", season)

	if push_to_s3:
		write_to_s3(content, "trades", season, s3)
