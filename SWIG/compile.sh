#!/bin/sh

swig -c++ -python -py3 -o KikiPy_wrap.cpp KikiPy.i
cp kiki.py ../py
