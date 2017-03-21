#!/bin/bash -ex

# This runs in the container to actually build the wheels.
BUILDER="/io/misc/build_helpers/_build-wheels.sh"

# Create a scratch path where a bunch of intermediate build state can be
# dumped.
BASE="$(mktemp -d)"

# Put a virtualenv in there
ENV="${BASE}/env"
virtualenv "${ENV}"

# Create a directory where we can dump wheels that the build depends on.
WHEELHOUSE="${BASE}/wheelhouse"
mkdir -p "${WHEELHOUSE}"

# Helpers to run programs from the virtualenv - instead of "activating" it and
# changing what "pip" and "python" mean for everything in the script.
PYTHON="${ENV}/bin/python"
PIP="${ENV}/bin/pip"


# Get a new, good version of pip (who knows what version came with the
# virtualenv on the system?)
"${PIP}" install --upgrade pip

# Dump the requirements into a pip-readable format.
"${PYTHON}" setup.py egg_info

# Get wheels for all of the requirements and dump them into the directory we
# created for that purpose.
"${PIP}" wheel \
	 --requirement pycryptopp.egg-info/requires.txt \
	 --wheel-dir "${WHEELHOUSE}"

# This image can build x86_64 (64 bit) manylinux wheels.
DOCKER_IMAGE="quay.io/pypa/manylinux1_x86_64"
docker pull "${DOCKER_IMAGE}"

# Build all the x86_64 bit wheels.  Give this image access to our working
# directory (the root of the pycryptopp source tree).  Also give it access to
# the wheelhouse we populated with our requirements above.  Also give it no
# network access at all.  The image is (intentionally) full of super old
# software that's riddled with vulnerabilities.  Cutting it off from the
# network limits the attack surface to something a bit less terrifying.
docker run \
       --rm \
       --network none \
       --volume "${PWD}:/io" \
       --volume "${WHEELHOUSE}:/io/wheelhouse" \
       "${DOCKER_IMAGE}" \
       "${BUILDER}"

# As above, but for the i686 (32 bit) builds.
DOCKER_IMAGE="quay.io/pypa/manylinux1_i686"
docker pull "${DOCKER_IMAGE}"
docker run \
       --rm \
       --network none \
       --volume "${PWD}:/io" \
       --volume "${WHEELHOUSE}:/io/wheelhouse" \
       "${DOCKER_IMAGE}" \
       linux32 "${BUILDER}"

# Get the pycryptopp wheels from the place they were dumped.
mkdir -p wheelhouse
cp -v "${WHEELHOUSE}"/pycryptopp-*.whl wheelhouse/
sha256sum wheelhouse/*.whl
