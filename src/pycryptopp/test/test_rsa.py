#!/usr/bin/env python

import random

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

KEYSIZE=522 # 522 bits is far too few for actual security -- it is used only for faster unit tests

class Signer(unittest.TestCase):
    def test_generate_bad_size(self):
        try:
            rsa.generate(KEYSIZE-1)
        except rsa.Error, le:
            self.failUnless("size in bits is required to be >=" in str(le), le)
        else:
            self.fail("Should have raised error from size being too small.")
        try:
            rsa.generate(sizeinbits=KEYSIZE-1)
        except rsa.Error, le:
            self.failUnless("size in bits is required to be >=" in str(le), le)
        else:
            self.fail("Should have raised error from size being too small.")

    def test_generate(self):
        rsa.generate(KEYSIZE)
        # Hooray!  It didn't raise an exception!  We win!
        rsa.generate(sizeinbits=KEYSIZE)
        # Hooray!  It didn't raise an exception!  We win!

    def test_sign(self):
        signer = rsa.generate(KEYSIZE)
        result = signer.sign("abc")
        self.failUnlessEqual(len(result), ((KEYSIZE+7)/8))
        # TODO: test against RSAInc. test vectors.

    def test_create_from_string_invalid(self):
        try:
            rsa.create_signing_key_from_string("invalid string")
        except rsa.Error, le:
            self.failUnless("decode error" in str(le), le)
        else:
            self.fail("Should have raised error from invalid string")

        try:
            rsa.create_verifying_key_from_string("invalid string")
        except rsa.Error, le:
            self.failUnless("decode error" in str(le), le)
        else:
            self.fail("Should have raised error from invalid string")

class SignAndVerify(unittest.TestCase):
    def _help_test_sign_and_check(self, signer, verifier, msg):
        sig = signer.sign(msg)
        self.failUnlessEqual(len(sig), ((KEYSIZE+7)/8))
        self.failUnless(verifier.verify(msg, sig))

    def test_sign_and_check_a(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        return self._help_test_sign_and_check(signer, verifier, "a")

    def _help_test_sign_and_check_random(self, signer, verifier):
        for i in range(3):
            l = random.randrange(0, 2**10)
            msg = randstr(l)
            self._help_test_sign_and_check(signer, verifier, msg)

    def test_sign_and_check_random(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        return self._help_test_sign_and_check_random(signer, verifier)

    def _help_test_sign_and_failcheck(self, signer, verifier, msg):
        sig = signer.sign("a")
        sig = sig[:-1] + chr(ord(sig[-1])^0x01)
        self.failUnless(not verifier.verify(msg, sig))

    def test_sign_and_failcheck_a(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        return self._help_test_sign_and_failcheck(signer, verifier, "a")

    def _help_test_sign_and_failcheck_random(self, signer, verifier):
        for i in range(3):
            l = random.randrange(0, 2**10)
            msg = randstr(l)
            self._help_test_sign_and_failcheck(signer, verifier, msg)

    def test_sign_and_failcheck_random(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        return self._help_test_sign_and_failcheck_random(signer, verifier)

    def test_serialize_and_deserialize_verifying_key_and_test(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        serstr = verifier.serialize()
        verifier = None
        newverifier = rsa.create_verifying_key_from_string(serstr)
        self._help_test_sign_and_check(signer, newverifier, "a")
        self._help_test_sign_and_check_random(signer, newverifier)
        self._help_test_sign_and_failcheck(signer, newverifier, "a")
        self._help_test_sign_and_failcheck_random(signer, newverifier)

    def test_serialize_and_deserialize_signing_key_and_test(self):
        signer = rsa.generate(KEYSIZE)
        verifier = signer.get_verifying_key()
        serstr = signer.serialize()
        signer = None
        newsigner = rsa.create_signing_key_from_string(serstr)
        self._help_test_sign_and_check(newsigner, verifier, "a")
        self._help_test_sign_and_check_random(newsigner, verifier)
        self._help_test_sign_and_failcheck(newsigner, verifier, "a")
        self._help_test_sign_and_failcheck_random(newsigner, verifier)


if __name__ == "__main__":
    unittest.main()
