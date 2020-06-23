#!/bin/bash

## Example of usage: ./run_sniper.sh gcc
## Modify the following paths appropriately
## CAUTION: use only absolute paths below!!!
SNIPER_EXE=/home/gregth/workspace/advcomparch/ex3/sniper-7.3/run-sniper
SNIPER_CONFIG=/home/gregth/workspace/advcomparch/ex4/code/ask4.cfg
BINARY_CODE=/home/gregth/workspace/advcomparch/ex4/code

OUTPUT_DIR_BASE="/home/gregth/workspace/advcomparch/ex4/outputs/3-2-shared-new"
makedir $OUTPUT_DIR_BASE
architectures="4_4_share-all 1_4_share-L3 1_1_share-nothing"

LOCKTYPES="dtas_cas dtas_ts dttas_cas dttas_ts mutex"
iterations=1000

for LOCKTYPE in $LOCKTYPES; do
	executable=${BINARY_CODE}/locks-sniper-${LOCKTYPE}
	echo "Running: $(basename ${executable})"
	benchOutDir=${OUTPUT_DIR_BASE}/$BENCH
	mkdir -p $benchOutDir

for architecture in $architectures; do
	n_threads=4
	l2=$(echo $architecture | cut -d'_' -f1)
	l3=$(echo $architecture | cut -d'_' -f2)
	name=$(echo $architecture | cut -d'_' -f3)

	for grain_size in 1; do
			outDir=$(printf "%s.NTHREADS_%02d-GRAIN_%03d-NAME_%s.out" $LOCKTYPE $n_threads $grain_size $name)
			outDir="${OUTPUT_DIR_BASE}/${outDir}"

			sniper_cmd="${SNIPER_EXE} \\
				-c ${SNIPER_CONFIG} \\
				-n ${n_threads} \\
				-d ${outDir} \\
				--roi \\
				-g --perf_model/l1_icache/shared_cores=1 \\
				-g --perf_model/l1_dcache/shared_cores=1 \\
				-g --perf_model/l2_cache/shared_cores=$l2 \\
				-g --perf_model/l3_cache/shared_cores=$l3 \\
				-- ${executable} ${n_threads} ${iterations} ${grain_size}"
				echo -e "CMD: $sniper_cmd\n"
				/bin/bash -c "time $sniper_cmd"
	done
done
done
