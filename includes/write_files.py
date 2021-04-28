
import datetime

def write_to_local_disk(content, page, season):

	paths = {
		"home": "html/output/index.html",
		"players": f'html/output/seasons/{season}/players/index.html'
	}

	f = open(paths[page], "w")
	f.write(content)
	f.close()

def write_to_s3(content, page, season, s3):
	keys = {
		"home": "index.html",
		"players": f'seasons/{season}/players/index.html'
	}

	x = datetime.datetime.now()

	filename_base = x.strftime("%Y_%m_%d_%H_%M_%S")

	filename = filename_base + ".html"

	s3.Bucket('baseball-dev.tomgsmith.com').put_object(Key=keys[page], Body=content, ContentType='text/html', ACL='public-read')
	s3.Bucket('baseball-dev.tomgsmith.com').put_object(Key='backup/' + filename, Body=content, ContentType='text/html', ACL='public-read')