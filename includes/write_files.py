
import datetime

local_home = "html/output/"

remote_home = ""

def write_to_local_disk(content, page, season):

	if page == "home":
		local_path = local_home
	else:
		local_path = local_home + f'seasons/{season}/{page}/'

	local_path += "index.html"

	f = open(local_path, "w")
	f.write(content)
	f.close()

def write_to_s3(content, page, season, s3):

	if page == "home":
		remote_path = remote_home
	else:
		remote_path = remote_home + f'seasons/{season}/{page}/'

	x = datetime.datetime.now()

	filename_base = x.strftime("%Y_%m_%d_%H_%M_%S")

	filename = filename_base + ".html"

	live_path = remote_path + "index.html"

	backup_path = "backup/" + remote_path + filename

	s3.Bucket('baseball-dev.tomgsmith.com').put_object(Key=live_path, Body=content, ContentType='text/html', ACL='public-read')
	s3.Bucket('baseball-dev.tomgsmith.com').put_object(Key=backup_path, Body=content, ContentType='text/html', ACL='public-read')