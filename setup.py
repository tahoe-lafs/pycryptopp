#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
#
# Copyright (C) 2008 Allmydata, Inc.
# Copyright (C) 2009 Zooko Wilcox-O'Hearn
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

DEBUG=False
if "--debug" in sys.argv:
    DEBUG=True
    sys.argv.remove("--debug")

DISABLE_EMBEDDED_CRYPTOPP=False
if "--disable-embedded-cryptopp" in sys.argv:
    DISABLE_EMBEDDED_CRYPTOPP=True
    sys.argv.remove("--disable-embedded-cryptopp")

# There are two ways that this setup.py script can build pycryptopp, either by using the
# Crypto++ source code bundled in the pycryptopp source tree, or by linking to a copy of the
# Crypto++ library that is already installed on the system.

extra_compile_args=[]
extra_link_args=[]
define_macros=[]
undef_macros=[]
libraries=[]
ext_modules=[]
include_dirs=[]
library_dirs=[]
extra_srcs=[] # This is for Crypto++ .cpp files if they are needed.

if DEBUG:
    extra_compile_args.append("-O0")
    extra_compile_args.append("-g")
    extra_compile_args.append("-Wall")
    extra_link_args.append("-g")
    undef_macros.append('NDEBUG')
else:
    extra_compile_args.append("-w")

if DISABLE_EMBEDDED_CRYPTOPP:
    # Link with a Crypto++ library that is already installed on the system.

    # Check for a directory starting with "/usr/include" or "/usr/local/include" and
    # ending with "cryptopp" or "crypto++".

    # This is because the upstream Crypto++ GNUmakefile and the Microsoft Visual
    # Studio projects produce include directory and library named "cryptopp", but
    # Debian (and hence Ubuntu, and a lot of other derivative distributions) changed
    # that name to "crypto++".  In Debian package libcrypto++ version 5.5.2-1,
    # 2007-12-11, they added symlinks from "cryptopp", so once everyone has upgraded
    # past that version then we can eliminate this detection code.

    # So this will very likely do what you want, but if it doesn't (perhaps because
    # you have more than one version of Crypto++ installed and it guessed wrong
    # about which one you wanted to build against) and then you have to read this
    # code and understand what it is doing.

    for inclpath in ["/usr/include/crypto++", "/usr/local/include/crypto++", "/usr/local/include/cryptopp", "/usr/include/cryptopp"]:
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

else:
    # Build the Crypto++ library which is included by source code in the pycryptopp tree and
    # link against it.
    CRYPTOPPDIR=os.path.join('cryptopp')
    include_dirs.append(".")

    if 'sunos' in platform.system().lower():
        extra_compile_args.append('-Wa,--divide') # allow use of "/" operator

    # pycryptopp provides access to a very limited subset of libcrypto++.
    # These are the source files that we actually need to compile.
    used_cpp_files = ["sha.cpp", "rsa.cpp", "rijndael.cpp",
                      "pubkey.cpp", "eccrypto.cpp", "dsa.cpp", "cryptlib.cpp",
                      "iterhash.cpp", "asn.cpp", "queue.cpp", "filters.cpp",
                      "ecp.cpp", "algebra.cpp",
                      "dll.cpp", "oaep.cpp", "gfpcrypt.cpp",
                      "modes.cpp", "hmac.cpp", "randpool.cpp", "pssr.cpp",
                      "hrtimer.cpp", "hex.cpp", "basecode.cpp", "cpu.cpp",
                      "integer.cpp", "pkcspad.cpp", "gf2n.cpp", "algparam.cpp",
                      "rdtables.cpp", "ec2n.cpp",
                      "tiger.cpp", "tigertab.cpp", "fips140.cpp", "misc.cpp",
                      "nbtheory.cpp", "osrng.cpp", "rng.cpp", "mqueue.cpp",
                      # on windows, when NDEBUG is off, modes.cpp requires DES
                      "des.cpp", "dessp.cpp",
                      ]
    used_cpp_files.sort()

    cryptopp_src = [ os.path.join(CRYPTOPPDIR, x) for x in used_cpp_files ]
    extra_srcs.extend(cryptopp_src)

