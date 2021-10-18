#!/usr/bin/python3

import datetime

###################################################

from includes.dbconn import get_row, get_rows

from includes.write_files import write_to_local_disk
from includes.write_files import write_to_s3

###################################################

def generate_season_nav_page(connection, s3, env):

	content = "<p>Seasons</p>"

	# content["title"] = f'Baseball seasons'

	with open("html/templates/base.html") as file:
		base = file.read()

	query = 'SELECT season FROM seasons ORDER BY season ASC'

	print(query)

	rows = get_rows(query)

	for row in rows:

		content += f'<p><a href = "/seasons/{row["season"]}">{row["season"]}</a></p>\n'

	page = base.replace("{main}", content)

	page = page.replace("{title}", "Baseball seasons")

	page = page.replace("{page_generated}", str(datetime.datetime.now()))

	if env["create_local_files"]:
		write_to_local_disk(page, "season_nav", 0)

	if env["push_to_s3"]:
		write_to_s3(page, "season_nav", 0, s3)

def get_small_stats_table(column, person_type, picked_only, season):

	html = ""

	if person_type == "player":
		with open("html/templates/player_row_tiny.html") as file:
			template = file.read()
		query = f'SELECT fnf, player_id, {column} FROM player_x_season_detail WHERE season = {season}'

		if picked_only:
			query += ' AND picked > 0'

		query += f' ORDER BY {column} DESC'
	else:
		with open("html/templates/owner_row_tiny.html") as file:
			template = file.read()
		query = f'SELECT nickname, owner_id, {column} FROM ownersXseasons_detail WHERE season = {season} ORDER BY {column} DESC, nickname ASC'

	query += ' LIMIT 5'

	print(query)

	rows = get_rows(query)

	i = 0

	for row in rows:
		i += 1

		this_person = template

		if row[column] < 0:
			cat_val = "N/A"
		else:
			cat_val = row[column]

		vals = {
			"rank": i,
			"cat_val": cat_val
		}

		if person_type == "player":
			vals["fnf"] = row["fnf"]
			vals["player_id"] = row["player_id"]
		else:
			vals["nickname"] = row["nickname"]
			vals["owner_id"] = row["owner_id"]

		for val in vals:
			this_person = this_person.replace("{" + val + "}", str(vals[val]))

		html += this_person + "\n"

	return html

def make_ordinal(n):
	n = int(n)
	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
	if 11 <= (n % 100) <= 13:
		suffix = 'th'
	return str(n) + suffix

# def get_home_page_content(connection, season, archive_home_page):

	content = {
		"season": season,
		"page_generated": datetime.datetime.now()
	}

	###################################################
	# Get main list of owners
	content["owner_rows_summary"] = get_owner_rows_summary(connection, season)

	###################################################
	# owner drop-down
	content["owner_dropdown"] = get_owner_dropdown(connection, season)

	###################################################
	# owner detailed teams
	content["teams"] = get_owner_detailed_teams(connection, season)

	###################################################
	content["most_productive_players-picked"] = get_small_stats_table("points", "player", True, season)
	content["most_valuable_players-picked"] = get_small_stats_table("value", "player", True, season)
	content["most_popular_players"] = get_small_stats_table("picked", "player", True, season)
	content["most_productive_players-all"] = get_small_stats_table("points", "player", False, season)
	content["most_valuable_players-all"] = get_small_stats_table("value", "player", False, season)

	if not archive_home_page:
		content["yesterday_top_owners"] = get_small_stats_table("yesterday", "owner", True, season)
		content["hot_owners"] = get_small_stats_table("recent", "owner", True, season)
		content["yesterday_top_players-picked"] = get_small_stats_table("yesterday", "player", True, season)
		content["hot_players-picked"] = get_small_stats_table("recent", "player", True, season)
		content["last_updated"] = get_last_updated(connection, season)

	###################################################

	content["title"] = f'Baseball {season}: Standings'

	with open("html/templates/base.html") as file:
		base = file.read()

	if archive_home_page:
		home_template = "html/templates/home_archive.html"
	else:
		home_template = "html/templates/home.html"

	with open(home_template) as file:
		home = file.read()

	home = base.replace("{main}", home)

	for chunk in content:
		home = home.replace("{" + chunk + "}", str(content[chunk]))

	return home

def get_season_home_page_content(connection, season, season_is_current):

	content = {
		"season": season,
		"page_generated": datetime.datetime.now()
	}

	###################################################
	# Get main list of owners
	content["owner_rows_summary"] = get_owner_rows_summary(connection, season)

	###################################################
	# owner drop-down
	content["owner_dropdown"] = get_owner_dropdown(connection, season)

	###################################################
	# owner detailed teams
	content["teams"] = get_owner_detailed_teams(connection, season, season_is_current)

	###################################################
	content["most_productive_players-picked"] = get_small_stats_table("points", "player", True, season)
	content["most_valuable_players-picked"] = get_small_stats_table("value", "player", True, season)
	content["most_popular_players"] = get_small_stats_table("picked", "player", True, season)
	content["most_productive_players-all"] = get_small_stats_table("points", "player", False, season)
	content["most_valuable_players-all"] = get_small_stats_table("value", "player", False, season)

	if season_is_current:
		content["yesterday_top_owners"] = get_small_stats_table("yesterday", "owner", True, season)
		content["hot_owners"] = get_small_stats_table("recent", "owner", True, season)
		content["yesterday_top_players-picked"] = get_small_stats_table("yesterday", "player", True, season)
		content["hot_players-picked"] = get_small_stats_table("recent", "player", True, season)
		content["last_updated"] = get_last_updated(connection, season)
		content["make_a_trade"] = "inline"
	else:
		content["make_a_trade"] = "none"

	###################################################

	content["title"] = f'Baseball {season}: Standings'

	with open("html/templates/base.html") as file:
		base = file.read()

	season_page = get_season_template(season)

	season_page = base.replace("{main}", season_page)

	for chunk in content:
		season_page = season_page.replace("{" + chunk + "}", str(content[chunk]))

	return season_page

