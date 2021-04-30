#!/usr/bin/python3

import boto3
import datetime
import json
import mysql.connector
from mysql.connector import Error
import os

import includes.dbconn
from includes.dbconn import connection, cursor, get_row, get_rows, pcursor

import includes.generate_home_page
from includes.generate_home_page import generate_home_page
from includes.generate_players_page import generate_players_page
from includes.generate_trades_page import generate_trades_page

###################################################

with open('.env.json') as json_file:
	env = json.load(json_file)

season = env["season"]

s3 = boto3.resource('s3')

###################################################

push_to_s3 = env["push_to_s3"]
create_local_files = env["create_local_files"]

generate_home_page(connection, season, s3, push_to_s3, create_local_files)

generate_players_page(connection, season, s3, push_to_s3, create_local_files)

generate_trades_page(connection, season, s3, push_to_s3, create_local_files)

exit()
