#!/usr/bin/env python
# -*- coding: utf-8 -*-

# pycryptopp -- Python wrappers for a few algorithms from Crypto++
#
# Copyright © 2009-2012 Zooko Wilcox-O'Hearn
# Author: Zooko Wilcox-O'Hearn
#
# See README.rst for licensing information.

import os, platform, re, subprocess, sys

from setuptools import Extension, setup
from setuptools import Command
from distutils.util import get_platform
from setuptools.command.test import ScanningLoader
import unittest

import versioneer
versioneer.versionfile_source = "src/pycryptopp/_version.py"
versioneer.versionfile_build = "pycryptopp/_version.py"
versioneer.tag_prefix = "pycryptopp-"
versioneer.parentdir_prefix = "pycryptopp-"

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

BUILD_DOUBLE_LOAD_TESTER=False
BDLTARG="--build-double-load-tester"
if BDLTARG in sys.argv:
    BUILD_DOUBLE_LOAD_TESTER=True
    sys.argv.remove(BDLTARG)

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
    "License :: OSI Approved :: GNU General Public License (GPL)", # See README.rst for alternative licensing.
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

srcs = ['src/pycryptopp/_pycryptoppmodule.cpp',
        'src/pycryptopp/publickey/rsamodule.cpp',
        'src/pycryptopp/hash/sha256module.cpp',
        'src/pycryptopp/cipher/aesmodule.cpp',
        'src/pycryptopp/cipher/xsalsa20module.cpp',
        ]
if ECDSA:
    srcs.append('src/pycryptopp/publickey/ecdsamodule.cpp')
if BUILD_DOUBLE_LOAD_TESTER:
    srcs.append('_doubleloadtester.cpp', )

ext_modules.append(
    Extension('pycryptopp._pycryptopp', extra_srcs + srcs, include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
    )

# python-ed25519
sources = [os.path.join("src-ed25519","glue","ed25519module.c")]
sources.extend([os.path.join("src-ed25519","supercop-ref",s)
                for s in os.listdir(os.path.join("src-ed25519","supercop-ref"))
                if s.endswith(".c") and s!="test.c"])
m = Extension("pycryptopp.publickey.ed25519._ed25519",
              include_dirs=[os.path.join("src-ed25519","supercop-ref")],
              sources=sources)
ext_modules.append(m)


if BUILD_DOUBLE_LOAD_TESTER:
    ext_modules.append(
        Extension('_doubleloadtester', extra_srcs + srcs, include_dirs=include_dirs, library_dirs=library_dirs, libraries=libraries, extra_link_args=extra_link_args, extra_compile_args=extra_compile_args, define_macros=define_macros, undef_macros=undef_macros)
        )

miscdeps=os.path.join(os.getcwd(), 'misc', 'dependencies')
dependency_links=[os.path.join(miscdeps, t) for t in os.listdir(miscdeps) if t.endswith(".tar")]
setup_requires = []
install_requires = ['setuptools >= 0.6a9'] # for pkg_resources for loading test vectors for unit tests

# setuptools_pyflakes is needed only if you want "./setup.py flakes" to run
# pyflakes on all the pycryptopp modules.
if 'flakes' in sys.argv[1:]:
    setup_requires.append('setuptools_pyflakes >= 1.0.0')

# stdeb is required to produce Debian files with "sdist_dsc".
# http://github.com/astraw/stdeb/tree/master
if "sdist_dsc" in sys.argv:
    setup_requires.append('stdeb')

data_fnames=['COPYING.GPL', 'COPYING.TGPPL.html', 'README.rst']

readmetext = open('README.rst').read()

# In case we are building for a .deb with stdeb's sdist_dsc command, we put the
# docs in "share/doc/pycryptopp".
doc_loc = "share/doc/" + PKG
data_files = [(doc_loc, data_fnames)]

commands = versioneer.get_cmdclass().copy()

###### Version updating code

CPP_GIT_VERSION_BODY = '''
/* This _version.py is generated from git metadata by the pycryptopp
 * setup.py. The main version number is taken from the most recent release
 * tag. If some patches have been added since the last release, this will
 * have a -NN "build number" suffix, or else a -rNN "revision number" suffix.
 */

#define CRYPTOPP_EXTRA_VERSION "%(pkgname)s-%(normalized)s"
'''

def get_normalized_version():
    pieces = versioneer.get_versions()["version"].split("-")
    if len(pieces) == 1:
        normalized_version = pieces[0]
    else:
        normalized_version = "%s.post%s" % (pieces[0], pieces[1])
    if pieces[-1] == "dirty":
        normalized_version += ".dev0"
    return normalized_version


class UpdateVersion(Command):
    description = "update extraversion.h from revision-control metadata"
    user_options = []

    def initialize_options(self):
        pass
    def finalize_options(self):
        pass
    def run(self):
        versions = versioneer.get_versions()
        fn = os.path.join(EMBEDDED_CRYPTOPP_DIR, 'extraversion.h')
        f = open(fn, "wb")
        BODY = CPP_GIT_VERSION_BODY
        f.write(BODY %
                { "pkgname": self.distribution.get_name(),
                  "version": versions["version"],
                  "normalized": get_normalized_version(),
                  "full": versions["full"] })
        f.close()
        print "git-version: wrote '%s' into '%s'" % (versions["version"], fn)
commands["update_version"] = UpdateVersion

class Test(Command):
    description = "run tests"
    user_options = []
    def initialize_options(self):
        self.test_suite = None
    def finalize_options(self):
        if self.test_suite is None:
            self.test_suite = self.distribution.test_suite
    def setup_path(self):
        # copied from distutils/command/build.py
        self.plat_name = get_platform()
        plat_specifier = ".%s-%s" % (self.plat_name, sys.version[0:3])
        self.build_lib = os.path.join("build", "lib"+plat_specifier)
        sys.path.insert(0, self.build_lib)
    def run(self):
        self.setup_path()
        loader = ScanningLoader()
        test = loader.loadTestsFromName(self.test_suite)
        runner = unittest.TextTestRunner(verbosity=2)
        result = runner.run(test)
        sys.exit(not result.wasSuccessful())
commands["test"] = Test

setup(name=PKG,
      version=get_normalized_version(),
      description='Python wrappers for a few algorithms from the Crypto++ library',
      long_description=readmetext,
      author='Zooko Wilcox-O\'Hearn',
      author_email='zooko@zooko.com',
      url='https://tahoe-lafs.org/trac/' + PKG,
      license='GNU GPL', # see README.rst for details -- there is also an alternative licence
      packages=["pycryptopp",
                "pycryptopp.cipher",
                "pycryptopp.hash",
                "pycryptopp.publickey",
                "pycryptopp.publickey.ed25519",
                "pycryptopp.test",
                ],
      include_package_data=True,
      exclude_package_data={
          '': [ '*.cpp', '*.hpp', ]
          },
      data_files=data_files,
      package_dir={"pycryptopp": "src/pycryptopp"},
      setup_requires=setup_requires,
      install_requires=install_requires,
      dependency_links=dependency_links,
      classifiers=trove_classifiers,
      ext_modules=ext_modules,
      test_suite=PKG+".test",
      zip_safe=False, # I prefer unzipped for easier access.
      cmdclass=commands,
      )
