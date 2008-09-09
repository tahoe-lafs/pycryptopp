#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
#
# Copyright (C) 2008 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn
# See README.txt for licensing information.

import os, platform, re, subprocess, sys

try:
    from ez_setup import use_setuptools
except ImportError:
    pass
else:
    # On cygwin there was a permissions error that was fixed in 0.6c6.
    use_setuptools(min_version='0.6c6')

from setuptools import Extension, find_packages, setup

CRYPTOPPDIR=os.path.join('cryptopp', 'c5')

extra_compile_args=[]
extra_link_args=[]
define_macros=[]
undef_macros=[]
libraries=[]
ext_modules=[]
include_dirs=[CRYPTOPPDIR]
library_dirs=[]

# Versions of GNU assembler older than 2.10 do not understand the kind of ASM that Crypto++ uses.
sp = subprocess.Popen(['as', '-v'], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)
sp.stdin.close()
sp.wait()
if re.search("GNU assembler version (0|1|2.0)", sp.stderr.read()):
    define_macros.append(('CRYPTOPP_DISABLE_ASM', 1))

if 'sunos' in platform.system().lower():
    extra_compile_args.append('-Wa,--divide') # allow use of "/" operator

cryptopp_src = [ os.path.join(CRYPTOPPDIR, x) for x in os.listdir(CRYPTOPPDIR) if x.endswith('.cpp') ]

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
try:
    verstrline = open(VERSIONFILE, "rt").read()
except EnvironmentError:
    pass # Okay, there is no version file.
else:
    VSRE = r"^verstr = ['\"]([^'\"]*)['\"]"
    mo = re.search(VSRE, verstrline, re.M)
    if mo:
        verstr = mo.group(1)
    else:
        print "unable to find version in %s" % (VERSIONFILE,)
        raise RuntimeError("if %s.py exists, it is required to be well-formed" % (VERSIONFILE,))

ext_modules.append(
    Extension('pycryptopp.publickey.rsa', cryptopp_src + ['pycryptopp/publickey/rsamodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.publickey.ecdsa', cryptopp_src + ['pycryptopp/publickey/ecdsamodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.hash.sha256', cryptopp_src + ['pycryptopp/hash/sha256module.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.cipher.aes', cryptopp_src + ['pycryptopp/cipher/aesmodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

miscdeps=os.path.join(os.getcwd(), 'misc', 'dependencies')
dependency_links=[os.path.join(miscdeps, t) for t in os.listdir(miscdeps) if t.endswith(".tar")]
setup_requires = []
install_requires = ['setuptools >= 0.6a9'] # for pkg_resources for loading test vectors for unit tests

# darcsver is needed only if you want "./setup.py darcsver" to write a new
# version stamp in pycryptopp/_version.py, with a version number derived from
# darcs history.  http://pypi.python.org/pypi/darcsver
if 'darcsver' in sys.argv[1:]:
    setup_requires.append('darcsver >= 1.0.0')

# setuptools_pyflakes is needed only if you want "./setup.py flakes" to run
# pyflakes on all the pycryptopp modules.
if 'flakes' in sys.argv[1:]:
    setup_requires.append('setuptools_pyflakes >= 1.0.0')

# setuptools_darcs is required to produce complete distributions (such as
# with "sdist" or "bdist_egg"), unless there is a 
# pycryptopp.egg-info/SOURCES.txt file present which contains a complete list 
# of needed files.
# http://pypi.python.org/pypi/setuptools_darcs
setup_requires.append('setuptools_darcs >= 1.0.5')

data_fnames=['COPYING.GPL', 'COPYING.TGPPL.html', 'README.txt']
# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/python-pycryptopp".
doc_loc = "share/doc/python-pycryptopp"
data_files = [(doc_loc, data_fnames)]

def _setup(test_suite):
    setup(name='pycryptopp',
          version=verstr,
          description='Python wrappers for the Crypto++ library',
          long_description='RSA-PSS-SHA256 signatures, ECDSA(1363)/EMSA1(SHA-256) signatures, SHA-256 hashes, and AES-CTR encryption',
          author='Zooko O\'Whielacronx',
          author_email='zooko@zooko.com',
          url='http://allmydata.org/trac/pycryptopp',
          license='GNU GPL',
          packages=find_packages(),
          include_package_data=True,
          data_files=data_files,
          setup_requires=setup_requires,
          install_requires=install_requires,
          dependency_links=dependency_links,
          classifiers=trove_classifiers,
          ext_modules=ext_modules,
          test_suite=test_suite,
          zip_safe=False, # I prefer unzipped for easier access.
          )

try:
    _setup(test_suite="pycryptopp.test")
except Exception, le:
    # to work around a bug in Elisa
    if "test_suite must be a list" in str(le):
        _setup(test_suite=["pycryptopp.test"])
