#!/usr/bin/env python

import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

## For nbit predictors
outputDir = "../report/graphs/4-3/"

axes = dict()
benches = []

for outFile in sys.argv[1:]:
    fp = open(outFile)

    benchfile = outFile.split('/')[-1]
    nametokens = benchfile.split('.')
    benchname = nametokens[0] + '.' + nametokens[1]
    print(benchname)

    line = fp.readline()
    while line:
        if line.startswith("Total Instructions"):
            total_instructions = float(line.split(":")[1])

        if line.startswith("  BTB-"):
            if benchname not in benches:
                benches.append(benchname)
            tokens = line.split()
            combo = tokens[0].replace(':','')

            print(tokens)
            correct = float(tokens[1])
            incorrect = float(tokens[2])
            target_incorrect = float(tokens[4])
            total = correct + incorrect
            missprediction_rate = (target_incorrect + incorrect) / total_instructions * 100
            axes.setdefault(combo, []).append(missprediction_rate)

        line = fp.readline()
    fp.close()

print(benches)
for (key, val) in axes.items():
    print (key, val)

fig, ax = plt.subplots(figsize=(10, 13))
ax.grid(axis='x')
ax.set_axisbelow(True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(True)
ax.spines['bottom'].set_color('darkgray')
ax.spines['left'].set_visible(True)
ax.spines['left'].set_color('darkgray')

percentage = [str(x) + '%' for x in np.arange(0, 51, 5)]
bar_thickness = 0.6
combos_count = len(axes.keys())
y_pos = (combos_count+ 1) * bar_thickness * np.arange(len(benches))
x_pos = np.arange(len(percentage))
matplotlib.axes.Axes.tick_params(ax, colors='dimgray')

counter = 0
handles = []
labels = []
maxval = -1;
for (combo, vals) in axes.items():
    p = ax.barh(y_pos + bar_thickness*counter, np.array(vals), height=bar_thickness, align='center')
    labels.append(combo)
    handles.append(p)

    i = 0
    for bar_val in vals:
        maxval = max(maxval, bar_val)
        plt.text(x = bar_val + 1 , y = -0.05 + (counter + i*(combos_count+1)) *bar_thickness ,
            s = "{:.2f}".format(bar_val)+'%',
            size = 6)
        i += 1

    counter += 1

ax.set_yticks(y_pos + 0.5*combos_count*bar_thickness)
ax.set_yticklabels(benches)
ax.set_ylim(-0.5, bar_thickness*(combos_count+1)*len(benches))
ax.set_xticks(5*x_pos)
ax.set_xlim(0,2*maxval)
ax.set_xticklabels(percentage)
ax.legend(handles, labels)

if False:
    for i in range (0,12):
        plt.text(x = a_Axis[i]+1.5 , y = -0.05+(i*5*height), s = "{:.2f}".format(a_Axis[i])+'%',
                size = 9, bbox=dict(color='steelblue'))
        plt.text(x = d_Axis[i]+1.5 , y = -0.15+3*height+(i*5*height), s = "{:.2f}".format(d_Axis[i])+'%',
                size = 9, bbox=dict(color='indianred'))

plt.title("Prediction Misses + Target Misspredictions over Total Instructions (%)")

plt.savefig(outputDir + 'bar_chart.png', bbox_inches="tight", frame=True, pad_inches=0.3)
plt.savefig("4-3-target",bbox_inches="tight")