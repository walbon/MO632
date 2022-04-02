#!/usr/bin/env python3


import matplotlib.pyplot as plt
import numpy as np
import json
import datetime
import os
import sys

TESTS = dict()
RESULTS_ppc = dict()
SENSORS = []
FOLDER = 'ppc10_round2/results'
SENSORS_DATA = 'ppc10_round2/jsons_MMA/output-all-power10-r2.json'
DATA = dict()

base_x = 'pkg_power'
# capturing the --base parameter
args = sys.argv[1:]
args = iter(args)
for arg in args:
    if arg == "--base":
        base_x = next(args)

print(f"[Sorting the X axis values based on {base_x} of x86]")

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
                           datetime.timedelta(seconds=jason['benchmarks'][0]['real_time']*1e-9*jason['benchmarks'][0]['iterations'])
                    bkm = jason['benchmarks'][0]['name']
                    if not bkm in RESULTS_ppc.keys():
                        RESULTS_ppc[bkm] = list()
                    jason['benchmarks'][0]['context'] = jason['context']
                    jason['benchmarks'][0]['context']['date_start'] = date_start
                    jason['benchmarks'][0]['context']['date_end'] = date_end
                    RESULTS_ppc[bkm].append(jason['benchmarks'][0])
        else:
            print(f"out: {files.name}")


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
                test_['sensors'] = DATA[data]
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
    cpu_time = []
    real_time = []
    items_per_second = []
    p0_power = []
    p1_power = []
    iterations = []
    size = len(RESULTS_ppc[test])
    for it in RESULTS_ppc[test]:
        cpu_time.append(it['cpu_time'])
        real_time.append(it['real_time'])
        items_per_second.append(it['items_per_second'])
        iterations.append(it['iterations'])
        p0 = []
        p1 = []
        for power in it['sensors']:
            p0.append(power['p0_power'])
            p1.append(power['p1_power'])
        p0_power.append(np.average(p0))
        p1_power.append(np.average(p1))

    PROCESSED_ppc[test] = dict()
    PROCESSED_ppc[test]['cpu_time'] = np.average(cpu_time)
    PROCESSED_ppc[test]['real_time'] = np.average(real_time)
    PROCESSED_ppc[test]['items_per_second'] = np.average(items_per_second)
    PROCESSED_ppc[test]['p0_power'] = np.average(p0_power)
    PROCESSED_ppc[test]['p1_power'] = np.average(p1_power)
    PROCESSED_ppc[test]['iterations'] = np.average(iterations)

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
                   datetime.timedelta(seconds=jason['benchmarks'][0]['real_time']*1e-9*jason['benchmarks'][0]['iterations'])
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
    cpu_time = []
    real_time= []
    items_per_second = []
    pkg_power = []
    duration = []
    iterations= []
    size = len(RESULTS_x86[test])
    for it in RESULTS_x86[test]:
        cpu_time.append(it['cpu_time'])
        real_time.append(it['real_time'])
        items_per_second.append(it['items_per_second'])
        pkg_power.append(np.average(it['sensors']['pkg']))
        duration.append(np.average(it['sensors']['duration']))
        iterations.append(it['iterations'])

    PROCESSED_x86[test] = dict()
    PROCESSED_x86[test]['cpu_time'] = np.average(cpu_time)
    PROCESSED_x86[test]['real_time'] = np.average(real_time)
    PROCESSED_x86[test]['items_per_second'] = np.average(items_per_second)
    PROCESSED_x86[test]['pkg_power'] = np.average(pkg_power)
    PROCESSED_x86[test]['duration'] = np.average(duration)
    PROCESSED_x86[test]['iterations'] = np.average(iterations)

print(f"... done. PowerPc sensors collected and each test got the average of usage.")


print(f"Collect the statistic data of perf records")
with open("reports_x86","r") as rep:
    REPORTS_x86 = json.load(rep)
with open("reports_ppc10","r") as rep:
    REPORTS_ppc = json.load(rep)


