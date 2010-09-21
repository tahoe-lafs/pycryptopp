2010-09-20 -- pycryptopp v0.5.24

    * make setup backwards-compatible to Python 2.4
    * fix incompatibilities between setup script and older versions of darcsver

2010-09-20 -- pycryptopp v0.5.23

    * don't attempt to compile Mac OS X extended attribute files (this fixes the build breaking)
    * include a version number of the specific version of Crypto++ in extraversion.h
    * small changes to docs

2010-09-18 -- pycryptopp v0.5.20

    * fix bugs in assembly implementation of SHA-256 from Crypto++
    * fix it to compile on *BSD (#39)
    * improve doc strings
    * add a quick start-up-self-test of SHA256 (#43)
    * execute the quick start-up-self-tests of AES and SHA256 on module import
