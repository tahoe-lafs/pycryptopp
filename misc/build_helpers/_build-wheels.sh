#!/bin/bash

# Copied straight from https://github.com/pypa/python-manylinux-demo

set -e -x

# Compile wheels
for PYBIN in /opt/python/cp2*/bin; do
    "${PYBIN}/pip" wheel /io/ -w /io/wheelhouse/
done
