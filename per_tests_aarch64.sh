#!/bin/bash

set -e
FILE_LIST="eigen_List_Of_Tests.txt"
bin="$(ls ~/tensorflow/bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test)"
EIGEN="${bin} --benchmark_out_format=json --benchmark_format=json"

trap printout SIGINT

function printout(){
	echo "]}" >> "$(cat .OUTPUT_FILE)"
	rm -rf .OUTPUT_FILE
        exit
}

cat "${FILE_LIST}" | \
while read -r TEST
do
	TEST_NAME="$( echo ${TEST} | tr -d " ")"
	OUTPUT="output_${TEST_NAME}.json"
	new_dir="results/${TEST_NAME}"
	N=0
	ea_core="NaN"
	ea_memory="NaN"
	ea_l2="NaN"
	seconds="NaN"
	printf ">> Running ${TEST_NAME} "
	printf "($(grep -n "$TEST" ${FILE_LIST} | cut -d ":" -f1 )/$(awk 'END{print NR}' ${FILE_LIST})): \n"
	printf "${new_dir}/${OUTPUT}" > .OUTPUT_FILE
	mkdir -p "${new_dir}"
	pushd "${new_dir}"
	printf "{ \"data\" : [ { \"timestamp\": \"%s\"} " "$(date +%Y%m%d-%T.%N)" > "${OUTPUT}"
	while [ $N -lt 10 ]
	do
		: Run benchmark turn $N
		printf " $N"
		while IFS= read -r line
		do
			[[ "$line" =~ "ea_core" ]] && \
				ea_core="$(echo $line | grep ea_core |\
					sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" )"
			[[ "$line" =~ "ea_memory" ]] && \
				ea_memory="$(echo $line | grep ea_memory   | \
					sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" )"
			[[ "$line" =~ "ea_l2" ]] && \
				ea_l2="$(echo $line | grep ea_l2   | \
					sed -e "s;\(.*\) Joules.*;\1;g ; s;,;\.;g" )"
			[[ "$line" =~ "seconds" ]] && \
				seconds="$(echo $line | grep seconds  | sed -e \
				"s;\(.*\) seconds time elapsed.*;\1;g ; s;,;\.;g" )"
		done < <(
		perf stat \
		-B -r 1 \
		-e ea_core \
		-e ea_memory \
		-e ea_l2 \
		$EIGEN --benchmark_filter="${TEST}" \
			--benchmark_out="eigen_benchmark_cpu_test-$(uname -m)_$(hostname -s)-$N.json" 2>&1 | \
			grep -e ea_core -e ea_memory -e ea_l2 -e seconds )

                printf ",{ \"timestamp\": \"%s\", \"ea_core\": %s, \"ea_memory\": %s, \"ea_l2\": %s, \"seconds\": %s }" \
                        "$(date +%Y%m%d-%T.%N)" "${ea_core}" "${ea_memory}" "${ea_l2}" "${seconds}" >> "${OUTPUT}"
		N=$((N+1))
	done
	printf ']}' >> "${OUTPUT}"
	popd
	sleep 1
done

