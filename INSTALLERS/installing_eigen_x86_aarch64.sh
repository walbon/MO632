#~/bin/bash

set -ex

yum update -y
yum install -y tar bzip2 wget git-core gcc gcc-c++ flex vim glibc-devel
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

dnf install dnf-plugins-core
dnf copr enable vbatts/bazel -y
dnf install bazel4 -y

cd
yum install -y python36-devel python3-pip
pip3 install --upgrade pip
python3 -m venv .
source ./bin/activate
pip3 install -U Cython
pip3 install -U pip numpy wheel keras_preprocessing
pip install numpy
git clone https://github.com/tensorflow/tensorflow.git
pushd tensorflow
rm -rf .bazelversion
bazel clean
./configure
source $HOME/bin/activate

CC=/root/gcc-10.3.0/bin/gcc CXX=/root/gcc-10.3.0/bin/g++ BAZEL_LINKLIBS=-l%:libstdc++.a \
bazel test --jobs $(nproc) --test_output=all \
--cache_test_results=no //tensorflow/core/kernels:eigen_benchmark_cpu_test

popd

