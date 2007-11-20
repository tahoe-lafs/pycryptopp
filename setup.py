#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
#
# Copyright (C) 2007 Allmydata, Inc.
# Author: Zooko Wilcox-O'Hearn

import os, sys
# try:
#     from ez_setup import use_setuptools
# except ImportError:
#     pass
# else:
#     if 'cygwin' in sys.platform.lower():
#         min_version='0.6c6'
#     else:
#         min_version='0.6a9'
#     use_setuptools(min_version=min_version, download_delay=0)

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

# Check for a directory starting with "/usr/include" or "/usr/local/include"
# and ending with "cryptopp" or "crypto++".

# This is because the upstream Crypto++ GNUmakefile and the Microsoft Visual
# Studio projects produce include directory and library named "cryptopp", but
# Debian (and hence Ubuntu, and a lot of other derivative distributions)
# changed that name to "crypto++".  This changed in Debian package of
# libcrypto++ version 5.5-5, 2007-11-11, so once everyone has upgraded past
# that version then we can eliminate this detection code.

# So this will very likely do what you want, but if it doesn't (because you
# have more than one version of Crypto++ installed it guessed wrong about which
# one you wanted to build against) and then you have to read this code and
# understand what it is doing.

for inclpath in [ "/usr/include/crypto++", "/usr/local/include/cryptopp", "/usr/include/cryptopp", "/usr/local/include/crypto++", ]:
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

try:
    import os
    (cin, cout, cerr,)= os.popen3("darcsver")
    print cout.read()
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
    Extension('pycryptopp.publickey._rsa', ['pycryptopp/publickey/_rsamodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.hash._sha256', ['pycryptopp/hash/_sha256module.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

ext_modules.append(
    Extension('pycryptopp.cipher._aes', ['pycryptopp/cipher/_aesmodule.cpp',], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

setup(name='pycryptopp',
      version=verstr,
      description='Python wrappers for the Crypto++ library',
      long_description='So far the only things it offers are RSA-PSS-SHA256 signatures and SHA-256 hashes.',
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='http://allmydata.org/source/pycryptopp',
      license='Open Software License 3.0 --  http://www.opensource.org/licenses/osl-3.0.php',
      packages=find_packages(),
      include_package_data=True,
      # setup_requires=['setuptools_darcs >= 1.0.5',],
      classifiers=trove_classifiers,
      ext_modules=ext_modules,
      test_suite="pycryptopp.test",
      zip_safe=False, # I prefer unzipped for easier access.
      dependency_links=["setuptools-0.6c7-py2.5.egg",],
      )
