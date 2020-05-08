#!/usr/bin/env python

import sys
import numpy as np
from scipy.stats import mstats

## We need matplotlib:
## $ apt-get install python-matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

x_Axis = []
ipc_Axis = []
mpki_Axis = []

ipc_dict = {}
mpki_dict = {}

for outFile in sys.argv[2:]:
    fp = open(outFile)
    line = fp.readline()
    while line:
        tokens = line.split()
        if (line.startswith("Total Instructions: ")):
            total_instructions = long(tokens[2])
        elif (line.startswith("IPC:")):
            ipc = float(tokens[1])
        elif (line.startswith("  Data Tlb")):
            entriesLine = fp.readline()
            l1_size = entriesLine.split()[1]
            sizeLine = fp.readline()
            l1_bsize = sizeLine.split()[2]
            assocLine = fp.readline()
            l1_assoc = assocLine.split()[1]
        elif (line.startswith("Tlb-Total-Misses")):
            l1_total_misses = long(tokens[1])
            l1_miss_rate = float(tokens[2].split('%')[0])
            mpki = l1_total_misses / (total_instructions / 1000.0)
        line = fp.readline()

    dir = 'fixed'
    color = 'red'
    title = sys.argv[1]
    if sys.argv[1] == 'variable':
        color = 'blue'
        dir = 'var'
        # First simulation set as reference
        size_baseline = 8
        asssoc_baseline = 4

        size_slowdown_factor = 1.1 ** np.log2(float(l1_size) / size_baseline) 
        assoc_slowdown_factor = 1.05  **  np.log2(float(l1_assoc) / asssoc_baseline)
        
        # Update ipc to reflect instruction per original cycle
        new_cycle = 1 * size_slowdown_factor * assoc_slowdown_factor
        ipc = ipc / float(new_cycle)

    fp.close()

    l1ConfigStr = '{}.{}.{}B'.format(l1_size,l1_assoc,l1_bsize)
    if l1ConfigStr not in x_Axis:   
        x_Axis.append(l1ConfigStr)

    if l1ConfigStr not in mpki_dict:
        mpki_dict[l1ConfigStr] = [mpki]
        ipc_dict[l1ConfigStr] = [ipc]
    else:
        mpki_dict[l1ConfigStr].append(mpki)
        ipc_dict[l1ConfigStr].append(ipc)

for key in x_Axis:
    print key
    ipc_Axis.append(mstats.gmean(ipc_dict[key]))
    mpki_Axis.append(mstats.gmean(mpki_dict[key]))

print x_Axis
print ipc_Axis
print mpki_Axis

fig, ax1 = plt.subplots()
ax1.grid(True)
ax1.set_xlabel("TlbEntries.Assoc.PageSize")

xAx = np.arange(len(x_Axis))
ax1.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
ax1.set_xticklabels(x_Axis, rotation=45)
ax1.set_xlim(-0.5, len(x_Axis) - 0.5)
ax1.set_ylim(min(ipc_Axis) - 0.05 * min(ipc_Axis), max(ipc_Axis) + 0.05 * max(ipc_Axis))
ax1.set_ylabel("$IPC$")
line1 = ax1.plot(ipc_Axis, label="Mean ipc", color=color,marker='x')

ax2 = ax1.twinx()
ax2.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
ax2.set_xticklabels(x_Axis, rotation=45)
ax2.set_xlim(-0.5, len(x_Axis) - 0.5)
ax2.set_ylim(min(mpki_Axis) - 0.05 * min(mpki_Axis), max(mpki_Axis) + 0.05 * max(mpki_Axis))
ax2.set_ylabel("$MPKI$")
line2 = ax2.plot(mpki_Axis, label="Mean TlbD_mpki", color="green",marker='o')

lns = line1 + line2
labs = [l.get_label() for l in lns]

benchmark = outFile.split(".")[0]
plt.title("[TLB (" + title + " cycle) - Geometric Mean IPC vs MPKI]")
lgd = plt.legend(lns, labs)
lgd.draw_frame(False)
print sys.argv[1]
print dir
outputIMGName = "../../report/graphs/TLB/" + dir + "/mean.png"
plt.savefig(outputIMGName, bbox_inches="tight")