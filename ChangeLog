2012-03-13  Zooko Wilcox-O'Hearn  <zooko@zooko.com>

	• src/pycryptopp/_version.py: release pycryptopp-0.6.0
	• add Ed25519 signatures (#75)
	• add XSalsa20 cipher (#40)
	• switch from darcs to git for revision control
	• pycryptopp version numbers now include a decimal encoding of the
	  git revid
	• reorganize the source tree and the version number generation
	• aesmodule.cpp: validate size of IV and throw exception if it is not 16 (#70)
	• fixed compile errors with gcc-4.7.0 (#78)
	• fixed compile errors concerning "CryptoPP::g_nullNameValuePairs" (#77)
	• suppress warnings from valgrind with new OpenSSL 1.0.1 on Fedora (#82)
	• raise Python exception instead of uncaught C++ exception
	  (resulting in abort) when deserializing malformed RSA keys (#83)

2009-09-15  Zooko Wilcox-O'Hearn  <zooko@zooko.com>

	• release pycryptopp-0.5.17
	• publickey/rsamodule.cpp, publickey/ecdsamodule.cpp,
	  hash/sha256module.cpp, cipher/aesmodule.cpp: fix a segfault bug
	  when sizeof(size_t) > sizeof(int) (not exploitable); thanks Nathan
	  Wilcox and Brian Warner. (#19)

2009-07-27  Zooko Wilcox-O'Hearn  <zooko@zooko.com>

	• release pycryptopp-0.5.16
	• setup.py, misc/: a few improvements to the build/packaging
