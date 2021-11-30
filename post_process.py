#!/usr/bin/env python3


import matplotlib.pyplot as plt
import numpy as np
import json
import datetime
import os

TESTS = dict()
RESULTS_ppc = dict()
SENSORS = []
FOLDER = 'ppc10_round2/results'
SENSORS_DATA = 'ppc10_round2/jsons_MMA/output-all-power10-r2.json'
DATA = dict()

def scan_benchmarks(folder_root):
	for files in os.scandir(folder_root):
		if files.is_dir():
			scan_benchmarks(folder_root+"/"+files.name)
		elif "Convolution" in folder_root:
			if files.name.endswith(".json") and \
			   files.name.startswith("eigen"):
				with open(folder_root+"/"+files.name) as data:
					jason = json.load(data)
					# Datetime should be the key to match
					# with sensors.
					# UTC -6h = CST
					# timestamp from host(CDT)
					# timestamp from sensors(UTC)
					date_start= datetime.datetime.fromisoformat(jason['context']['date'])
					date_end = date_start + \
						   datetime.timedelta(seconds=jason['benchmarks'][0]['real_time']*1e-9)
					bkm = jason['benchmarks'][0]['name']
					if not bkm in RESULTS_ppc.keys():
					    RESULTS_ppc[bkm] = list()
					jason['benchmarks'][0]['context'] = jason['context']
					jason['benchmarks'][0]['context']['date_start'] = date_start
					jason['benchmarks'][0]['context']['date_end'] = date_end
					RESULTS_ppc[bkm].append(jason['benchmarks'][0])
		else:
			print("out: " + files.name)


print(f"Processing the results in : {FOLDER}")
scan_benchmarks(FOLDER)
print(f"...read {len(RESULTS_ppc.keys())} total.")

# Reading the all content of bmc occ sensors in one file
print(f"Processing data from: {SENSORS_DATA}")
with open(SENSORS_DATA,'r') as data:
	SENSORS = json.load(data)

	# the timestamp captured in bmc was in UTC
	for s in SENSORS['data'][1:]:
		# timestamp from sensors(UTC)
		data_ = datetime.datetime.strptime(s['timestamp'],'%Y%m%d-%H:%M:%S').replace(tzinfo=datetime.timezone.utc)
		if not data_ in DATA.keys():
        		DATA[data_] = list()
		DATA[data_].append(s)
		# in the 1 sec of windows of sampling the ratio depends on the number of samples collected
		# eg. ratio = 1/samples
print(f"...proceeded {len(SENSORS['data'])} samples.")


print(f"Processing the sensors data with test set.")
matched = dict()
for r in RESULTS_ppc:
	for test_ in RESULTS_ppc[r]:
		found=False
		if not 'sensors' in test_.keys():
			# creates the sensors entry in dictionary
			test_['sensors'] = list()
		# Run all dataset of sensors to match with timestamp of tests.
		for data in DATA:
			if data >= test_['context']['date_start'] and \
			   data <= test_['context']['date_end'] :
				ratio = 1/len(DATA[data])
				samples = 2 + int((test_['real_time']*1e-9)/ratio)
				test_['sensors'] = DATA[data][0:samples]
				matched[r] = True
				found = True
			# Skip the data loop when is later than the target time of testing.
			elif data > test_['context']['date_end']:
				break
		if not found:
			matched[r] = False
print(f"..Test that matched {len([ x for x in matched if matched[x] == True ])} , ",\
      f"and without match {len([ x for x in matched if matched[x] == False ])}")

print(f"\nStarting to merge the Results of benchmarks with sensors.")
PROCESSED_ppc = dict()
for test in RESULTS_ppc:
	real_time = []
	cpu_time = []
	items_per_second = []
	p0_power = []
	p1_power = []
	size = len(RESULTS_ppc[test])
	for it in RESULTS_ppc[test]:
		real_time.append(it['real_time'])
		cpu_time.append(it['cpu_time'])
		items_per_second.append(it['items_per_second'])
		p0 = []
		p1 = []
		for power in it['sensors']:
			p0.append(power['p0_power'])
			p1.append(power['p1_power'])
		p0_power.append(np.average(p0))
		p1_power.append(np.average(p1))

	PROCESSED_ppc[test] = dict()
	PROCESSED_ppc[test]['real_time'] = np.average(real_time)
	PROCESSED_ppc[test]['cpu_time'] = np.average(cpu_time)
	PROCESSED_ppc[test]['items_per_second'] = np.average(items_per_second)
	PROCESSED_ppc[test]['p0_power'] = np.average(p0_power)
	PROCESSED_ppc[test]['p1_power'] = np.average(p1_power)

print(f"... done. PowerPc sensors collected and each test got the average of usage.")

RESULTS_x86 = dict()
def scan_benchmarks_x86(folder_root):
	for files in os.scandir(folder_root):
		if files.is_dir():
			scan_benchmarks_x86(folder_root+"/"+files.name)
		elif files.name.endswith("json") and files.name.startswith("eigen"):
			with open(folder_root+"/"+files.name) as data:
				jason = json.load(data)
			date_start= datetime.datetime.fromisoformat(jason['context']['date'])
			date_end = date_start + \
				   datetime.timedelta(seconds=jason['benchmarks'][0]['real_time']*1e-9)
			bkm = jason['benchmarks'][0]['name']
			if not bkm in RESULTS_x86.keys():
				RESULTS_x86[bkm] = list()
			jason['benchmarks'][0]['context'] = jason['context']
			jason['benchmarks'][0]['context']['date_start'] = date_start
			jason['benchmarks'][0]['context']['date_end'] = date_end
			RESULTS_x86[bkm].append(jason['benchmarks'][0])

