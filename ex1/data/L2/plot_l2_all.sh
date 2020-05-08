#!/bin/bash

BENCHS="blackscholes bodytrack canneal facesim ferret fluidanimate freqmine rtview swaptions streamcluster"

for bench in $BENCHS; do
    pin_cmd="./plot_l2.sh variable ${bench}*"
	time $pin_cmd
    pin_cmd="./plot_l2.sh fixed ${bench}*"
	time $pin_cmd
done

    pin_cmd="./plot_mean_l2.py fixed *out"
	time $pin_cmd
    pin_cmd="./plot_mean_l2.py variable *out"
	time $pin_cmd