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

def get_ipc_from_output_file(output_file):
	ipc = -999
	fp = open(output_file, "r")
	line = fp.readline()
	while line:
		if "IPC" in line:
			ipc = float(line.split()[2])
		line = fp.readline()

	fp.close()
	return ipc

def tuples_by_dispatch_width(tuples):
	ret = []
	tuples_sorted = sorted(tuples, key=operator.itemgetter(0))
	for key,group in itertools.groupby(tuples_sorted,operator.itemgetter(0)):
		ret.append((key, zip(*map(lambda x: x[1:], list(group)))))
	return ret

global_ws = [1,2,4,8,16,32,64,96,128,192,256,384]

if len(sys.argv) < 2:
	print "usage:", sys.argv[0], "<output_directories>"
	sys.exit(1)

results_tuples = []

for dirname in sys.argv[1:]:
	if dirname.endswith("/"):
		dirname = dirname[0:-1]
	basename = os.path.basename(dirname)
	output_file = dirname + "/sim.out"

	(bench, input_size, dispatch_width, window_size) = get_params_from_basename(basename)
	ipc = get_ipc_from_output_file(output_file)
	results_tuples.append((dispatch_width, window_size, ipc))


markers = ['.', 'o', 'v', '*', 'D']
#fig = plt.figure()
#ax = fig
fig, ax = plt.subplots()
plt.grid(True)
ax.set_xlabel("$Window Size$", fontsize=14)
ax.set_ylabel("$IPC$", fontsize=14)

i = 0
tuples_by_dw = tuples_by_dispatch_width(results_tuples)

x_ticks = np.arange(0, len(global_ws))
x_labels = map(str, global_ws)
ax.xaxis.set_ticks(x_ticks)
ax.xaxis.set_ticklabels(x_labels)

for tuple in tuples_by_dw:
	dw = tuple[0]
	ws_axis = tuple[1][0]
	ipc_axis = tuple[1][1]
	skipped = len(global_ws)-len(ipc_axis)
	x_ticks = np.arange(skipped, len(global_ws))

	ax.plot(x_ticks, ipc_axis, linewidth=1, label="DW_"+str(dw), marker=markers[i%len(markers)])
	i = i + 1

# Shrink current axis by 20%
box = ax.get_position()
#ax.set_position([box.x0, box.y0, box.width * 0.8, box.height])
# Put a legend to the right of the current axis
lgd = ax.legend(ncol=1, loc='upper left', bbox_to_anchor=(0, 1), prop={'size':10})

output_base = '../report/graphs/ipc/' 
output = output_base + bench + '.png'
print "Saving: " 	+ output
plt.savefig(output, bbox_extra_artists=(lgd,), bbox_inches='tight')