# In either case, we must provide a value for CRYPTOPP_DISABLE_ASM that
# matches the one used when Crypto++ was originally compiled. The Crypto++
# GNUMakefile tests the assembler version and only enables assembly for
# recent versions of the GNU assembler (2.10 or later). The /usr/bin/as on
# Mac OS-X 10.5 is too old (

try:
    sp = subprocess.Popen(['as', '-v'], stdin=subprocess.PIPE,
                          stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                          universal_newlines=True)
    sp.stdin.close()
    sp.wait()
    if re.search("GNU assembler version (0|1|2.0)", sp.stderr.read()):
        define_macros.append(('CRYPTOPP_DISABLE_ASM', 1))
except EnvironmentError:
    # Okay, nevermind. Maybe there isn't even an 'as' executable on this
    # platform.
    pass

try:
    # that "as -v" step creates an empty a.out, so clean it up. Modern GNU
    # "as" has --version, which emits the version number without actually
    # assembling anything, but older versions only have -v, which emits a
    # version number and *then* assembles from stdin.
    os.unlink("a.out")
except EnvironmentError:
    pass

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
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Topic :: Software Development :: Libraries",
    ]

PKG='pycryptopp'
VERSIONFILE = os.path.join(PKG, "_version.py")
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
    Extension('pycryptopp._pycryptopp', extra_srcs + ['pycryptopp/_pycryptoppmodule.cpp', 'pycryptopp/publickey/ecdsamodule.cpp', 'pycryptopp/publickey/rsamodule.cpp', 'pycryptopp/hash/sha256module.cpp', 'pycryptopp/cipher/aesmodule.cpp'], include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

miscdeps=os.path.join(os.getcwd(), 'misc', 'dependencies')
dependency_links=[os.path.join(miscdeps, t) for t in os.listdir(miscdeps) if t.endswith(".tar")]
setup_requires = []
install_requires = ['setuptools >= 0.6a9'] # for pkg_resources for loading test vectors for unit tests

# The darcsver command from the darcsver plugin is needed to initialize the
# distribution's .version attribute correctly. (It does this either by
# examining darcs history, or if that fails by reading the
# pycryptopp/_version.py file). darcsver will also write a new version
# stamp in pycryptopp/_version.py, with a version number derived from
# darcs history. Note that the setup.cfg file has an "[aliases]" section
# which enumerates commands that you might run and specifies that it will run
# darcsver before each one. If you add different commands (or if I forgot
# some that are already in use), you may need to add it to setup.cfg and
# configure it to run darcsver before your command, if you want the version
# number to be correct when that command runs.
# http://pypi.python.org/pypi/darcsver
setup_requires.append('darcsver >= 1.2.0')

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
doc_loc = "share/doc/python-" + PKG
data_files = [(doc_loc, data_fnames)]

def _setup(test_suite):
    setup(name=PKG,
          version=verstr,
          description='Python wrappers for the Crypto++ library',
          long_description='RSA-PSS-SHA256 signatures, ECDSA(1363)/EMSA1(SHA-256) signatures, SHA-256 hashes, and AES-CTR encryption',
          author='Zooko O\'Whielacronx',
          author_email='zooko@zooko.com',
          url='http://allmydata.org/trac/' + PKG,
          license='GNU GPL',
          packages=find_packages(),
          include_package_data=True,
          exclude_package_data = { '': [ '*.cpp' ] },
          data_files=data_files,
          setup_requires=setup_requires,
          install_requires=install_requires,
          dependency_links=dependency_links,
          classifiers=trove_classifiers,
          ext_modules=ext_modules,
          test_suite=test_suite,
          zip_safe=False, # I prefer unzipped for easier access.
          )

test_suite_name=PKG+".test"
try:
    _setup(test_suite=test_suite_name)
except Exception, le:
    # to work around a bug in Elisa v0.3.5
    # https://bugs.launchpad.net/elisa/+bug/263697
    if "test_suite must be a list" in str(le):
        _setup(test_suite=[test_suite_name])
    else:
        raise
