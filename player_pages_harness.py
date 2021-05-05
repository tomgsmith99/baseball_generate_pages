#!/usr/bin/python3

import boto3
import json
import mysql.connector
from mysql.connector import Error

from includes.dbconn import connection

from includes.generate_player_pages import generate_player_pages

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

season = env["season"]

s3 = boto3.resource('s3')

###################################################

push_to_s3 = env["push_to_s3"]
create_local_files = env["create_local_files"]

generate_player_pages(connection, season, s3, push_to_s3, create_local_files)

exit()
