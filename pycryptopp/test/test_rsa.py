#!/usr/bin/env python

import cStringIO, os, random, re

import unittest

global VERBOSE
VERBOSE=False

from pycryptopp.publickey import rsa

from base64 import b32encode
def ab(x): # debuggery
    if len(x) >= 3:
        return "%s:%s" % (len(x), b32encode(x[-3:]),)
    elif len(x) == 2:
        return "%s:%s" % (len(x), b32encode(x[-2:]),)
    elif len(x) == 1:
        return "%s:%s" % (len(x), b32encode(x[-1:]),)
    elif len(x) == 0:
        return "%s:%s" % (len(x), "--empty--",)

def randstr(n):
    return ''.join(map(chr, map(random.randrange, [0]*n, [256]*n)))

KEYSIZE=1536
class Signer(unittest.TestCase):
    def test_generate_from_seed_bad_seed(self):
        try:
            signer = rsa.generate_from_seed(KEYSIZE, "aaa")
        except rsa.Error, le:
            self.failUnless("seed is required to be of length >=" in str(le), le)
        else:
            self.fail("Should have raised error from seed being too short.")

    def test_generate_from_seed_bad_size(self):
        try:
            signer = rsa.generate_from_seed(1535, "aaaaaaaa")
        except rsa.Error, le:
            self.failUnless("size in bits is required to be >=" in str(le), le)
        else:
            self.fail("Should have raised error from size being too small.")

    def test_generate_from_seed(self):
        signer = rsa.generate_from_seed(KEYSIZE, "aaaaaaaa")
        # Hooray!  It didn't raise an exception!  We win!

    def test_generate_bad_size(self):
        try:
            signer = rsa.generate(1535)
        except rsa.Error, le:
            self.failUnless("size in bits is required to be >=" in str(le), le)
        else:
            self.fail("Should have raised error from size being too small.")

    def test_generate(self):
        signer = rsa.generate(KEYSIZE)
        # Hooray!  It didn't raise an exception!  We win!

    def test_sign(self):
        signer = rsa.generate(KEYSIZE)
        result = signer.sign("abc")
        self.failUnlessEqual(len(result), ((KEYSIZE+7)/8))
        # TODO: test against RSAInc. test vectors.

    def _help_test_sign_and_check(self, signer, msg):
        sig = signer.sign(msg)
        self.failUnlessEqual(len(sig), ((KEYSIZE+7)/8))
        verifier = signer.get_verifying_key()
        self.failUnless(verifier.verify(msg, sig))

    def test_sign_and_check_a(self):
        signer = rsa.generate(KEYSIZE)
        return self._help_test_sign_and_check(signer, "a")

    def test_sign_and_check_random(self):
        signer = rsa.generate(KEYSIZE)
        for i in range(3):
            l = random.randrange(0, 2**10)
            msg = randstr(l)
            self._help_test_sign_and_check(signer, msg)

    def _help_test_sign_and_failcheck(self, signer, msg):
        sig = signer.sign("a")
        sig = sig[:-1] + chr(ord(sig[-1])^0x01)
        verifier = signer.get_verifying_key()
        self.failUnless(not verifier.verify(msg, sig))

    def test_sign_and_check_a(self):
        signer = rsa.generate(KEYSIZE)
        return self._help_test_sign_and_failcheck(signer, "a")

    def test_sign_and_check_random(self):
        signer = rsa.generate(KEYSIZE)
        for i in range(3):
            l = random.randrange(0, 2**10)
            msg = randstr(l)
            self._help_test_sign_and_failcheck(signer, msg)

if __name__ == "__main__":
    unittest.main()
