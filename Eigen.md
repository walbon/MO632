# Setup of the benchmark testing

## GCC

It needs the GCC 10.3 at least to enable MMA feature on Power 10 and tensorflow must be built for the targeted architectures. 

```
yum update -y
yum install -y tar bzip2 wget git-core gcc gcc-c++ flex vim
git clone git://gcc.gnu.org/git/gcc.git
cd gcc
git reset --hard releases/gcc-10.3.0
./contrib/download_prerequisites
mkdir objdir
cd objdir
../configure --prefix=$HOME/gcc-10.3.0 --enable-languages=c,c++,fortran,go
make -j$(nproc)
make -j$(nproc) install
```
## Bazel
Bazel is the engine used by the tensorflow project. That needs at least v.3.2.0 to run the build, so I am adding the latest from the alternative repository.

```
dnf install dnf-plugins-core
dnf copr enable vbatts/bazel
dnf install bazel4

```

## Tensorflow
It is Important to update some python libraries such as numpy, cython etc, to give support of building of the tensorflow binaries.

```
yum install -y python36-devel python3-pip
pip3 install --upgrade pip
python3 -m venv .
source ./bin/activate
pip3 install -U Cython
pip3 install -U pip numpy wheel keras_preprocessing
git clone https://github.com/tensorflow/tensorflow.git
cd tensorflow
rm -rf .bazelversion
bazel clean
./configure
# For PowerPc, usage of gcc-toolset-10 to enablement of newer linker
yum install -y gcc-toolset-10
scl enable gcc-toolset-10 bash
source /$HOME/bin/activate
CC=/root/gcc-10.3.0/bin/gcc CXX=/root/gcc-10.3.0/bin/g++ BAZEL_LINKLIBS=-l%:libstdc++.a bazel test --jobs 8 --test_output=all --cache_test_results=no //tensorflow/core/kernels:eigen_benchmark_cpu_test
exit # exiting scl
```

## Running the Convolution Performance Testing 
Perform the testing, the data will be collected into a json file to help the comparison.
```
./bazel-out/*-opt/bin/tensorflow/core/kernels/eigen_benchmark_cpu_test --benchmark_filter=_ --benchmark_out_format=json --benchmark_out=eigen_benchmark_cpu_test-$(uname -m).json --benchmark_format=json
```

## References
https://docs.python.org/3/tutorial/venv.html

https://github.com/maxiwell/tensorflow/wiki/Building-and-Running-TF-Tests#build-the-whole-tensorflow

https://www.tensorflow.org/install/source

https://access.redhat.com/documentation/en-us/red_hat_enterprise_linux/8/html/developing_c_and_cpp_applications_in_rhel_8/gcc-toolset_toolsets

