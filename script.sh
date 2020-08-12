#!/bin/bash
#IFS= read -ra lines < max_bugs_format_for_automation
source ~/anaconda3/etc/profile.d/conda.sh
conda activate untitled
set -x
FUZZER=afl
RED=$(tput setaf 1)
NC=$(tput sgr0)
GREEN=$(tput setaf 2)

readarray -t lines < bugs_selection_format_for_automation
cd /home/vaush/Work/fuzzbench/oss_fuzz
for line in "${lines[@]}"
do
	IFS=' ' read -ra tokens <<< "$line"
	date=$(echo ${tokens[2]} | tr -dc '[:digit:]')
	benchmark_name=${tokens[0]}_${tokens[1]}_$date
	if PYTHONPATH=.. python3 ./benchmark_integration.py -p ${tokens[0]} -f ${tokens[1]} -r /src/${tokens[4]} -c ${tokens[3]} -d ${tokens[2]} -n $benchmark_name > /home/vaush/Work/fuzzbench_benchmark_integration_logs/$benchmark_name-integration.log 2>&1; then
		echo "${GREEN}Integration completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
	else
		echo "${RED}Integration failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
	fi
	cd ..
	if sudo make build-$FUZZER-$benchmark_name > ~/Work/fuzzbench_benchmark_integration_logs/$benchmark_name-build.log 2>&1; then	
		echo "${GREEN}Build testing completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
	else
		echo "${RED}Build testing failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
	fi
#	if sudo make run-$FUZZER-$benchmark_name > ~/Work/fuzzbench_benchmark_integration_logs/$benchmark_name-run.log 2>&1; then	
#		echo "${GREEN}Run testing completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
#	else
#		echo "${RED}Run testing failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
#	fi
	cd oss_fuzz
done
cd ~/Work/OSSFuzzWebScraper
set +x	
