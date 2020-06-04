#!/bin/bash

OUTPUT_DIR_BASE="/home/gregth/workspace/advcomparch/ex3/outputs"
SNIPER_DIR="/home/gregth/workspace/advcomparch/ex3/sniper-7.3"

echo "Outputs to be processed located in: $OUTPUT_DIR_BASE"
output="*Benchmark*|*Instructions Run*|*Percentage %*\n"
for benchdir in $OUTPUT_DIR_BASE/*; do
  bench=$(basename $benchdir)
  instructions=$(cat $benchdir/$bench.DW_01-WS_001.out/sim.out | sed -n 2p | cut -d "|" -f 2 | tr -d '[:space:]')
  percentage=$(echo "scale=2; $instructions/10000000"| bc | awk '{printf "%2.2f", $0}')
  output="$output$bench|$instructions|$percentage\n"
done
echo -ne $output | column -t -s '|'