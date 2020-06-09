#!/usr/bin/env python

import sys, os
import itertools, operator
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np

def get_params_from_basename(basename):
    tokens = basename.split('.')
    bench = tokens[0]
    input_size = 'ref'
    dw = int(tokens[1].split('-')[0].split('_')[1])
    ws = int(tokens[1].split('-')[1].split('_')[1])
    return (bench, input_size, dw, ws)

def get_energy_delay_from_output_file(output_file):
    EDP_1 = 0
    EDP_2 = 0
    EDP_3 = 0
    energy = 0
    fp = open(output_file, "r")
    line = fp.readline()
    while line:
        if 'total' in line:
            power = float(line.split()[1])
            if (line.split()[2] == 'kW'):
                power = power*1000.0

            energy = float(line.split()[3])
            if (line.split()[4] == 'kJ'):
                energy = energy*1000.0
            delay = energy/power
            EDP_1 = energy*delay
            EDP_2 = energy*(delay**2)
            EDP_3 = energy*(delay**3)

        line = fp.readline()

    fp.close()
    return (energy, EDP_1, EDP_2, EDP_3)

def tuples_by_dispatch_width(tuples):
    ret = []
    tuples_sorted = sorted(tuples, key=operator.itemgetter(0))
    for key,group in itertools.groupby(tuples_sorted,operator.itemgetter(0)):
        ret.append((key, list(zip(*map(lambda x: x[1:], list(group))))))
    return ret

global_ws = [1,2,4,8,16,32,64,96,128,192,256,384]

if len(sys.argv) < 2:
    print "usage:", sys.argv[0], "<output_directories>"
    sys.exit(1)


results_tuples = [[] for i in range(4)]

for dirname in sys.argv[1:]:
    if dirname.endswith("/"):
        dirname = dirname[0:-1]
    basename = os.path.basename(dirname)
    output_file = dirname + "/power.total.out"

    (bench, input_size, dispatch_width, window_size) = get_params_from_basename(basename)
    if (window_size < 16): continue
    (energy, EDP_1, EDP_2, EDP_3) = get_energy_delay_from_output_file(output_file)
    results_tuples[0].append((dispatch_width, window_size, energy))
    results_tuples[1].append((dispatch_width, window_size, EDP_1))
    results_tuples[2].append((dispatch_width, window_size, EDP_2))
    results_tuples[3].append((dispatch_width, window_size, EDP_3))


markers = ['.', 'o', 'v', '*', 'D']

fig, axes = plt.subplots(4, figsize=(10,19))
#plt.subplots_adjust(hspace=0.3)
plt.grid(True)
for i in range(4):
    ax = axes[i]
    ax.grid(b=True)

    if (i == 0):
        ylabel = '$Energy\ (J)$'
    elif (i == 1):
        ylabel = '$EDP\ (J*sec)$'
    else:
        ylabel = '$ED^' + str(i) + 'P\ (J*sec^' + str(i) + ')$'
    ax.set_ylabel(ylabel, fontsize=18)

    j = 0
    tuples_by_dw = tuples_by_dispatch_width(results_tuples[i]) 

    x_ticks = np.arange(0, len(global_ws))
    x_labels = map(str, global_ws)
    ax.xaxis.set_ticks(x_ticks)
    ax.xaxis.set_ticklabels(x_labels, fontsize=14)

    ax.tick_params(axis='both', which='major', labelsize=14)
    for tuple in tuples_by_dw:
        dw = tuple[0]
        ws_axis = tuple[1][0]
        area_axis = tuple[1][1]

        skipped = len(global_ws)-len(area_axis)
        x_ticks = np.arange(skipped, len(global_ws))

        ax.plot(x_ticks, area_axis, linewidth=2, label="DW_"+str(dw), marker=markers[j%len(markers)], markersize=10)
        j = j + 1


ax.set_xlabel("$Window Size$", fontsize=18)
lgd = ax.legend(ncol=len(tuples_by_dw), bbox_to_anchor=(0.99, -0.15), prop={'size':12})
output_base = '../report/graphs/edp/' 
output = output_base + bench + '.png'
print "Saving: " 	+ output
plt.savefig(output, bbox_extra_artists=(lgd,), bbox_inches='tight')