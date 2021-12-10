#!/bin/bash

set -e
FILE_LIST="eigen_List_Of_Tests.txt"
bin="$(ls ~/tensorflow/bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test)"
EIGEN="${bin}"

cat "${FILE_LIST}" | \
while read -r TEST
do
	TEST_NAME="$( echo ${TEST} | tr -d " ")"
	printf ">> Running ${TEST_NAME} "
	printf "($(grep -n "$TEST" ${FILE_LIST} | cut -d ":" -f1 )/$(awk 'END{print NR}' ${FILE_LIST})): \n"

	perf record -o ${TEST_NAME}_record.data $EIGEN --benchmark_filter="${TEST}" \

	sleep 1
done

