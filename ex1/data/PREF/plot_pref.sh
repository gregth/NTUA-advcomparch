#!/usr/bin/env python

import sys
import numpy as np

## We need matplotlib:
## $ apt-get install python-matplotlib
import matplotlib
import re
matplotlib.use('Agg')
import matplotlib.pyplot as plt

x_Axis = []
ipc_Axis = []
mpki_Axis = []

for outFile in sys.argv[1:]:
    fp = open(outFile)
    line = fp.readline()
    while line:
        tokens = line.split()
        if (line.startswith("Total Instructions: ")):
            total_instructions = long(tokens[2])
        elif (line.startswith("IPC:")):
            ipc = float(tokens[1])
        elif (line.startswith("L2_prefetching: Yes")):
            parts = re.split('\)|\(', line)
            print parts
            n = parts[1]
        elif (line.startswith("L2-Total-Misses")):
            l1_total_misses = long(tokens[1])
            l1_miss_rate = float(tokens[2].split('%')[0])
            mpki = l1_total_misses / (total_instructions / 1000.0)
        line = fp.readline()

    fp.close()

    print n
    l1ConfigStr = '{} Blocks'.format(n)
    print l1ConfigStr
    x_Axis.append(l1ConfigStr)
    ipc_Axis.append(ipc)
    mpki_Axis.append(mpki)

print x_Axis
print ipc_Axis
print mpki_Axis

fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.set_xlabel("Number of prefetched blocks")

xAx = np.arange(len(x_Axis))
ax1.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
ax1.set_xticklabels(x_Axis, rotation=45)
ax1.set_xlim(-0.5, len(x_Axis) - 0.5)
ax1.set_ylim(min(ipc_Axis) - 0.05 * min(ipc_Axis), max(ipc_Axis) + 0.05 * max(ipc_Axis))
ax1.set_ylabel("$IPC$")
line1 = ax1.plot(ipc_Axis, label="ipc", color="red",marker='x')

ax2 = ax1.twinx()
ax2.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
ax2.set_xticklabels(x_Axis, rotation=45)
ax2.set_xlim(-0.5, len(x_Axis) - 0.5)
ax2.set_ylim(min(mpki_Axis) - 0.05 * min(mpki_Axis), max(mpki_Axis) + 0.05 * max(mpki_Axis))
ax2.set_ylabel("$MPKI$")
line2 = ax2.plot(mpki_Axis, label="L2D_mpki", color="green",marker='o')

lns = line1 + line2
labs = [l.get_label() for l in lns]

benchmark = outFile.split(".")[0]
plt.title("[L2 With enabled Prefetching - BENCHMARK: " + benchmark + "]  IPC vs MPKI")
lgd = plt.legend(lns, labs)
lgd.draw_frame(False)
outputIMGName = "../../report/graphs/PREF/" + benchmark + ".png"
plt.savefig(outputIMGName, bbox_inches="tight")