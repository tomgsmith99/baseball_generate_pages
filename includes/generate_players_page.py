import datetime

import includes.dbconn
from includes.dbconn import get_row, get_rows

import includes.write_files
from includes.write_files import write_to_local_disk
from includes.write_files import write_to_s3

###################################################

def get_players_page_content(connection, season):

	content = {
		"season": season,
		"page_generated": datetime.datetime.now()
	}

	content["title"] = "Players"

	query = f'SELECT * FROM players_current_view WHERE season={season} ORDER BY points DESC, lnf ASC'

	html = ""

	with open("html/templates/player_in_player_table.html") as file:
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

	with open("html/templates/base.html") as file:
		base = file.read()

	with open("html/templates/players.html") as file:
		players_page = file.read()

	players_page = base.replace("{main}", players_page)

	for chunk in content:
		players_page = players_page.replace("{" + chunk + "}", str(content[chunk]))

	return players_page

def generate_players_page(connection, season, s3):

	content = get_players_page_content(connection, season)

	write_to_local_disk(content, "players", season)

	write_to_s3(content, "players", season, s3)

###################################################

# f = open(base_path + "html/output/players.html", "w")
# f.write(players_page)
# f.close()

###################################################

# s3.Bucket('baseball.tomgsmith.com').put_object(Key='seasons/' + str(season) + '/players/index.html', Body=players_page, ContentType='text/html', ACL='public-read')
# s3.Bucket('baseball.tomgsmith.com').put_object(Key='backup/players/' + filename, Body=players_page, ContentType='text/html', ACL='public-read')

# def get_small_stats_table(column, person_type, picked_only=True):

# 	html = ""

# 	if person_type == "player":
# 		with open("html/templates/player_row_tiny.html") as file:
# 			template = file.read()
# 		query = f'SELECT fnf, player_id, {column} FROM players_current_view'

# 		if picked_only:
# 			query += ' WHERE picked > 0'

# 		query += f' ORDER BY {column} DESC'
# 	else:
# 		with open("html/templates/owner_row_tiny.html") as file:
# 			template = file.read()
# 		query = f'SELECT nickname, owner_id, {column} FROM ownersXseasons_current_view ORDER BY {column} DESC, nickname ASC'

# 	query += ' LIMIT 5'

# 	print(query)

# 	rows = get_rows(query)

# 	i = 0

# 	for row in rows:
# 		i += 1

# 		this_person = template

# 		if row[column] < 0:
# 			cat_val = "N/A"
# 		else:
# 			cat_val = row[column]

# 		vals = {
# 			"rank": i,
# 			"cat_val": cat_val
# 		}

# 		if person_type == "player":
# 			vals["fnf"] = row["fnf"]
# 			vals["player_id"] = row["player_id"]
# 		else:
# 			vals["nickname"] = row["nickname"]
# 			vals["owner_id"] = row["owner_id"]

# 		for val in vals:
# 			this_person = this_person.replace("{" + val + "}", str(vals[val]))

# 		html += this_person + "\n"

# 	return html

# def make_ordinal(n):
# 	n = int(n)
# 	suffix = ['th', 'st', 'nd', 'rd', 'th'][min(n % 10, 4)]
# 	if 11 <= (n % 100) <= 13:
# 		suffix = 'th'
# 	return str(n) + suffix

# def get_home_page_content(connection, season):

# 	content = {
# 		"season": season,
# 		"page_generated": datetime.datetime.now()
# 	}

# 	###################################################
# 	# Get main list of owners
# 	content["owner_rows_summary"] = get_owner_rows_summary(connection, season)

# 	###################################################
# 	# owner drop-down
# 	content["owner_dropdown"] = get_owner_dropdown(connection, season)

# 	###################################################
# 	# owner detailed teams
# 	content["teams"] = get_owner_detailed_teams(connection, season)

# 	###################################################
# 	content["most_productive_players-picked"] = get_small_stats_table("points", "player", True)
# 	content["most_valuable_players-picked"] = get_small_stats_table("value", "player", True)
# 	content["most_popular_players"] = get_small_stats_table("picked", "player", True)
# 	content["most_productive_players-all"] = get_small_stats_table("points", "player", False)
# 	content["most_valuable_players-all"] = get_small_stats_table("value", "player", False)
# 	content["yesterday_top_owners"] = get_small_stats_table("yesterday", "owner")
# 	content["hot_owners"] = get_small_stats_table("recent", "owner")
# 	content["yesterday_top_players-picked"] = get_small_stats_table("yesterday", "player", True)
# 	content["hot_players-picked"] = get_small_stats_table("recent", "player", True)

# 	content["last_updated"] = get_last_updated(connection, season)

# 	###################################################

# 	content["title"] = "Standings"

# 	with open("html/templates/base.html") as file:
# 		base = file.read()

# 	with open("html/templates/home.html") as file:
# 		home = file.read()

# 	home = base.replace("{main}", home)

# 	for chunk in content:
# 		home = home.replace("{" + chunk + "}", str(content[chunk]))

# 	return home

# def get_last_updated(connection, season):

