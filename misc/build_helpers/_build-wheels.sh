#!/bin/bash

# Based on https://github.com/pypa/python-manylinux-demo

set -e -x

# Compile wheels
for PYBIN in /opt/python/cp2*/bin; do
    "${PYBIN}/pip" wheel /io/ -w /wheelhouse/
done

# Bundle external shared libraries into the wheels and write them to their
# final location.
for whl in /wheelhouse/pycrypto-*.whl; do
    auditwheel repair "$whl" -w /io/wheelhouse/
done
