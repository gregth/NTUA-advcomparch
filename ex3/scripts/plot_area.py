#!/usr/bin/env python

import sys, os
import itertools, operator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def get_params_from_basename(basename):
    print(basename)
    tokens = basename.split('.')
    bench = tokens[0]
    input_size = 'ref'
    dw = int(tokens[1].split('-')[0].split('_')[1])
    ws = int(tokens[1].split('-')[1].split('_')[1])
    return (bench, input_size, dw, ws)

def get_area_from_output_file(output_file):
    area = 0
    fp = open(output_file, "r")
    line = fp.readline()
    while line:
        if 'Area' in line and 'Processor' in line:
            area = float(line.split()[2	].replace(',', ''))
        line = fp.readline()

    fp.close()
    return area

def tuples_by_dispatch_width(tuples):
    ret = []
    tuples_sorted = sorted(tuples, key=operator.itemgetter(0))
    for key,group in itertools.groupby(tuples_sorted,operator.itemgetter(0)):
        ret.append((key, list(zip(*map(lambda x: x[1:], list(group))))))
    return ret

global_ws = [1,2,4,8,16,32,64,96,128,192,256,384]

if len(sys.argv) < 2:
    print ("usage:", sys.argv[0], "<output_directories>")
    sys.exit(1)

results_tuples = []

for dirname in sys.argv[1:]:
    if dirname.endswith("/"):
        dirname = dirname[0:-1]
    basename = os.path.basename(dirname)
    output_file = dirname + "/info.py"

    (bench, input_size, dispatch_width, window_size) = get_params_from_basename(basename)
    if (window_size < 16): continue
    area = get_area_from_output_file(output_file)
    results_tuples.append((dispatch_width, window_size, area))


markers = ['.', 'o', 'v', '*', 'D']
plt.grid(True)
fig, ax = plt.subplots()
ax.set_xlabel("$Window  Size$", fontsize=14)
ax.set_ylabel("$Area  (mm^2)$", fontsize=14)
ax.grid(b=True)

x_ticks = np.arange(0, len(global_ws))
x_labels = map(str, global_ws)
ax.xaxis.set_ticks(x_ticks)
ax.xaxis.set_ticklabels(x_labels)

i = 0
tuples_by_dw = tuples_by_dispatch_width(results_tuples)
for tuple in tuples_by_dw:
    dw = tuple[0]
    ws_axis = tuple[1][0]
    area_axis = tuple[1][1]
    skipped = len(global_ws)-len(area_axis)

    x_ticks = np.arange(skipped, len(global_ws))

    ax.plot(x_ticks, area_axis, label="DW_"+str(dw), marker=markers[i%len(markers)])
    i = i + 1

lgd = ax.legend(ncol=len(tuples_by_dw), bbox_to_anchor=(1, -0.15), prop={'size':8})
output_base = '../report/graphs/area/' 
output = output_base + 'area.png'
print "Saving: " 	+ output
plt.savefig(output, bbox_extra_artists=(lgd,), bbox_inches='tight')