#!/bin/bash

BENCHS="blackscholes bodytrack canneal facesim ferret fluidanimate freqmine rtview swaptions streamcluster"

for bench in $BENCHS; do
    pin_cmd="./plot_pref.sh ${bench}*"
	time $pin_cmd
done
