#!/bin/bash -ex

# This runs in the container to actually build the wheels.
BUILDER="/io/misc/build_helpers/_build-wheels.sh"

# This image can build x86_64 (64 bit) manylinux wheels.
DOCKER_IMAGE="quay.io/pypa/manylinux1_x86_64"
docker pull "${DOCKER_IMAGE}"
docker run --rm -v "${PWD}:/io" "${DOCKER_IMAGE}" "${BUILDER}"

# This image can build i686 (32 bit) manylinux wheels.
DOCKER_IMAGE="quay.io/pypa/manylinux1_i686"
docker pull "${DOCKER_IMAGE}"
docker run --rm -v "${PWD}:/io" "${DOCKER_IMAGE}" linux32 "${BUILDER}"

# Show the user what they built.
ls wheelhouse
