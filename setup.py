#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
#
# Copyright (C) 2008 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn
# See README.txt for licensing information.

import os, re, sys

miscdeps=os.path.join(os.getcwd(), 'misc', 'dependencies')

try:
    from ez_setup import use_setuptools
except ImportError:
    pass
else:
    # On cygwin there was a permissions error that was fixed in 0.6c6.
    use_setuptools(min_version='0.6c6', download_delay=0, to_dir=miscdeps)

from setuptools import Extension, find_packages, setup

DEBUGMODE=("--debug" in sys.argv)

extra_compile_args=[]
extra_link_args=[]
define_macros=[]
undef_macros=[]
libraries=[]
ext_modules=[]
include_dirs=[]
library_dirs=[]

if DEBUGMODE:
    extra_compile_args.append("-O0")
    extra_compile_args.append("-g")
    extra_compile_args.append("-Wall")
    extra_link_args.append("-g")
    undef_macros.append('NDEBUG')

# Check for a directory starting with "/usr/include" or "/usr/local/include" and
# ending with "cryptopp" or "crypto++".

# This is because the upstream Crypto++ GNUmakefile and the Microsoft Visual
# Studio projects produce include directory and library named "cryptopp", but
# Debian (and hence Ubuntu, and a lot of other derivative distributions) changed
# that name to "crypto++".  In Debian package libcrypto++ version 5.5.2-1,
# 2007-12-11, they added symlinks from "cryptopp", so once everyone has upgraded
# past that version then we can eliminate this detection code.

# So this will very likely do what you want, but if it doesn't (perhaps because
# you have more than one version of Crypto++ installed it guessed wrong about
# which one you wanted to build against) and then you have to read this code and
# understand what it is doing.

for inclpath in ["/usr/local/include/cryptopp", "/usr/include/cryptopp", "/usr/include/crypto++", "/usr/local/include/crypto++", ]:
    if os.path.exists(inclpath):
        if inclpath.endswith("crypto++"):
            print "\"%s\" detected, so we will use the Debian name \"crypto++\" to identify the library instead of the upstream name \"cryptopp\"." % (inclpath,)
            define_macros.append(("USE_NAME_CRYPTO_PLUS_PLUS", True,))
            libraries.append("crypto++")
        else:
            libraries.append("cryptopp")
        incldir = os.path.dirname(inclpath)
        include_dirs.append(incldir)
        libdir = os.path.join(os.path.dirname(incldir), "lib")
        library_dirs.append(libdir)
        break

if not libraries:
    print "Did not locate libcrypto++ or libcryptopp in the usual places."
    print "Adding /usr/local/{include,lib} and -lcryptopp in the hopes"
    print "that they will work."

    # Note that when using cygwin build tools (including gcc) to build
    # Windows-native binaries, the os.path.exists() will not see the
    # /usr/local/include/cryptopp directory but the subsequent call to g++
    # will.
    libraries.append("cryptopp")
    include_dirs.append("/usr/local/include")
    library_dirs.append("/usr/local/lib")

trove_classifiers=[
    "Environment :: Console",
    "License :: OSI Approved :: GNU General Public License (GPL)", 
    "License :: DFSG approved",
    "License :: Other/Proprietary License",
    "Intended Audience :: Developers",
    "Operating System :: Microsoft",
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Operating System :: POSIX :: Linux",
    "Operating System :: POSIX",
    "Operating System :: MacOS :: MacOS X",
    "Operating System :: Microsoft :: Windows :: Windows NT/2000",
    "Operating System :: OS Independent",
    "Natural Language :: English",
    "Programming Language :: C",
    "Programming Language :: C++",
    "Programming Language :: Python",
    "Topic :: Software Development :: Libraries",
    ]

VERSIONFILE = "pycryptopp/_version.py"
verstr = "unknown"
VSRE = re.compile("^verstr = ['\"]([^'\"]*)['\"]", re.M)
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    mo = VSRE.search(verstrline)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("if %s.py exists, it is required to be well-formed" % (VERSIONFILE,))

ext_modules.append(
    Extension('pycryptopp.publickey.rsa', ['pycryptopp/publickey/rsamodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.hash.sha256', ['pycryptopp/hash/sha256module.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.cipher.aes', ['pycryptopp/cipher/aesmodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

dependency_links=[os.path.join(miscdeps, t) for t in os.listdir(miscdeps) if t.endswith(".tar")]
setup_requires = []

# darcsver is needed only if you want "./setup.py darcsver" to write a new
# version stamp in pycryptopp/_version.py, with a version number derived from
# darcs history.  http://pypi.python.org/pypi/darcsver
setup_requires.append('darcsver >= 1.0.0')

# setuptools_darcs is required only if you want to use "./setup.py sdist",
# "./setup.py bdist", and the other "dist" commands -- it is necessary for them
# to produce complete distributions, which need to include all files that are
# under darcs revision control.  http://pypi.python.org/pypi/setuptools_darcs
setup_requires.append('setuptools_darcs >= 1.0.5')

setup(name='pycryptopp',
      version=verstr,
      description='Python wrappers for the Crypto++ library',
      long_description='So far the only things it offers are RSA-PSS-SHA256 signatures, SHA-256 hashes, and AES-CTR with initial counter value of 0.',
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='http://allmydata.org/source/pycryptopp',
      license='GNU GPL',
      packages=find_packages(),
      include_package_data=True,
      setup_requires=setup_requires,
      dependency_links=dependency_links,
      classifiers=trove_classifiers,
      ext_modules=ext_modules,
      test_suite="pycryptopp.test",
      zip_safe=False, # I prefer unzipped for easier access.
      )
