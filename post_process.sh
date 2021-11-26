#!/usr/bin/env python3


import matplotlib.pyplot as plt
import numpy as np
import json
import datetime
import os

def lookfor(time,windowS=5):
	delta = datetime.timedelta(seconds=windowS)
	for data in sensors['data']:
		if time - datetime.datetime.strptime(['timestamp'],'%Y%m%d-%H:%M:%S') < delta:
		    return(data['timestamp'])


TESTS = dict()
RESULTS = dict()
SENSORS = []
FOLDER = 'ppc10_round2/results'
SENSORS_DATA = 'ppc10/occ_sensors_MMA/all.json'


def scan_benchmarks(folder_root):

	for files in os.scandir(folder_root):
		if files.is_dir():
			#print("IsDIR : " + files.name)
			scan_benchmarks(folder_root+"/"+files.name)
		elif "Convolution" in folder_root:
			#print("\t"+files.name)
			if files.name.endswith(".json") and \
			   files.name.startswith("eigen"):
				with open(folder_root+"/"+files.name) as data:
					jason = json.load(data)
					# Datetime should be the key to match
					# with sensors.
					# timestamp from sensors(UTC)
					# timestamp from host(CDT)
					# UTC -6h = CST
					date_= datetime.datetime.fromisoformat(jason['context']['date'])
					date_= date_.replace(tzinfo=datetime.timezone.utc)
					data_new = date_ - datetime.timedelta(hours=6) #CST+6h=UTC
					RESULTS[data_new] = dict()
					RESULTS[data_new]['benchmark'] = jason
					RESULTS[data_new]['sensors'] = []
		else:
			print("out: " + files.name)

scan_benchmarks(FOLDER)

# Reading the all content of bmc occ sensors in one file
print(f"Processing data from: {SENSORS_DATA}")
with open(SENSORS_DATA,'r') as data:
	SENSORS = json.load(data)
print(f"...proceeded {len(SENSORS['data'])} samples.")

not_found=0
for sensor in SENSORS['data'][1:]:
	# Convert timestamp(UTC)
	date_ = datetime.datetime.strptime(sensor['timestamp'],'%Y%m%d-%H:%M:%S')
	date_ = date_.replace(tzinfo=datetime.timezone.utc)
	if date_ in RESULTS.keys():
		RESULTS[date_]['sensors'].append(sensor)
	else:
		not_found+=1
print(f"Not founds: {not_found}")


# Mapping of Name of testing by the datetime
TESTS = dict()
for dt in RESULTS:
	    TESTS[RESULTS[dt]['benchmark']['benchmarks'][0]['name']]=dt

print("Total of tests",len(TESTS))
print("Total of runs",len(RESULTS))
counting_need=0
for t in RESULTS:
	if len(RESULTS[t]['sensors']) < 2:
		counting_need+=1
print(f"Which need more data: {counting_need}")




