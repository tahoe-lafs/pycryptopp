===========================================================
 pycryptopp: a small number of good cryptography algorithms
===========================================================

Introduction and Licence
========================

pycryptopp is a python wrapper around a few algorithms from the Crypto++
library.

It lives at https://tahoe-lafs.org/trac/pycryptopp

LICENCE
-------

You may use this package under the GNU General Public License, version
2 or, at your option, any later version.  You may use this package
under the Transitive Grace Period Public Licence, version 1.0 or, at
your option, any later version.  (You may choose to use this package
under the terms of either licence, at your option.)  See the file
COPYING.GPL for the terms of the GNU General Public License, version 2.
See the file COPYING.TGPPL.html for the terms of the Transitive Grace
Period Public Licence, version 1.0.

The Ed25519 code comes from the python-ed25519 distribution [3]_, for which
the basic C code is in the public domain, and the Python bindings are under
the MIT license. See COPYING.ed25519 for details.

BUILDING
--------

To build it run "./setup.py build".  To test it run "./setup.py test".
To install it into your system run "./setup.py install".  To create a
binary package run "./setup.py bdist_egg".  There are more features of
setup.py -- see the documentation of setuptools [1] for details.

If "./setup.py test" doesn't print out "PASSED" and exit with exit
code 0 then there is something seriously wrong.  Do not use this build
of pycryptopp.  Please report the error to the cryptopp-users mailing
list [2].  The next step in debugging if the pycryptopp tests fail is
to find out if the underlying Crypto++ tests fail on the same system.
To do that, you have to acquire the Crypto++ source code from
http://cryptopp.com , build it, and run the self-test, by executing
"cryptest.exe v", as described in Crypto++'s Readme.txt file.

DOCUMENTATION
-------------

The documentation is in the docstrings.  From a command-line, use
"pydoc pycryptopp", "pydoc pycryptopp.cipher", and so on.  From within
a Python interpreter use "help(pycryptopp)",
"help(pycryptopp.cipher)", "help(pycryptopp.cipher.aes)" and so on.

The documentation for pycryptopp.publickey.ed25519 is in README.ed25519,
adapted from the upstream python-ed25519 library [3].

CONTACT
-------

Please post to the cryptopp-users mailing list [2] with comments about
this package.

BOOK REVIEW
-----------

If you are not already acquainted with modern cryptography, buy a copy
of Ferguson, Schneier, and Kohno "Cryptography Engineering" and read it.
It is easy going and will increase your understanding greatly.

ACKNOWLEDGEMENTS
----------------

Thanks to Wei Dai and the contributors to Crypto++, Andrew M. Kuchling
for his "pycrypto" library which inspired this one, Brian Warner for
help on Python packaging questions, inspiration, and a million other
things besides, and Greg Hazel and Samuel Neves for Windows porting
and fixing bugs.


Zooko O'Whielacronx
Boulder, Colorado
January 7, 2012


.. [1] http://peak.telecommunity.com/DevCenter/setuptools
.. [2] http://groups.google.com/group/cryptopp-users
.. [3] https://github.com/warner/python-ed25519
