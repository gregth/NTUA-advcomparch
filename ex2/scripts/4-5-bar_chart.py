#!/usr/bin/env python

import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mstats

## For nbit predictors
outputDir = "../report/graphs/4-5/"
predictors_to_plot = [ "  Static", "  BTFNT", "  Pentium", "  Nbit", "  Local", "  Global", "  Tournament", "  ALPHA"]


def plot(outputDir, benchname, axes, sortit=True):
    fig, ax = plt.subplots(figsize=(9, 7))
    ax.grid(axis='x')
    ax.set_axisbelow(True)

    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['bottom'].set_visible(True)
    ax.spines['bottom'].set_color('darkgray')
    ax.spines['left'].set_visible(True)
    ax.spines['left'].set_color('darkgray')

    percentage = [str(x) for x in np.arange(0, 160, 10)]
    bar_thickness = 0.6
    combos_count = len(axes)
    y_pos = (combos_count+ 1) * bar_thickness * np.arange(len(benches))
    matplotlib.axes.Axes.tick_params(ax, colors='dimgray')

    counter = 0
    handles = []
    labels = []
    maxval = -1;

    if sortit:
        axes = sorted(axes, key=lambda tup: tup[1], reverse=True)

    for (combo, val) in axes:
        p = ax.barh(y_pos + bar_thickness*counter, np.array(val), height=0.7*bar_thickness, align='center')
        labels.append('[ MPKI: ' + "{:.3f}".format(val)+ ' ]' + combo)
        handles.append(p)
        maxval = max(maxval, val)
        plt.text(x = val + 1 , y = -0.05 + counter *bar_thickness , s = "{:.3f}".format(val), size = 10)
        counter += 1;

    ax.set_yticks(y_pos + 0.5*combos_count*bar_thickness)
    ax.set_yticklabels([])
    ax.set_ylim(-0.5, bar_thickness*(combos_count+1)*len(benches))
    ax.set_xlim([0, maxval])
    print(maxval)
    percentage = [str(x) for x in np.arange(0, maxval + 10, 10)]
    x_pos = np.arange(len(percentage))
    ax.set_xticks(10*x_pos)
    ax.set_xticklabels(percentage)
    ax.legend(handles[::-1], labels[::-1], loc='upper center', bbox_to_anchor=(0.5, -0.09),
          fancybox=True, shadow=True, ncol=1)
    plt.xlabel('MPKI')
    plt.ylabel('Predictor')

    plt.title("Predictors comparison for " + benchname)
    plt.savefig(outputDir +  benchname + '.png', bbox_inches="tight", frame=True, pad_inches=0.3)
    plt.cla()
    plt.clf()


axes = dict()
for outFile in sys.argv[1:]:
    fp = open(outFile)
    curaxes = []

    benchfile = outFile.split('/')[-1]
    nametokens = benchfile.split('.')
    benchname = nametokens[0] + '.' + nametokens[1]
    benchname = benchname.replace(".", '-')
    print(benchname)
    benches = []
    print(benchname)

    line = fp.readline()
    while line:
        if line.startswith("Total Instructions"):
            total_instructions = float(line.split(":")[1])

        for pred_prefix in predictors_to_plot:
            if line.startswith(pred_prefix):
                if benchname not in benches:
                    benches.append(benchname)
                tokens = line.split(":")
                combo = tokens[0]
                tokens = tokens[1].split()

                print(tokens)
                correct = float(tokens[0])
                incorrect = float(tokens[1])
                missprediction_rate = incorrect / total_instructions * 1000
                curaxes.append((combo, missprediction_rate))
                axes.setdefault(combo, []).append(missprediction_rate)
 
        line = fp.readline()

    plot(outputDir, benchname, curaxes)
    fp.close()

axes_tuple = []
for label, vals in axes.items():
    axes_tuple.append((label, mstats.gmean(vals)))
plot(outputDir, 'mean', axes_tuple) 

tups = sorted(axes_tuple, key=lambda tup: tup[1], reverse=False)
for (t, p) in tups:
    print(t)