print("\n Processing x86 data")
scan_benchmarks_x86('x86_64-Intel-XeonCooperLake_round2/results')
print(f"...read {len(RESULTS_x86)} test groups.")

def scan_output_x86(folder_root):
	for files in os.scandir(folder_root):
		if files.is_dir():
			scan_output_x86(folder_root+"/"+files.name)
		elif files.name.endswith(".json") and files.name.startswith("output"):
			with open(folder_root+"/"+files.name) as data:
				jason = json.load(data)
			bkm = "BM_SPATIAL_NAME("+files.name.split("_")[1].split(".")[0].replace(",",", ")+")"
			for index in range(len(jason['data'])-1) :
				RESULTS_x86[bkm][index]['sensors'] = dict()

				RESULTS_x86[bkm][index]['sensors']['pkg'] = jason['data'][index+1]['pkg']
				RESULTS_x86[bkm][index]['sensors']['ram'] = jason['data'][index+1]['ram']
				RESULTS_x86[bkm][index]['sensors']['duration'] = jason['data'][index+1]['seconds']

print(f"Collecting sensor data then merge them in test groups")
scan_output_x86('x86_64-Intel-XeonCooperLake_round2/results')
print(f"...read all sensor data and matched them.")



print(f"\nStarting to merge the Results of benchmarks with sensors.")
PROCESSED_x86 = dict()
for test in RESULTS_x86:
	real_time = []
	cpu_time = []
	items_per_second = []
	pkg_power = []
	size = len(RESULTS_x86[test])
	for it in RESULTS_x86[test]:
		real_time.append(it['real_time'])
		cpu_time.append(it['cpu_time'])
		items_per_second.append(it['items_per_second'])
		pkg_power.append(np.average(it['sensors']['pkg']))

	PROCESSED_x86[test] = dict()
	PROCESSED_x86[test]['real_time'] = np.average(real_time)
	PROCESSED_x86[test]['cpu_time'] = np.average(cpu_time)
	PROCESSED_x86[test]['items_per_second'] = np.average(items_per_second)
	PROCESSED_x86[test]['pkg_power'] = np.average(pkg_power)

print(f"... done. PowerPc sensors collected and each test got the average of usage.")


print(f"Drawing graphs of power")
y_ppc = [(PROCESSED_ppc[value]['p0_power']+PROCESSED_ppc[value]['p1_power'])*PROCESSED_ppc[value]['real_time']*1e-9 for value in PROCESSED_x86.keys() ]
y_x86 = [ PROCESSED_x86[value]['pkg_power'] for value in PROCESSED_x86.keys() ]

y_ppc_realtime = [ PROCESSED_ppc[value]['real_time'] for value in PROCESSED_x86.keys() ]
y_x86_realtime = [ PROCESSED_x86[value]['real_time'] for value in PROCESSED_x86.keys() ]

y_ppc_cpu = [ PROCESSED_ppc[value]['cpu_time'] for value in PROCESSED_x86.keys() ]
y_x86_cpu = [ PROCESSED_x86[value]['cpu_time'] for value in PROCESSED_x86.keys() ]

y_x86_items = [ PROCESSED_x86[value]['items_per_second'] for value in PROCESSED_x86.keys() ]
y_ppc_items = [ PROCESSED_ppc[value]['items_per_second'] for value in PROCESSED_x86.keys() ]

x = [ Xx for Xx in PROCESSED_x86.keys() ]

fig,ax = plt.subplots(4,sharex=True)


ax[0].set_title("Comparison of Power Usage")
ax[0].set_ylabel("Total Energy(Joules)")
ax[0].plot(x,y_x86,color="tab:blue",label="Intel Xeon Platinum")
ax[0].plot(x,y_ppc,color="tab:orange", label="IBM Power 10")
fig.legend(loc='upper right', shadow=True, fontsize='x-large')

ax[1].set_title("Comparison of CPU Time")
ax[1].set_ylabel("Total CPU Time")
ax[1].plot(x,y_x86_cpu,color="tab:blue",label="Intel Xeon Platinum")
ax[1].plot(x,y_ppc_cpu,color="tab:orange", label="IBM Power 10")

ax[2].set_title("Comparison of Real Time")
ax[2].set_ylabel("Total Real Time")
ax[2].plot(x,y_x86_realtime,color="tab:blue",label="Intel Xeon Platinum")
ax[2].plot(x,y_ppc_realtime,color="tab:orange", label="IBM Power 10")

ax[3].set_title("Comparison of Items per second")
ax[3].set_ylabel("Total Items per second")
ax[3].plot(x,y_x86_items,color="tab:blue",label="Intel Xeon Platinum")
ax[3].plot(x,y_ppc_items,color="tab:orange", label="IBM Power 10")

plt.xticks([])
plt.grid(False)
plt.show()

