#!/bin/bash

set -e

FILE_LIST="eigen_List_Of_Tests.txt"
bin="$(ls ~/tensorflow/bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test)"
EIGEN="${bin} --benchmark_out_format=json --benchmark_format=json"

cat "${FILE_LIST}" | \
while read -r TEST
do
	TEST_NAME="$( echo ${TEST} | tr -d " ")"
	new_dir="results/${TEST_NAME}"
	N=0

	printf ">> Running ${TEST_NAME} "
        printf "($(grep -n "$TEST" ${FILE_LIST} | cut -d ":" -f1 )/$(awk 'END{print NR}' ${FILE_LIST})): \n"

	mkdir -p "${new_dir}"
	pushd "${new_dir}"
	while [ $N -lt 100 ]
	do
			: Run benchmark turn $N
			printf "$N"
			$EIGEN --benchmark_filter="${TEST}" \
				--benchmark_out=eigen_benchmark_cpu_test-$(uname -m)_$(\
				hostname -s)-${TEST_NAME}-$N.json > /dev/null || printf "ERROR "
			N=$((N+1))
	done
	popd
	sleep 5s
done

