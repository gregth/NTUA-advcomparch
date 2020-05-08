#!/usr/bin/env python

import sys
import numpy as np

## We need matplotlib:
## $ apt-get install python-matplotlib
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

total, conditionalNotTaken, conditionalTaken, unconditional, calls, returns = 0, 0, 0, 0, 0, 0
instructions = []
benches = []
outputDir = "../report/graphs/4-1/"

for outFile in sys.argv[1:]:
    fp = open(outFile)

    benchName = outFile.split('/')[-1]
    titleTokens = benchName.split('.')
    title = titleTokens[0] + '.' + titleTokens[1]
    benches.append(title)

    line = fp.readline()
    while line:
        line = line.strip()
        tokens = line.split()
        if line.startswith("Total Instructions:"):
            total = float(tokens[2])
        elif line.startswith("Total-Branches"):
            totalBranches = float(tokens[1])
        elif line.startswith("Conditional-Taken-Branches:"):
            conditionalTaken = float(tokens[1])
        elif line.startswith("Conditional-NotTaken"):
            conditionalNotTaken = float(tokens[1])
        elif line.startswith("Unconditional-Branches"):
            unconditional = float(tokens[1])
        elif line.startswith("Calls"):
            calls = float(tokens[1])
        elif line.startswith("Returns"):
            returns = float(tokens[1])
        line = fp.readline()


    conditionalTaken = (conditionalTaken / totalBranches) * 100
    conditionalNotTaken = (conditionalNotTaken / totalBranches) * 100
    unconditional = (unconditional / totalBranches) * 100
    calls = (calls / totalBranches) * 100
    returns = (returns / totalBranches) * 100
    instructions.append(total)

    print(conditionalTaken)
    print(conditionalNotTaken)
    print(unconditional)
    print(calls)
    print(returns)

    labels = ['Conditional-Taken ('+"{:.2f}".format(conditionalTaken)+'%)',
        'Conditional-NotTaken ('+"{:.2f}".format(conditionalNotTaken)+'%)',
        'Unconditional ('+"{:.2f}".format(unconditional)+'%)',
        'Calls ('+"{:.2f}".format(calls)+'%)',
        'Returns ('+"{:.2f}".format(returns)+'%)']

    sizes = [conditionalTaken, conditionalNotTaken, unconditional, calls, returns]

    #ax1.pie(sizes, explode=explode, labels=labels, autopct='%1.1f%%',
    #    shadow=True, startangle=90)j

    fig = plt.figure()
    ax = plt.subplot(111)
    plt.axis('equal')

    radius = 1 
    wedges, texts = plt.pie(sizes, radius=radius, wedgeprops=dict(width=0.4), startangle=180)
    bbox_props = dict(boxstyle="square,pad=0.1", fc="w", ec="k", lw=0.72)
    kw = dict(arrowprops=dict(arrowstyle="-"),
            bbox=bbox_props, zorder=0, va="center")

    for i, p in enumerate(wedges):
        ang = (p.theta2 - p.theta1)/2. + p.theta1
        y = radius*np.sin(np.deg2rad(ang))
        x = radius*np.cos(np.deg2rad(ang))
        horizontalalignment = {-1: "right", 1: "left"}[int(np.sign(x))]
        connectionstyle = "angle,angleA=0,angleB={}".format(ang)
        kw["arrowprops"].update({"connectionstyle": connectionstyle})
        #plt.annotate(labels[i], xy=(x, y), xytext=(0.6*np.sign(x), 2.2*y),
        #            horizontalalignment=horizontalalignment, **kw)

    percentage = float(totalBranches)/total*100
    stats = 'Total Branches: ' + str(long(totalBranches)) + " - {:.2f}% ".format(percentage)  + "of total instructions"
    plt.title(stats, fontsize=12)

    box = ax.get_position()
    # Put a legend to the right of the current axis
    ax.legend(wedges, labels, loc='center left', bbox_to_anchor=(1, 0.5))

    plt.savefig(outputDir + title.replace('.', '-') + '.png', bbox_inches="tight", frame=True, pad_inches=0.3)
    plt.show()


print(instructions)
plt.figure();
fig, ax = plt.subplots()
ax.grid(axis='x')
ax.set_axisbelow(True)
matplotlib.axes.Axes.ticklabel_format(ax, axis='x', style='sci', useMathText=True)

ax.spines['top'].set_visible(False)
ax.spines['right'].set_visible(False)
ax.spines['bottom'].set_visible(True)
ax.spines['bottom'].set_color('darkgray')
ax.spines['left'].set_visible(True)
ax.spines['left'].set_color('darkgray')

y_pos = np.arange(len(benches))

matplotlib.axes.Axes.tick_params(ax, colors='dimgray')
p = ax.barh(y_pos, instructions, height=0.4, align='center', color='red')
ax.set_yticks(y_pos)
ax.set_yticklabels(benches)
ax.invert_yaxis()  # labels read top-to-bottom
ax.set_xlabel('Total Instructions', color='dimgray')
ax.set_title('Total Instructions', color='k')
# ax.draw_frame(False)
#ax.legend((p[0]), ('Total Instructions',''))

plt.show()
plt.savefig(outputDir + "total.png",bbox_inches="tight", frame=True, pad_inches=0.3)