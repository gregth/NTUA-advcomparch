#!/bin/bash

BENCHS="blackscholes bodytrack canneal facesim ferret fluidanimate freqmine rtview swaptions streamcluster"

for bench in $BENCHS; do
    pin_cmd="./plot_TLB.sh variable ${bench}*"
	time $pin_cmd
    pin_cmd="./plot_TLB.sh fixed ${bench}*"
	time $pin_cmd
done
