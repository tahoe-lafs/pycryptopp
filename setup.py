#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
# 
# Copyright (C) 2007 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn

import os, sys
from ez_setup import use_setuptools
if 'cygwin' in sys.platform.lower():
    min_version='0.6c6'
else:
    min_version='0.6a9'
use_setuptools(min_version=min_version, download_delay=0)

from setuptools import Extension, find_packages, setup

DEBUGMODE=False
# DEBUGMODE=True

extra_compile_args=[]
extra_link_args=[]
define_macros=[]
undef_macros=[]
libraries=[]
ext_modules=[]

if DEBUGMODE:
    extra_compile_args.append("-O0")
    extra_compile_args.append("-g")
    extra_compile_args.append("-Wall")
    extra_link_args.append("-g")
    undef_macros.append('NDEBUG')

# Check for the existence of "/usr/include/crypto++/rsa.h", and if it is
# present, pass #define "USE_NAME_CRYPTO_PLUS_PLUS" to the C++ compiler, and
# tell the C++ compiler to link to an extra library named "crypto++".

# This is because the upstream Crypto++ GNUmakefile and the Microsoft Visual
# Studio projects produce include directory and library named "cryptopp", but
# Debian (and hence Ubuntu, and a lot of other derivative distributions)
# changed that name to "crypto++".

# So this will very likely do what you want, unless what you want is to ignore
# an extant install of Crypto++ which has include files in
# /usr/include/crypto++, and instead include and link to a specific install of
# Crypto++ which is named "cryptopp", in which case you'll have to remove the
# /usr/include/crypto++ or edit this setup.py file.
checkincldir = os.path.join("/", "usr", "include", "crypto++")
if os.path.exists(checkincldir):
    print "%s detected, so we will use the Debian name \"crypto++\" to identify the library instead of the upstream name \"cryptopp\"." % (checkincldir,)
    define_macros.append(("USE_NAME_CRYPTO_PLUS_PLUS", True,))
    libraries.append("crypto++")
else:
    libraries.append("cryptopp")

trove_classifiers=[
    "Environment :: Console",
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
# XXX ADD SOME 
    ]

try:
    import os
    os.system("darcsver")
except Exception, le:
    pass
import re
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
    Extension('pycryptopp.publickey._rsa', ['pycryptopp/publickey/_rsamodule.cpp',], libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

setup(name='pycryptopp',
      # install_requires=['something>=1.0.0',],
      version=verstr,
      # XXXdescription='a fast erasure code with command-line, C, and Python interfaces',
      # XXXlong_description='Fast, portable, programmable erasure coding a.k.a. "forward error correction": the generation of redundant blocks of information such that if some blocks are lost then the original data can be recovered from the remaining blocks.',
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='http://allmydata.org/source/zfec',
      # XXXlicense='GNU GPL',
      packages=find_packages(),
      classifiers=trove_classifiers,
      # XXXentry_points = { 'console_scripts': [ 'zfec = zfec.cmdline_zfec:main', 'zunfec = zfec.cmdline_zunfec:main' ] },
      ext_modules=ext_modules,
      test_suite="pycryptopp.test",
      zip_safe=False, # I prefer unzipped for easier access.
      dependency_links=["setuptools-0.6c7-py2.5.egg",],
      )
