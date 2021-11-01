#!/bin/bash

set -e

FILE_LIST="eigen_List_Of_Tests.txt"

EIGEN="/root/gcc/objdir/tensorflow/bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test
--benchmark_out_format=json
--benchmark_format=json
--copt='-DEIGEN_ALTIVEC_DISABLE_MMA'
"

cat "${FILE_LIST}" | \
while read -r line
do
	new_dir="results/$( echo ${line} | tr -d " ")"
	mkdir -p "${new_dir}"
	pushd "${new_dir}"
	N=0
	while [ $N -lt 10 ]
	do
			: Run benchmark turn $N
			set -x
			$EIGEN --benchmark_filter="${line}" \
			--benchmark_out=eigen_benchmark_cpu_test-$(uname -m)_$(hostname	-s)-NoMMA-$N.json
			set +x
			N=$((N+1))
	done
	popd
	sleep 1m
done

