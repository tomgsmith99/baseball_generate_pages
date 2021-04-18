#!/usr/bin/python3

import includes.dbconn
from includes.dbconn import get_rows

###############################################

query = "SELECT * FROM ownersXseasons_current_view ORDER BY points DESC, nickname ASC"

print(query)

rows = get_rows(query)

print(rows)

