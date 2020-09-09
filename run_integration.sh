#!/bin/bash
FUZZER=libfuzzer
RED=$(tput setaf 1)
NC=$(tput sgr0)
GREEN=$(tput setaf 2)
debug=0
run_test=0
fuzzbench_folder=""
cwd=$(pwd)
usage(){echo "Usage: $0 [-d] [-r] -p <fuzzbench_path>"; exit $1;}
while getopts ":hdrp:" opt; do
  case ${opt} in
    h ) usage 0 
      ;;
    d ) debug=1
      ;;
    r ) run_test=1
      ;;
    p ) fuzzbench_folder=${OPTARG}
      ;;
    *) usage 1
      ;;
  esac
done
shift $((OPTIND -1))
if [ -z "${fuzzbench_folder}" ]; then
	usage 1
fi
if [$debug -eq 1]; then
       set -x
fi       
mkdir -p $cwd/fuzzbench_benchmark_integration_logs
readarray -t lines < $cwd/bugs_selection_format_for_automation
cd ${fuzzbench_folder}/benchmarks
for line in "${lines[@]}"
do
	IFS=' ' read -ra tokens <<< "$line"
	date=$(echo ${tokens[2]} | tr -dc '[:digit:]')
	benchmark_name=${tokens[0]}_${tokens[1]}
	if PYTHONPATH=.. python3 ./oss_fuzz_benchmark_integration.py -p ${tokens[0]} -f ${tokens[1]} -c ${tokens[3]} -d ${tokens[2]} -n $benchmark_name > $cwd/fuzzbench_benchmark_integration_logs/$benchmark_name-integration.log 2>&1; then
		echo "${GREEN}Integration completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
	else
		echo "${RED}Integration failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
	fi
	cd ..
	if sudo make build-$FUZZER-$benchmark_name > $cwd/fuzzbench_benchmark_integration_logs/$benchmark_name-build.log 2>&1; then	
		echo "${GREEN}Build testing completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
	else
		echo "${RED}Build testing failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
	fi
	if [${run_test} -eq 1]; then
		if sudo make run-$FUZZER-$benchmark_name > ~/Work/fuzzbench_benchmark_integration_logs/$benchmark_name-run.log 2>&1; then			echo "${GREEN}Run testing completed for project ${tokens[0]} with target ${tokens[1]}${NC}"
		else
			echo "${RED}Run testing failed for project ${tokens[0]} with target ${tokens[1]}${NC}" 
		fi
	fi
	cd benchmarks
done
cd $cwd
if [$debug -eq 1]; then
       set +x
fi       
