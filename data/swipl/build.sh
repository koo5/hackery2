#!/usr/bin/env bash

#
# git clone https://github.com/SWI-Prolog/swipl.git swipl
# cd swipl
#
# and then run this script.

set -x
set -e

git submodule update --init --recursive

cd packages/xpce
git remote add koo5 https://github.com/koo5/packages-xpce.git
git fetch koo5
git cherry-pick -n koo5/more_eye_friendly_gtrace_color_theme_squashed


cd ../..
mkdir build
cd build
cmake -G Ninja ..
ninja
ctest -j 8 --output-on-failure
ninja install
