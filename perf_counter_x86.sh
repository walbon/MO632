#!/bin/bash

runs=10
eigen="_"

while [ $# -gt 0 ]
do
	if [ "${1}" == "-n" ]; then
		shift
		runs="$1"
		shift
	else
		eigen="${1}"
		shift
	fi
done

eigen_command="${HOME}/tensorflow/bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test \
	--benchmark_out_format=json --benchmark_format=json \
	--benchmark_out=eigen_benchmark_cpu_test-$(uname -m)_$(hostname -s)_$(date +%Y%m%d-%T).json"

command="${eigen_command} --benchmark_filter=${eigen}"

printf "\n{ \"benchmark_filter\": \"%s\"," "${eigen}"
printf "\n \"data\": ["
for (( r=1; r<=runs; r++ )) do \
	perf stat \
	-B -r 1 \
	-e \"power/energy-cores/\" \
	-e \"power/energy-ram/\" \
	-e \"power/energy-pkg/\" \
	"${command}" 2>&1 | \
		while IFS= read -r line
		do
			[[ "$line" =~ "cores" ]] && echo $line | grep cores |\
				sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" > cores
			[[ "$line" =~ "ram" ]] && echo $line | grep ram   | \
				sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" > ram
			[[ "$line" =~ "pkg" ]] && echo $line | grep pkg   | \
				sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" > pkg
			[[ "$line" =~ "seconds" ]] && echo $line | grep seconds  | \
				sed -e "s;\(.*\) seconds time elapsed.*;\1;g ; s;,;\.;g" > seconds
		done
		[ "$r" -gt 1 ] && printf ", "
		printf "{ \"cores\": %s, \"ram\": %s, \"pkg\": %s, \"seconds\": %s }" \
			"$(cat cores)" "$(cat ram)" "$(cat pkg)" "$(cat seconds)"
done
printf "] }\n"

# fix using vim %s;\(\d*\)\.\(\d\d\d\)\.\(\d\d\);\1\2.\3;g
