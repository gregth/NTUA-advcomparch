#!/bin/bash

OUTPUT_DIR_BASE="/home/gregth/workspace/advcomparch/ex3/outputs"

echo "Outputs to be processed located in: $OUTPUT_DIR_BASE"
for benchdir in $OUTPUT_DIR_BASE/*; do
  bench=$(basename $benchdir)
  echo -e "\nProcessing directory: $bench"
  cmd1="./plot_ipc.py $benchdir/*.out"
  cmd2="./plot_energy.py $benchdir/*.out"
  cmd2="./plot_area.py $benchdir/*.out"
  cmd2="./plot_energy_common.py $benchdir/*.out"
  /bin/bash -c "$cmd1"
done
#!/bin/bash

BENCHMAKRS="astar cactusADM gcc GemsFDTD gobmk hmmer mcf omnetpp sjeng soplex xalancbmk zeusmp"
