#!/bin/bash

c++ -O3 -Wall -shared -std=c++11 -fPIC $(python3 -m pybind11 --includes) count_conflicts.cpp -o count_conflicts_cpp$(python3-config --extension-suffix)