def get_last_updated(connection, season):

	query = "SELECT update_desc FROM updates ORDER BY time_of_update DESC LIMIT 1"

	print(query)

	row = get_row(query)

	return row["update_desc"]

def get_owner_detailed_team(connection, season, owner_id):

	query = f'SELECT * FROM owner_x_roster_detail WHERE owner_id = {owner_id} AND season = {season}'
	query += " ORDER BY o ASC, salary DESC"

	print(query)

	players = get_rows(query)

	return players

def get_owner_template(season_is_current):

	if season_is_current:
		filename = "owner_team_detail_current.html"
	else:
		filename = "owner_team_detail_past.html"

	with open("html/templates/" + filename) as file:
		template = file.read()

	return template

def get_roster_html(roster, season_is_current):

	if season_is_current:
		filename = "player_in_team_current.html"
	else:
		filename = "player_in_team_past.html"

	with open("html/templates/" + filename) as file:
		player_template = file.read()

	active_html = ""

	bench_html = ""

	for p in roster:

		for f in p:
			if p[f] == -1:
				p[f] = "N/A"

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

	return active_html + "\n" + bench_html

def get_season_template(season):

	if season < 2004:
		filename = "season_old.html"
	else:
		filename = "season.html"

	with open("html/templates/" + filename) as file:
		season_page = file.read()

	return season_page

def get_owner_detailed_teams(connection, season, season_is_current):

	teams = ""

	query = f'SELECT * FROM ownersXseasons_detail WHERE season = {season} ORDER BY place ASC'

	print(query)

	rows = get_rows(query)

	template = get_owner_template(season_is_current)

	for row in rows:

		owner_id = row["owner_id"]

		this_team = template

		row["season"] = season

		if row["team_name"]:
			row["team_name"] = " - " + row["team_name"]

		if row["bank"]:
			row["bank"] = "bank: $" + str(row["bank"])
		else:
			row["bank"] = ""

		row["link"] = str(season) + "_" + str(owner_id)

		row["place"] = make_ordinal(row["place"])

		int_fields = ["points", "recent", "yesterday"]

		fields = int_fields + ["bank", "link", "nickname", "salary", "place", "season", "team_name"]

		for field in fields:

			if field in int_fields and int(row[field]) < 0:
				row[field] = "N/A"

			this_team = this_team.replace("{" + field + "}", str(row[field]))

		roster = get_owner_detailed_team(connection, season, owner_id)

		roster_html = get_roster_html(roster, season_is_current)

		this_team = this_team.replace("{roster}", roster_html)

		teams += this_team

	return teams

def get_owner_dropdown(connection, season):

	owner_dropdown = ""

	template = "<a class='dropdown-item' href='#{link}'>{nickname}</a>"

	query = f'SELECT * FROM ownersXseasons_detail WHERE season = {season} ORDER BY nickname ASC'

	print(query)

	rows = get_rows(query)

	for row in rows:

		this_row = template

		link = str(season) + "_" + str(row["owner_id"])

		this_row = this_row.replace("{link}", link)
		this_row = this_row.replace("{nickname}", row["nickname"])

		owner_dropdown += this_row + "\n"

	return owner_dropdown

def get_owner_rows_summary(connection, season):

	owner_rows_summary = ""

	with open("html/templates/owner_row_home_page.html") as file:
		template = file.read()

	query = f'SELECT * FROM ownersXseasons_detail WHERE season={season} ORDER BY place ASC, nickname ASC'

	print(query)

	rows = get_rows(query)

	# now generate owner rows

	for row in rows:

		this_row = template

		owner_id = row["owner_id"]

		row["link"] = str(season) + "_" + str(owner_id)

		if row["head_shot"]:
			url = row["head_shot"]
			row["head_shot"] = f'<img src="{url}">'

		fields = ["head_shot", "link", "nickname", "place", "points", "team_name"]

		for field in fields:
			this_row = this_row.replace("{" + field + "}", str(row[field]))

		owner_rows_summary += this_row

	return owner_rows_summary

# def generate_home_page(connection, season, s3, env):

# 	content = get_home_page_content(connection, season, env["archive_home_page"])

# 	if env["create_local_files"]:
# 		write_to_local_disk(content, "home", season)

# 	if env["push_to_s3"]:
# 		write_to_s3(content, "home", season, s3)

def generate_season_home_page(connection, season, season_is_current, s3, env):

	content = get_season_home_page_content(connection, season, season_is_current)

	if env["create_local_files"]:
		write_to_local_disk(content, "season", season)

	if env["push_to_s3"]:
		write_to_s3(content, "season", season, s3)
