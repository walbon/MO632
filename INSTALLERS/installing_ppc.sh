#!/bin/bash

set -ex

: GCC
yum update -y

yum install -y gcc-toolset-11 || {
	yum install -y tar bzip2 wget git-core gcc gcc-c++ flex vim
	git clone git://gcc.gnu.org/git/gcc.git
	pushd gcc
	git reset --hard releases/gcc-10.3.0
	./contrib/download_prerequisites
	mkdir objdir
	pushd objdir
	../configure --prefix=$HOME/gcc-10.3.0 --enable-languages=c,c++,fortran,go --enable-multilib
	make -j$(nproc)
	make -j$(nproc) install
	popd
	popd
}

: Bazel

dnf install dnf-plugins-core
dnf copr enable vbatts/bazel -y
dnf install bazel4 -y

: TensorFlow
cd
yum install -y python36-devel python3-pip
pip3 install --upgrade pip
python3 -m venv .
source ./bin/activate
pip3 install -U Cython
pip3 install -U pip numpy wheel keras_preprocessing
git clone https://github.com/tensorflow/tensorflow.git
pushd tensorflow
rm -rf .bazelversion
bazel clean
./configure

if yum install -y gcc-toolset-11 ; then
	bazel test --jobs $(nproc) --test_output=all --cache_test_results=no \
		//tensorflow/core/kernels:eigen_benchmark_cpu_test

else

# For PowerPc, usage of gcc-toolset-10 at least to enablement of newer linker
	cat > Benchmarks << EOF
source $HOME/bin/activate
CC=/root/gcc-10.3.0/bin/gcc CXX=/root/gcc-10.3.0/bin/g++ BAZEL_LINKLIBS=-l%:libstdc++.a \
bazel test --jobs $(nproc) --test_output=all --cache_test_results=no \
//tensorflow/core/kernels:eigen_benchmark_cpu_test

EOF
	chmod +x Benchmarks

	yum install -y gcc-toolset-10
	scl enable gcc-toolset-10 ./Benchmarks
fi
