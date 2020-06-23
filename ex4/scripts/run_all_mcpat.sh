#!/bin/bash

OUTPUT_DIR_BASE="/home/gregth/workspace/advcomparch/ex4/outputs/3-2-shared-new"
SNIPER_DIR="/home/gregth/workspace/advcomparch/ex3/sniper-7.3"

echo "Outputs to be processed located in: $OUTPUT_DIR_BASE"

for benchdir in $OUTPUT_DIR_BASE/*; do
  bench=$(basename $benchdir)
  echo -e "\nProcessing directory: $bench"

  cmd="${SNIPER_DIR}/tools/advcomparch_mcpat.py -d $benchdir -t total -o $benchdir/info > $benchdir/power.total.out"
  echo CMD: $cmd
  /bin/bash -c "$cmd"
done