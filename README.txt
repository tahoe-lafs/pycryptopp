ABOUT THIS PACKAGE

pycryptopp [1] is a python wrapper around the Crypto++ library [2].

LICENSE

You may use this package under the GNU General Public License, version 2 or, at
your option, any later version.  You may use this package under the Transitive
Grace Period Public Licence, version 1.0.  (You may choose to use this package
under the terms of either licence, at your option.)  See the file COPYING.GPL
for the terms of the GNU General Public License, version 2.  See the file
COPYING.TGPPL for the terms of the Transitive Grace Period Public Licence,
version 1.0.

BUILDING

To build this package from source requires the Crypto++ library including
development headers.  To build it run "./setup.py build".  To test it run
"./setup.py test".  To install it into your system run "./setup.py install".  To
create a binary package run "./setup.py bdist_egg".  There are more features of
setup.py -- see the documentation of setuptools [3] for details.

Note: on Mac OS X, it doesn't work to install Crypto++ into the standard "/usr"
PREFIX, e.g. by running "make install" in the cryptopp directory -- you'll get
an error message like "/usr/bin/ld: can't locate file for: -lcryptopp" when you
try to build pycryptopp.  However, it does work to run "make install
PREFIX=/usr/local".  This appears to be a strange feature of the Mac OS X
version of gcc.

DOCUMENTATION

The documentation is in the docstrings.  From within a Python interpreter use
"help(pycryptopp)", "help(pycryptopp.cipher)", and "help(pycryptopp.cipher.aes)"
and so on.  From a command-line, use "pydoc pycryptopp", "pydoc
pycryptopp.cipher", and so on.

CONTACT

I intend to set up a mailing list, but until I do please post to the
cryptopp-users mailing list [4] with comments about this package.

ACKNOWLEDGEMENTS

Thanks to Wei Dai and the contributors to Crypto++, Andrew M. Kuchling for his
"pycrypto" library which inspired this one, and Brian Warner for help on Python
packaging questions and a million other things besides.


Zooko O'Whielacronx
Boulder, Colorado
December 17, 2007

[1] http://pypi.python.org/pypi/pycryptopp
[2] http://cryptopp.com
[3] http://peak.telecommunity.com/DevCenter/setuptools
[4] http://groups.google.com/group/cryptopp-users