print(f"Drawing graphs of power")

colors = { "Intel": "#FF671F", "IBM":"#0f62fe" }

# both archs are using the same x values
x = [ Xx for Xx in PROCESSED_x86.keys() ]

x = sorted( x , key = lambda value : PROCESSED_x86[value][base_x])

print(f"Drawing graphs with the base as {base_x}")

y_ppc = \
[(PROCESSED_ppc[value]['p0_power']+PROCESSED_ppc[value]['p1_power'])*PROCESSED_ppc[value]['real_time']*1e-9*PROCESSED_ppc[value]['iterations'] for value in x ]
y_x86 = [ PROCESSED_x86[value]['pkg_power'] for value in x ]

total = 0
for t in y_ppc:
    total+=t
xtotal=0
for s in y_x86:
    xtotal+=s
print(f" PPC {total}, Intel {xtotal}")


y_ppc_ = \
[((PROCESSED_ppc[value]['p0_power']+PROCESSED_ppc[value]['p1_power'])*PROCESSED_ppc[value]['real_time']*1e-9*PROCESSED_ppc[value]['iterations'])*100*(256/448)/PROCESSED_x86[value]['pkg_power'] for value in x ]
print(f"Average of power usage between Ppc/x86: {np.average(y_ppc_)}")


y_ppc_duration = [ PROCESSED_ppc[value]['cpu_time'] for value in x]
y_x86_duration = [ PROCESSED_x86[value]['cpu_time'] for value in x ]

y_ppc_items = [ PROCESSED_ppc[value]['items_per_second'] for value in x ]
y_x86_items = [ PROCESSED_x86[value]['items_per_second'] for value in x ]

y_ppc_perf = [ REPORTS_ppc[value]['value'] for value in x ]
y_x86_perf = [ REPORTS_x86[value]['value'] for value in x ]

fig,ax = plt.subplots(4,sharex=True)
fig.subplots_adjust(hspace=.318)
fig.subplots_adjust(wspace=.2)
fig.subplots_adjust(bottom=.1)
fig.subplots_adjust(left=.058)
fig.subplots_adjust(right=.99)
fig.subplots_adjust(top=.952)

ax[0].set_title("Consumption of energy of test set")
ax[0].set_ylabel("Total Energy(Joules)")
ax[0].bar([value    for value in range(len(x))],y_x86,color=colors['Intel'],label="Intel Xeon Platinum", width=0.3)
ax[0].bar([value+.3 for value in range(len(x))],y_ppc,color=colors['IBM'], label="IBM Power 10", width=0.3)
fig.legend(loc='lower center', shadow=True, fontsize='x-large', ncol=2)

ax[1].set_title("MMA Usage")
ax[1].set_ylabel("%")
ax[1].bar([value for value in range(len(x))],y_ppc_perf, color=colors['IBM'], width=0.3)
ax[1].set_ylim(0,100)
ax[1].grid(color='#95a5a6', linestyle='--', linewidth=1, axis='y', alpha=0.6)
plt.grid(False)

ax[2].set_title("CPU time average")
ax[2].set_ylabel("Nanoseconds(ns)")
ax[2].bar([value for value in range(len(x))],y_x86_duration,color=colors['IBM'],label="Intel Xeon Platinum", width=0.3)
ax[2].bar([value+.3 for value in range(len(x))],y_ppc_duration,color=colors['Intel'], label="IBM Power 10", width=0.3)

ax[3].set_title("calcs/second")
ax[3].set_ylabel("calcs/second")
ax[3].bar([value for value in range(len(x))],y_x86_items,color=colors['IBM'],label="Intel Xeon Platinum", width=0.3)
ax[3].bar([value+.3 for value in range(len(x))],y_ppc_items,color=colors['Intel'], label="IBM Power 10", width=0.3)


plt.xticks(np.arange(1,len(x)+1))
#plt.grid(False)
plt.show()

