#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
# 
# Copyright (C) 2007 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn

from ez_setup import use_setuptools
import sys
if 'cygwin' in sys.platform.lower():
    min_version='0.6c6'
else:
    min_version='0.6a9'
use_setuptools(min_version=min_version, download_delay=0)

from setuptools import Extension, find_packages, setup
# from distutils.core import Extension, setup
# def find_packages():
#     return ["pycryptopp",]

DEBUGMODE=False
# DEBUGMODE=True

extra_compile_args=[]
extra_link_args=[]

undef_macros=[]

if DEBUGMODE:
    extra_compile_args.append("-O0")
    extra_compile_args.append("-g")
    extra_compile_args.append("-Wall")
    extra_link_args.append("-g")
    undef_macros.append('NDEBUG')

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
      ext_modules=[Extension('_pycryptopp', ['pycryptopp/_pycryptoppmodule.cpp',], libraries=["cryptopp",], extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, undef_macros=undef_macros),],
      test_suite="pycryptopp.test", # XXX
      zip_safe=False, # I prefer unzipped for easier access.
      )
