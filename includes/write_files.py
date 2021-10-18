
import datetime
import json
import os.path

#######################################

local_home = "/Users/tomsmith/projects/baseball_local_static/public/"

remote_home = ""

#######################################

with open('.env.json') as json_file:
	env = json.load(json_file)

def write_to_local_disk(content, page, season, obj_id=0):

	if page == "home":
		local_path = local_home

	elif page == "player":

		if not os.path.isdir(local_home + "seasons"):
			os.mkdir(local_home + "seasons")

		local_path = local_home + f'players/{obj_id}/'

	elif page == "season":

		if not os.path.isdir(local_home + "seasons"):
			os.mkdir(local_home + "seasons")

		local_path = local_home + f'seasons/{season}/'

	elif page == "season_nav":

		if not os.path.isdir(local_home + "seasons"):
			os.mkdir(local_home + "seasons")

		local_path = local_home + f'seasons/'


	# else:
	# 	local_path = local_home + f'seasons/{season}/{page}/'

	# create the local path if it does not exist

	if not os.path.isdir(local_path):
		os.mkdir(local_path)

	local_path += "index.html"

	f = open(local_path, "w")
	f.write(content)
	f.close()

def write_to_s3(content, page, season, s3, obj_id=0):

	s3_bucket = env["s3_bucket"]

	if page == "home":
		remote_path = remote_home
	elif page == "player":
		remote_path = remote_home + f'players/{obj_id}/'
	elif page == "season":
		remote_path = remote_home + f'seasons/{obj_id}/'
	# else:
	# 	remote_path = remote_home + f'seasons/{season}/{page}/'

	live_path = remote_path + "index.html"

	s3.Bucket(s3_bucket).put_object(Key=live_path, Body=content, ContentType='text/html', ACL='public-read')

	if page == "home" or page == "players":
		x = datetime.datetime.now()

		filename_base = x.strftime("%Y_%m_%d_%H_%M_%S")

		filename = filename_base + ".html"

		backup_path = "backup/" + remote_path + filename

		s3.Bucket(s3_bucket).put_object(Key=backup_path, Body=content, ContentType='text/html', ACL='public-read')
