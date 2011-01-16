#!/usr/bin/env python

# pycryptopp -- Python wrappers for Crypto++
#
# Copyright (C) 2009-2010 Zooko Wilcox-O'Hearn
# Author: Zooko Wilcox-O'Hearn
# See README.txt for licensing information.

import glob, os, platform, re, subprocess, sys

egg = os.path.realpath(glob.glob('darcsver-*.egg')[0])
sys.path.insert(0, egg)

from setuptools import Extension, find_packages, setup

# ECDSA=False
ECDSA=True

DEBUG=False
if "--debug" in sys.argv:
    DEBUG=True
    sys.argv.remove("--debug")

DISABLE_EMBEDDED_CRYPTOPP=False
if "--disable-embedded-cryptopp" in sys.argv:
    DISABLE_EMBEDDED_CRYPTOPP=True
    sys.argv.remove("--disable-embedded-cryptopp")

# Unfortunately stdeb v0.3 doesn't seem to offer a way to pass command-line
# arguments to setup.py when building for Debian, but it does offer a way to
# pass environment variables, so we here check for that in addition to the
# command-line argument check above.
if os.environ.get('PYCRYPTOPP_DISABLE_EMBEDDED_CRYPTOPP') == "1":
    DISABLE_EMBEDDED_CRYPTOPP=True

EMBEDDED_CRYPTOPP_DIR='embeddedcryptopp'

TEST_DOUBLE_LOAD=False
if "--test-double-load" in sys.argv:
    TEST_DOUBLE_LOAD=True
    sys.argv.remove("--test-double-load")

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

#
# Fix the build on OpenBSD
# http://tahoe-lafs/trac/pycryptopp/ticket/32
#
if 'openbsd' in platform.system().lower():
    extra_link_args.append("-fpic")

if DEBUG:
    extra_compile_args.append("-O0")
    extra_compile_args.append("-g")
    extra_compile_args.append("-Wall")
    extra_link_args.append("-g")
    undef_macros.append('NDEBUG')
else:
    extra_compile_args.append("-w")

if DISABLE_EMBEDDED_CRYPTOPP:
    define_macros.append(('DISABLE_EMBEDDED_CRYPTOPP', 1))

    # Link with a Crypto++ library that is already installed on the system.

    for inclpath in ["/usr/local/include/cryptopp", "/usr/include/cryptopp"]:
        if os.path.exists(inclpath):
            libraries.append("cryptopp")
            incldir = os.path.dirname(inclpath)
            include_dirs.append(incldir)
            libdir = os.path.join(os.path.dirname(incldir), "lib")
            library_dirs.append(libdir)
            break

    if not libraries:
        print "Did not locate libcryptopp in the usual places."
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
    # Build the bundled Crypto++ library which is included by source
    # code in the pycryptopp tree and link against it.
    include_dirs.append(".")

    if 'sunos' in platform.system().lower():
        extra_compile_args.append('-Wa,--divide') # allow use of "/" operator

    if 'win32' in sys.platform.lower():
        try:
            res = subprocess.Popen(['cl'], stdin=open(os.devnull), stdout=subprocess.PIPE).communicate()
        except EnvironmentError, le:
            # Okay I guess we're not using the "cl.exe" compiler.
            using_msvc = False
        else:
            using_msvc = True
    else:
        using_msvc = False

    if using_msvc:
        # We can handle out-of-line assembly.
        cryptopp_src = [ os.path.join(EMBEDDED_CRYPTOPP_DIR, x) for x in os.listdir(EMBEDDED_CRYPTOPP_DIR) if x.endswith(('.cpp', '.asm')) ]
    else:
        # We can't handle out-of-line assembly.
        cryptopp_src = [ os.path.join(EMBEDDED_CRYPTOPP_DIR, x) for x in os.listdir(EMBEDDED_CRYPTOPP_DIR) if x.endswith('.cpp') ]

    # Mac OS X extended attribute files when written to a non-Mac-OS-X
    # filesystem come out as "._$FNAME", for example "._rdtables.cpp",
    # and those files contain uncompilable data that is not C++, thus
    # on occasion causing the build to fail. This works-around that:
    cryptopp_src = [ c for c in cryptopp_src if not os.path.basename(c).startswith('._') ]

    extra_srcs.extend(cryptopp_src)

# In either case, we must provide a value for CRYPTOPP_DISABLE_ASM that
# matches the one used when Crypto++ was originally compiled. The Crypto++
# GNUmakefile tests the assembler version and only enables assembly for
# recent versions of the GNU assembler (2.10 or later). The /usr/bin/as on
# Mac OS-X 10.6 is too old.

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
else:
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
    "Operating System :: Microsoft :: Windows",
    "Operating System :: Unix",
    "Operating System :: MacOS :: MacOS X",
    "Natural Language :: English",
    "Programming Language :: C",
    "Programming Language :: C++",
    "Programming Language :: Python",
    "Programming Language :: Python :: 2",
    "Programming Language :: Python :: 2.4",
    "Programming Language :: Python :: 2.5",
    "Programming Language :: Python :: 2.6",
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

srcs = ['pycryptopp/_pycryptoppmodule.cpp', 'pycryptopp/publickey/rsamodule.cpp', 'pycryptopp/hash/sha256module.cpp', 'pycryptopp/cipher/aesmodule.cpp']
if ECDSA:
    srcs.append('pycryptopp/publickey/ecdsamodule.cpp')
if TEST_DOUBLE_LOAD:
    srcs.append('_testdoubleloadmodule.cpp', )

