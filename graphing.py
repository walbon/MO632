#!/usr/bin/env python3

import sys
import json
import numpy as np
from matplotlib import pyplot as plt

def main():
    args = sys.argv[1:]

    jasons = []
    items = []

    for arg in args:
        if ".json" in arg:
            jasons.append(arg)
        else:
            items.append(arg)

    if len(jasons) == 0:
        sys.exit()

    if len(items) == 0:
        items = ['real_time','cpu_time','items_per_second']

    jasons_proc = dict()
    all_data = dict()

    for f in jasons:
        with open (f,'r') as data:
            content_json = json.loads(data.read())
        content = dict()

        Xaxis_items = []
        for x in range(len(content_json['benchmarks'])):
            name = content_json['benchmarks'][x]['name']
            content[name] = dict()
            Xaxis_items.append(content_json['benchmarks'][x]['name'])
            for i in items:
                content[name][i] = content_json['benchmarks'][x][i]
        all_data[f] = content

    Yaxis = dict()
    for i in items:
        Yaxis[i] = dict()

    for f in jasons:
        for i in items:
            Yaxis[i][f] = []

        for n in sorted(all_data[f].keys()):
            for i in items:
                Yaxis[i][f].append(all_data[f][n][i])

    #Xaxis_items = np.arange(0,len(all_data[f]))

    # graphs
    colors = ["tab:orange","tab:green","tab:blue","tab:brown","tab:red"]

    if len(items) > 1:
        fig, axis = plt.subplots(len(items), sharex=True)
        for i in items:
            axis[items.index(i)].set_title(i.replace('_',' '))
            for n in range(len(jasons)):
                axis[items.index(i)].plot(Xaxis_items, Yaxis[i][jasons[n]],
                        color=colors[n],label=f"{jasons[n].split('-')[-1].split('.')[0]}")
            legend = axis[0].legend(loc='upper right', shadow=True, fontsize='x-large')
    else:
        fig, axis = plt.subplots()
        for i in items:
            axis.set_title(i)
            for n in range(len(jasons)):
                axis.plot(Xaxis_items, Yaxis[i][jasons[n]], color=colors[n],label=jasons[n].split("-")[-1].split(".")[0])
                legend = axis.legend(loc='upper right', shadow=True, fontsize='x-large')

    plt.xticks([])

    plt.show()

if __name__ == "__main__":
    main()

