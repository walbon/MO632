#!/usr/bin/env python3

import sys
import json
import numpy as np
from matplotlib import pyplot as plt

def main():
    args = sys.argv[1:]

    jasons = []
    for arg in args:
        if ".json" in arg:
            jasons.append(arg)

    if len(jasons) < 1:
        sys.exit()

    jasons_proc = dict()
    all_data = dict()

    for f in jasons:
        with open (f,'r') as data:
            content_json = json.loads(data.read())
        content = dict()
        for x in range(len(content_json['benchmarks'])):
            name = content_json['benchmarks'][x]['name']
            real_time = content_json['benchmarks'][x]['real_time']
            cpu_time = content_json['benchmarks'][x]['cpu_time']
            items_per_second = content_json['benchmarks'][x]['items_per_second']
            content[name] = dict()
            content[name]['real_time'] = real_time
            content[name]['cpu_time'] = cpu_time
            content[name]['items_per_second'] = items_per_second
        all_data[f] = content

    Yaxis_real_time = dict()
    Yaxis_cpu_time = dict()
    Yaxis_itemspsc = dict()
    for f in jasons:
        Yaxis_real_time[f] = []
        Yaxis_cpu_time[f] = []
        Yaxis_itemspsc[f] = []
        for n in sorted(all_data[f].keys()):
            Yaxis_real_time[f].append(all_data[f][n]['real_time'])
            Yaxis_cpu_time[f].append(all_data[f][n]['cpu_time'])
            Yaxis_itemspsc[f].append(all_data[f][n]['items_per_second'])

    Xaxis_items = np.arange(0,len(all_data[f]))

    # graphs
    colors = ["tab:orange","tab:green","tab:blue","tab:brown","tab:red"]

    fig, axis = plt.subplots(3, sharex=True)

    axis[0].set_title("Items per second")
    for n in range(len(jasons)):
        axis[0].plot(Xaxis_items, Yaxis_itemspsc[jasons[n]], color=colors[n],label=jasons[n].split("-")[-1].split(".")[0])

    axis[1].set_title("CPU Time")
    for n in range(len(jasons)):
        axis[1].plot(Xaxis_items, Yaxis_cpu_time[jasons[n]], color=colors[n])

    axis[2].set_title("Real Time")
    for n in range(len(jasons)):
        axis[2].plot(Xaxis_items, Yaxis_real_time[jasons[n]], color=colors[n])

    legend = axis[0].legend(loc='upper right', shadow=True, fontsize='x-large')



    plt.show()

if __name__ == "__main__":
    main()

