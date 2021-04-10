#!/usr/bin/python3

import boto3
import datetime

s3 = boto3.resource('s3')

x = datetime.datetime.now()

print(x)

print(x.year)
print(x.day)
print(x.month)

day = str(x.day)
month = str(x.month)

if len(month) == 1:
	month = "0" + month
if len(day) == 1:
	day = "0" + day

filename = str(x.year) + "-" + month + "-" + day + ".html"

data = "<html>hello!</html>"

# s3.Bucket('baseball.tomgsmith.com').put_object(Key='test.html', Body=data)

s3.Bucket('baseball.tomgsmith.com').put_object(Key=filename, Body=data)

