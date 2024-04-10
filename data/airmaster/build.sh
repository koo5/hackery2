#!/usr/bin/env bash

clang++ -I/usr/include/c++/11 -I/usr/include/x86_64-linux-gnu/c++/11 -L /usr/lib/gcc/x86_64-linux-gnu/11  -Wall -o your_program_name test.cpp -lmosquitto
