#!/usr/bin/env python3

import sys
import json
import numpy as np
from matplotlib import pyplot as plt

def main():
    args = sys.argv[1:]

    jasons = []
    items = []
    base_x = 'cpu_time'

    args = iter(args)
    for arg in args:
        if arg == "--base":
            base_x = next(args)
        elif ".json" in arg:
            jasons.append(arg)
        else:
            items.append(arg)

    if len(jasons) == 0:
        sys.exit()

    if len(items) == 0:
        items = ['real_time','items_per_second']
    if not base_x in items:
        items.append(base_x)
    if not 'name' in items:
        items.append('name')

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
        Xaxis_items = []

        for i in items:
            Yaxis[i][f] = []

        count = 0
        ordem = [na for na in sorted(all_data[f].items(), key = lambda x:all_data[f][x[0]][base_x])]
        for n in ordem:
            count+=1
            Xaxis_items.append(all_data[f][n[0]][base_x])
            print(count,all_data[f][n[0]]['name'].split("(")[1])
            for i in items:
                Yaxis[i][f].append(all_data[f][n[0]][i])

    # graphs
    colors = ["#FF671F", "#0f62fe", "tab:green", "tab:brown","tab:red"]

    # Removing the items that are not valuable to have a graph based on the X values and names of
    # tests
    items.remove('name')

    if len(items) > 1:
        fig, axis = plt.subplots(len(items), sharex=True, sharey=False)
        fig.subplots_adjust(hspace=.2)
        fig.subplots_adjust(wspace=.1)
        fig.subplots_adjust(bottom=.1)
        fig.subplots_adjust(left=.035)
        fig.subplots_adjust(right=.990)
        fig.subplots_adjust(top=.952)
        legendado = []
        for i in items:
            once = 0
            axis[items.index(i)].set_title(i.replace('_',' '))
            for n in range(len(jasons)):
                axis[items.index(i)].bar(np.arange(1,len(Xaxis_items)+1)+once*.2,
                                        Yaxis[i][jasons[n]],
                                        color=colors[n],
                                        label=f"{jasons[n].split('-')[-1].split('.')[0]}",
                                        width=1/(1+len(jasons)))
                axis[items.index(i)].set_xlim(-5,len(Xaxis_items)+5)
                axis[items.index(i)].set_ylim(-min(Yaxis[i][jasons[n]])/20,max(Yaxis[i][jasons[n]])*1.20)

                if once < len(jasons):
                    once = once + 1
                    if not jasons[n] in legendado:
                        legend = fig.legend(loc='lower center', shadow=True, fontsize='x-large', ncol = 2)
                        legendado.append(jasons[n])
                if 'time' in i:
                    axis[items.index(i)].set_ylabel("[seconds]")
                if 'items_per_second' in i:
                    axis[items.index(i)].set_ylabel("[calcs/second]")
    else:
        fig, axis = plt.subplots()
        for i in items:
            axis.set_title(i)
            for n in range(len(jasons)):
                axis.plot(Xaxis_items, Yaxis[i][jasons[n]],
                        color=colors[n],label=jasons[n].split("-")[-1].split(".")[0])
                legend = fig.legend(loc='lower center', shadow=True, fontsize='x-large', ncol = 2)

    plt.show()

if __name__ == "__main__":
    main()

