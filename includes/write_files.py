

def write_to_local_disk(content, page, season):

	paths = {
		"home": "html/output/index.html",
		"players": f'html/output/seasons/{season}/players/index.html'
	}

	f = open(paths[page], "w")
	f.write(content)
	f.close()