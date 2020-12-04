#!/usr/bin/env bash
set -x
set -e

rm -rf ./build/
mkdir build
cd build
cmake -G Ninja ..
ninja
ctest -j 8 --output-on-failure
#ninja install
