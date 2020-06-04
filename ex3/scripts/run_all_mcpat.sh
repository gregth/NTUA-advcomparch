#!/bin/bash

OUTPUT_DIR_BASE="/home/gregth/workspace/advcomparch/ex3/outputs"
SNIPER_DIR="/home/gregth/workspace/advcomparch/ex3/sniper-7.3"

echo "Outputs to be processed located in: $OUTPUT_DIR_BASE"
for benchdir in $OUTPUT_DIR_BASE/*; do
  bench=$(basename $benchdir)
  echo -e "$bench: "
  cat $benchdir/$bench.DW_01-WS_001.out/sim.out | sed -n 2p
done

for benchdir in $OUTPUT_DIR_BASE/*; do
  bench=$(basename $benchdir)
  echo -e "\nProcessing directory: $bench"

  for configdir in $benchdir/*; do
    config=$(basename $benchdir)
    echo -e "\nProcessing config: $config"

    cmd="${SNIPER_DIR}/tools/advcomparch_mcpat.py -d $configdir -t total -o $configdir/info > $configdir/power.total.out"
    echo CMD: $cmd
    #cmd="./plot_ipc.py $benchdir/*.out"
    /bin/bash -c "$cmd"
  done
done