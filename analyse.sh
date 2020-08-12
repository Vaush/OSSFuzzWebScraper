#! /bin/bash
source ~/anaconda3/etc/profile.d/conda.sh
conda activate untitled
num=20
if [ $# -ge 1 ]; then
	if [ $1 == "-d" ]; then
		exec 3>&2
	else
		exec 3>&2 1>/dev/null
	fi
	if [ $# -ge 2]; then
		num=$2
	fi
else
	exec 3>&2 1>/dev/null
fi
#set -x
if [ -f "bugs_1" ]; then
	echo "Using the already existing bug scraping files" >&3
	s1=0
else
	echo "Running the bug scraping script" >&3
	python main.py
	s1=$?
fi
if [ $s1 -eq 0 ]; then
	echo "Bug scraping succeeded" >&3
	python analyse.py
	s2=$?
	if [ $s2 -eq 0 ]; then
		echo "Bug analysis and counting succeeded" >&3
		sort -r -n -k 4 max_bugs_num | head -n$num > max_bugs_num_sorted_selection
		s3=$?
		if [ $s3 -eq 0 ]; then
			echo "Bug sorting and selection succeeded" >&3
			python get_hashes.py
			s4=$?
			if [ $s4 -eq 0 ]; then
				echo "Project commits' hashes retrieval succedeed" >&3
				python write_format_for_automation.py 1>&3
				s5=$?
				if [ $s5 -eq 0 ]; then
					rm bugs_1*
					rm max_bugs*
					echo "Bug retrieval completely successful" >&3
					exit 0
				fi
			fi
		fi
	fi
fi
echo "An error occurred" >&3

#set +x