# 	query = "SELECT update_desc FROM updates ORDER BY time_of_update DESC LIMIT 1"

# 	print(query)

# 	row = get_row(query)

# 	return row["update_desc"]

# def get_owner_detailed_teams(connection, season):

# 	teams = ""

# 	with open("html/templates/owner_team_detail.html") as file:
# 		template = file.read()

# 	query = "SELECT * FROM ownersXseasons_current_view ORDER BY place ASC"

# 	print(query)

# 	rows = get_rows(query)

# 	for row in rows:

# 		owner_id = row["owner_id"]

# 		this_team = template

# 		row["season"] = season

# 		row["link"] = str(season) + "_" + str(row["owner_id"])

# 		row["place"] = make_ordinal(row["place"])

# 		int_fields = ["points", "recent", "yesterday"]

# 		fields = int_fields + ["bank", "link", "nickname", "salary", "place", "season", "team_name"]

# 		for field in fields:

# 			if field in int_fields and int(row[field]) < 0:
# 				row[field] = "N/A"

# 			this_team = this_team.replace("{" + field + "}", str(row[field]))

# 		query = f'SELECT * FROM oxrcXpos WHERE owner_id={row["owner_id"]}'
# 		query += " ORDER BY o ASC, salary DESC"

# 		print(query)

# 		players = get_rows(query)

# 		with open("html/templates/player_in_team.html") as file:
# 			player_template = file.read()

# 		active_html = ""

# 		bench_html = ""

# 		for p in players:

# 			if p["recent"] == -1:
# 				p["recent"] = "N/A"

# 			if p["yesterday"] == -1:
# 				p["yesterday"] = "N/A"

# 			if p["value"] == -1:
# 				p["value"] = "N/A"

# 			this_player = player_template

# 			fields = ["fnf", "pos", "player_id", "points", "recent", "salary", "team", "value", "yesterday"]

# 			for field in fields:
# 				this_player = this_player.replace("{" + field + "}", str(p[field]))

# 			if p["acquired"] == 1:
# 				this_player = this_player.replace("{font-style}", "italic")
# 			else:
# 				this_player = this_player.replace("{font-style}", "normal")

# 			if p["benched"] == 1:
# 				bench_html += this_player
# 			else:
# 				active_html += this_player

# 		if bench_html != "":
# 			bench_html = '<tr><td colspan="10" style="text-align: center;">Benched players</td></tr>\n' + bench_html

# 		this_team = this_team.replace("{active_html}", active_html)
# 		this_team = this_team.replace("{bench_html}", bench_html)

# 		teams += this_team

# 	return teams

# def get_owner_dropdown(connection, season):

# 	owner_dropdown = ""

# 	template = "<a class='dropdown-item' href='#{link}'>{nickname}</a>"

# 	query = "SELECT * FROM ownersXseasons_current_view ORDER BY nickname ASC"

# 	print(query)

# 	rows = get_rows(query)

# 	for row in rows:

# 		this_row = template

# 		link = str(season) + "_" + str(row["owner_id"])

# 		this_row = this_row.replace("{link}", link)
# 		this_row = this_row.replace("{nickname}", row["nickname"])

# 		owner_dropdown += this_row + "\n"

# 	return owner_dropdown

# def get_owner_rows_summary(connection, season):

# 	owner_rows_summary = ""

# 	with open("html/templates/owner_row_home_page.html") as file:
# 		template = file.read()

# 	query = f'SELECT * FROM ownersXseasons_current_view WHERE season={season} ORDER BY place ASC, nickname ASC'

# 	print(query)

# 	rows = get_rows(query)

# 	# now generate owner rows

# 	for row in rows:

# 		this_row = template

# 		owner_id = row["owner_id"]

# 		row["link"] = str(season) + "_" + str(row["owner_id"])

# 		if row["head_shot"]:
# 			url = row["head_shot"]
# 			row["head_shot"] = f'<img src="{url}">'

# 		fields = ["head_shot", "link", "nickname", "place", "points", "team_name"]

# 		for field in fields:
# 			this_row = this_row.replace("{" + field + "}", str(row[field]))

# 		owner_rows_summary += this_row

# 	return owner_rows_summary

# def write_to_local(content, page):

# 	paths = {
# 		"home": "html/output/index.html"
# 	}

# 	f = open(paths[page], "w")
# 	f.write(content)
# 	f.close()

# def write_to_s3(content, page, s3):

# 	keys = {
# 		"home": "index.html"
# 	}

# 	x = datetime.datetime.now()

# 	filename_base = x.strftime("%Y_%m_%d_%H_%M_%S")

# 	filename = filename_base + ".html"

# 	s3.Bucket('baseball.tomgsmith.com').put_object(Key=keys[page], Body=content, ContentType='text/html', ACL='public-read')
# 	s3.Bucket('baseball.tomgsmith.com').put_object(Key='backup/' + filename, Body=content, ContentType='text/html', ACL='public-read')

# def generate_home_page(connection, season, s3):

# 	content = get_home_page_content(connection, season)

# 	write_to_local(content, "home")

# 	# write_to_s3(content, "home", s3)
