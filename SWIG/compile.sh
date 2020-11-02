#!/bin/sh

swig -c++ -python -py3 -globals kiki -o KikiPy_wrap.cpp KikiPy.i
cp kiki.py ../py
