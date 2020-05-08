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


def plot(outputDir, benchname, axes):
    fig, ax = plt.subplots(figsize=(9, 5))
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
    combos_count = len(axes.keys())
    y_pos = (combos_count+ 1) * bar_thickness * np.arange(len(benches))
    matplotlib.axes.Axes.tick_params(ax, colors='dimgray')

    counter = 0
    handles = []
    labels = []
    maxval = -1;
    for (combo, vals) in axes.items():
        p = ax.barh(y_pos + bar_thickness*counter, np.array(vals), height=0.7*bar_thickness, align='center')
        labels.append(combo + ' [' + "{:.2f}".format(vals[0])+ ']')
        handles.append(p)

        i = 0
        for bar_val in vals:
            maxval = max(maxval, bar_val)
            plt.text(x = bar_val + 1 , y = -0.05 + (counter + i*(combos_count+1)) *bar_thickness ,
                s = "{:.3f}".format(bar_val),
                size = 10)
            i += 1

        counter += 1

    ax.set_yticks(y_pos + 0.5*combos_count*bar_thickness)
    ax.set_yticklabels([])
    ax.set_ylim(-0.5, bar_thickness*(combos_count+1)*len(benches))
    ax.set_xlim([0, maxval])
    print(maxval)
    percentage = [str(x) for x in np.arange(0, maxval + 10, 10)]
    x_pos = np.arange(len(percentage))
    ax.set_xticks(10*x_pos)
    ax.set_xticklabels(percentage)
    ax.legend(handles, labels, loc='upper center', bbox_to_anchor=(0.5, -0.05),
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

    benchfile = outFile.split('/')[-1]
    nametokens = benchfile.split('.')
    benchname = nametokens[0] + '.' + nametokens[1]
    benchname = benchname.replace(".", '-')
    print(benchname)
    curaxes = dict()
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
                curaxes.setdefault(combo, []).append(missprediction_rate)
                axes.setdefault(combo, []).append(missprediction_rate)

        line = fp.readline()
    plot(outputDir, benchname, curaxes)
    fp.close()

for label, vals in axes.items():
    axes[label] = [mstats.gmean(vals)]
plot(outputDir, 'mean', axes)


