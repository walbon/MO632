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
	cores="NaN"
	ram="NaN"
	pkg="NaN"
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
			[[ "$line" =~ "cores" ]] && \
				cores="$(echo $line | grep cores |\
					sed -e "s;\(.*\) Joules.*;\1;g ; " )"
			[[ "$line" =~ "ram" ]] && \
				ram="$(echo $line | grep ram   | \
					sed -e "s;\(.*\) Joules.*;\1;g ; " )"
			[[ "$line" =~ "pkg" ]] && \
				pkg="$(echo $line | grep pkg   | \
					sed -e "s;\(.*\) Joules.*;\1;g ; " )"
			[[ "$line" =~ "seconds" ]] && \
				seconds="$(echo $line | grep seconds  | sed -e \
				"s;\(.*\) seconds time elapsed.*;\1;g ; " )"
		done < <(
		perf stat \
		-B -r 1 \
		-e \"power/energy-cores/\" \
		-e \"power/energy-ram/\" \
		-e \"power/energy-pkg/\" \
		$EIGEN --benchmark_filter="${TEST}" \
			--benchmark_out="eigen_benchmark_cpu_test-$(uname -m)_$(hostname -s)-$N.json" 2>&1 | \
			grep -e cores -e ram -e pkg -e seconds )

                printf ",{ \"timestamp\": \"%s\", \"cores\": %s, \"ram\": %s, \"pkg\": %s, \"seconds\": %s }" \
                        "$(date +%Y%m%d-%T.%N)" "${cores}" "${ram}" "${pkg}" "${seconds}" >> "${OUTPUT}"
		N=$((N+1))
	done
	printf ']}' >> "${OUTPUT}"
	popd
	sleep 1
done

