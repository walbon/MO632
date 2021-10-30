#!/usr/bin/env python3

import sys
import json
import numpy as np
from matplotlib import pyplot as plt

colors = ["tab:orange","tab:green","tab:blue","tab:brown","tab:red"]

def main():
    args = sys.argv[1:]

    FILES = []
    ITEMS = []
    jasons = dict()
    Axis_Y = dict()

    for arg in args:
        if ".json" in arg:
            FILES.append(arg)
        else:
            ITEMS.append(arg)

    if len(FILES) == 0:
        sys.exit()

    if len(ITEMS) == 0:
        ITEMS = ['p0_power','p1_power']

    for f in FILES:
        with open (f,'r') as data:
            content_json = json.loads(data.read())
        jasons[f] = content_json

    for f in FILES:
        Axis_Y[f] = dict()
        for it in ITEMS:
            Axis_Y[f][it] = []
            Axis_X = np.arange(1,len(jasons[f]['data']))
            for index in range(1,len(jasons[f]['data'])):
                Axis_Y[f][it].append(jasons[f]['data'][index][it])
    # graphs
    if len(ITEMS) > 1:
        fig, axis = plt.subplots(len(ITEMS), sharex=True)
        for i in ITEMS:
            axis[ITEMS.index(i)].set_title(i)
            for f in FILES:
                axis[ITEMS.index(i)].plot(Axis_X, Axis_Y[f][i],color=colors[FILES.index(f)])

    else:
        fig, axis = plt.subplots(1, sharex=True)
        axis.set_title(ITEMS)
        for f in FILES:
            axis.plot(Axis_X, Axis_Y[f][ITEMS[0]])

    plt.xticks([])
    plt.show()

if __name__ == "__main__":
    main()

