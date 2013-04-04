

===========================================================
 pycryptopp: a small number of good cryptography algorithms
===========================================================

Introduction and Licence
========================

Pycryptopp is a collection of Python interfaces to a few good crypto
algorithms. It lives at https://tahoe-lafs.org/trac/pycryptopp

RECOMMENDED algorithms:

• AES-CTR ; from the Crypto++ library ; see pycryptopp.cipher.aes
• XSalsa20 ; from the Crypto++ library ; see pycryptopp.cipher.xsalsa20
• Ed25519 ; from the supercop library ; see pycryptopp.publickey.ed25519

DEPRECATED algorithms:

The maintainers of pycryptopp intend to stop supporting these soon. Please
migrate away from depending on pycryptopp's implementation of these
algorithms, or else write to us and offer some inducement to continue
supporting them.

• RSA from the Crypto++ library ; see pycryptopp.publickey.rsa ; deprecated
  in favor of Ed25519
• Ecdsa from the Crypto++ library ; see pycryptopp.publickey.ecdsa ;
  deprecated in favor of Ed25519
• SHA-256 from the Crypto++ library ; see pycryptopp.hash.sha256 ; deprecated
  in favor of the Python Standard Library's hashlib module

LICENCE
-------

You may use this package under the GNU General Public License, version 2 or,
at your option, any later version. You may use this package under the
Transitive Grace Period Public Licence, version 1.0 or, at your option, any
later version. You may use this package under the MIT License. You may use
this package under the Simple Permissive Licence.

(You may choose to use this package under the terms of any of these licences,
at your option.)

See the file COPYING.GPL for the terms of the GNU General Public License,
version 2. See the file COPYING.TGPPL.rst for the terms of the Transitive
Grace Period Public Licence, version 1.0. See the file COPYING.MIT.txt for
the terms of the MIT License. See the file COPYING.SPL.txt for the terms of
the Simple Permissive Licence.

BUILDING
--------

To build it run "python setup.py build". To test it run "python setup.py
test". To install it into your system run "python setup.py install". To
create a binary package run "python setup.py bdist_egg".

If "python setup.py test" doesn't print out "PASSED" and exit with exit
code 0 then there is something seriously wrong. Do not use this build of
pycryptopp. Please report the error to the tahoe-dev mailing list ²_.

To see some simple benchmarks run "python setup.py bench". If the "pyutil"
library is installed then the benchmarks will include mean, best, worst, and
quartiles of wall-clock time, else they will just report the mean wall-clock
time per operation.

DOCUMENTATION
-------------

The documentation is in the docstrings. From a command-line, use "pydoc
pycryptopp", "pydoc pycryptopp.cipher", and so on. From within a Python
interpreter use "help(pycryptopp)", "help(pycryptopp.cipher)",
"help(pycryptopp.cipher.aes)" and so on.

The documentation for pycryptopp.publickey.ed25519 is in README.ed25519.rst,
adapted from the upstream python-ed25519 library.

CONTACT
-------

Please post to the tahoe-dev mailing list ²_ with comments about this
package.

BOOK REVIEW
-----------

If you are not already acquainted with how to use modern cryptography, read
Ferguson, Schneier, and Kohno “Cryptography Engineering”.  It is easy going
and will increase your understanding greatly.

ACKNOWLEDGEMENTS
----------------

Thanks to Wei Dai and the contributors to Crypto++, Andrew M. Kuchling for
his "pycrypto" library which inspired this one, Brian Warner for help on
Python packaging questions, python-Ed25519, inspiration, and a million other
things besides, Greg Hazel and Samuel Neves for Windows porting and fixing
bugs, and Daniel J. Bernstein for Ed25519.


Zooko Wilcox-O'Hearn

Boulder, Colorado, USA

2012-03-18


.. _¹: https://github.com/warner/python-ed25519
.. _²: https://tahoe-lafs.org/cgi-bin/mailman/listinfo/tahoe-dev