ext_modules.append(
    Extension('pycryptopp._pycryptopp', extra_srcs + srcs, include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

if TEST_DOUBLE_LOAD:
    ext_modules.append(
        Extension('_testdoubleload', extra_srcs + srcs, include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
        )

miscdeps=os.path.join(os.getcwd(), 'misc', 'dependencies')
dependency_links=[os.path.join(miscdeps, t) for t in os.listdir(miscdeps) if t.endswith(".tar")]
setup_requires = []
install_requires = ['setuptools >= 0.6a9'] # for pkg_resources for loading test vectors for unit tests

# The darcsver command from the darcsver plugin is needed to initialize the
# distribution's .version attribute. (It does this either by examining darcs
# history, or if that fails by reading the pycryptopp/_version.py
# file). darcsver will also write a new version stamp in
# pycryptopp/_version.py, with a version number derived from darcs
# history. Note that the setup.cfg file has an "[aliases]" section which
# enumerates commands that you might run and specifies that it will run
# darcsver before each one. If you add different commands (or if I forgot some
# that are already in use), you may need to add it to setup.cfg and configure
# it to run darcsver before your command, if you want the version number to be
# correct when that command runs.  http://pypi.python.org/pypi/darcsver
setup_requires.append('darcsver >= 1.6.3')

# setuptools_pyflakes is needed only if you want "./setup.py flakes" to run
# pyflakes on all the pycryptopp modules.
if 'flakes' in sys.argv[1:]:
    setup_requires.append('setuptools_pyflakes >= 1.0.0')

# setuptools_darcs is required to produce complete distributions (such
# as with "sdist" or "bdist_egg"), unless there is a
# pycryptopp.egg-info/SOURCE.txt file present which contains a complete
# list of files that should be included.
# http://pypi.python.org/pypi/setuptools_darcs However, requiring it
# runs afoul of a bug in Distribute, which was shipped in Ubuntu
# Lucid, so for now you have to manually install it before building
# sdists or eggs:
# http://bitbucket.org/tarek/distribute/issue/55/revision-control-plugin-automatically-installed-as-a-build-dependency-is-not-present-when-another-build-dependency-is-being
if False:
    setup_requires.append('setuptools_darcs >= 1.1.0')

# stdeb is required to produce Debian files with "sdist_dsc".
# http://github.com/astraw/stdeb/tree/master
if "sdist_dsc" in sys.argv:
    setup_requires.append('stdeb')

data_fnames=['COPYING.GPL', 'COPYING.TGPPL.html', 'README.txt']

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/pycryptopp".
doc_loc = "share/doc/" + PKG
data_files = [(doc_loc, data_fnames)]

# Note that due to a bug in distutils we also have to maintain a
# MANIFEST.in file specifying embeddedcryptopp/extraversion.h. This bug was
# fixed in Python 2.7
data_files.append((EMBEDDED_CRYPTOPP_DIR, [EMBEDDED_CRYPTOPP_DIR+'/extraversion.h']))

if ECDSA:
    long_description='RSA-PSS-SHA256 signatures, ECDSA(1363)/EMSA1(SHA-256) signatures, SHA-256 hashes, and AES-CTR encryption'
else:
    long_description='RSA-PSS-SHA256 signatures, SHA-256 hashes, and AES-CTR encryption'

PY_VERSION_BODY='''
# This is the version of this tree, as created by %(versiontool)s from the darcs patch
# information: the main version number is taken from the most recent release
# tag. If some patches have been added since the last release, this will have a
# -NN "build number" suffix, or else a -rNN "revision number" suffix. Please see
# pyutil.version_class for a description of what the different fields mean.

__pkgname__ = "%(pkgname)s"
verstr = "%(pkgversion)s"
try:
    from pyutil.version_class import Version as pyutil_Version
    __version__ = pyutil_Version(verstr)
except (ImportError, ValueError):
    # Maybe there is no pyutil installed, or this may be an older version of
    # pyutil.version_class which does not support SVN-alike revision numbers.
    from distutils.version import LooseVersion as distutils_Version
    __version__ = distutils_Version(verstr)
'''

CPP_VERSION_BODY='''
/* This is the version of this tree, as created by %(versiontool)s from the darcs patch
 * information: the main version number is taken from the most recent release
 * tag. If some patches have been added since the last release, this will have a
 * -NN "build number" suffix, or else a -rNN "revision number" suffix. Please see
 * pyutil.version_class for a description of what the different fields mean.
 */

#define CRYPTOPP_EXTRA_VERSION "%(pkgname)s-%(pkgversion)s"
'''

setup(name=PKG,
      version=verstr,
      description='Python wrappers for a few algorithms from the Crypto++ library',
      long_description=long_description,
      author='Zooko O\'Whielacronx',
      author_email='zooko@zooko.com',
      url='http://tahoe-lafs.org/trac/' + PKG,
      license='GNU GPL', # see README.txt for details -- there is also an alternative licence
      packages=find_packages(),
      include_package_data=True,
      exclude_package_data={
          '': [ '*.cpp', '*.hpp', ]
          },
      data_files=data_files,
      setup_requires=setup_requires,
      install_requires=install_requires,
      dependency_links=dependency_links,
      classifiers=trove_classifiers,
      ext_modules=ext_modules,
      test_suite=PKG+".test",
      zip_safe=False, # I prefer unzipped for easier access.
      versionfiles=[os.path.join('pycryptopp', '_version.py'), os.path.join(EMBEDDED_CRYPTOPP_DIR, 'extraversion.h')],
      versionbodies=[PY_VERSION_BODY, CPP_VERSION_BODY],
      )
