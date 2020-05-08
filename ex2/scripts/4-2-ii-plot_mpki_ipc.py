#!/usr/bin/env python

import sys
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import numpy as np
from scipy.stats import mstats

## For nbit predictors
predictors_to_plot = [ "  Nbit-32K-1", "  Nbit-16K-2", "  Nbit-8K-4", "  2bitFSM"]
outputDir = "../report/graphs/4-2ii/"

mpki_Axis = []
mpki_dict = {}
for outFile in sys.argv[1:]:
	fp = open(outFile)

	x_Axis = []
	mpki_Axis = []

	benchName = outFile.split('/')[-1]
	titleTokens = benchName.split('.')
	title = titleTokens[0] + '.' + titleTokens[1]

	line = fp.readline()
	while line:
		tokens = line.split()
		if line.startswith("Total Instructions:"):
			total_ins = long(tokens[2])
		else:
			for pred_prefix in predictors_to_plot:
				if line.startswith(pred_prefix):
					predictor_string = tokens[0].split(':')[0]
					correct_predictions = long(tokens[1])
					incorrect_predictions = long(tokens[2])
					x_Axis.append(predictor_string)
					val = (incorrect_predictions / (total_ins / 1000.0))
					mpki_Axis.append(val)
					mpki_dict.setdefault(predictor_string, []).append(val)

		line = fp.readline()

	fig, ax1 = plt.subplots()
	ax1.grid(True)

	myorder = [2, 0, 1, 3] # Ad Hoc
	mpki_Axis = [mpki_Axis[i] for i in myorder]
	x_Axis = [x_Axis[i] for i in myorder]


	xAx = np.arange(len(x_Axis))
	ax1.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
	ax1.set_xticklabels(x_Axis, rotation=25)
	ax1.set_xlim(-0.5, len(x_Axis) - 0.5)
	ax1.set_ylim(min(mpki_Axis) - 0.05, max(mpki_Axis) + 0.05)
	ax1.set_ylabel("$MPKI$")
	line1 = ax1.plot(mpki_Axis, label="mpki", color="red",marker='x')

	plt.title("MPKI for " + title + " [Fixed Hardware 32K Bits]")

	plt.savefig(outputDir + title.replace('.', '-') + '.png', bbox_inches="tight", frame=True, pad_inches=0.3)
	plt.clf()
	plt.cla()

avg_mpk = []
print(mpki_dict)
for key in x_Axis:
		#mpki_Axis.append(mstats.gmean(mpki_dict[key]))
		avg_mpk.append(mstats.gmean(mpki_dict[key]))
fig, ax1 = plt.subplots()
ax1.grid(True)

xAx = np.arange(len(x_Axis))
ax1.xaxis.set_ticks(np.arange(0, len(x_Axis), 1))
ax1.set_xticklabels(x_Axis, rotation=25)
ax1.set_xlim(-0.5, len(x_Axis) - 0.5)
ax1.set_ylim(min(avg_mpk) - 0.05 * min(avg_mpk), max(avg_mpk) + 0.05 * max(avg_mpk))
plt.title("Geometric Average MPKI")
ax1.set_ylabel("$MPKI$")
line2 = ax1.plot(avg_mpk, label="Geometric Mean mpki", color="green",marker='o')
plt.savefig(outputDir + 'mean.png', bbox_inches="tight", frame=True, pad_inches=0.3)