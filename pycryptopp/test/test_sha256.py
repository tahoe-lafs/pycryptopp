#!/usr/bin/env python

import cStringIO, os, random, re

import unittest

from binascii import b2a_hex

global VERBOSE
VERBOSE=False

from pycryptopp.hash import sha256

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

h0 = "e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855"
h_bd = "68325720aabd7c82f30f554b313d0570c95accbb7dc4b5aae11204c08ffe732b"
h_5fd4 = "7c4fbf484498d21b487b9d61de8914b2eadaf2698712936d47c3ada2558f6788"

class SHA256(unittest.TestCase):
    def test_digest(self):
        empty_digest = sha256.SHA256().digest()
        self.failUnless(isinstance(empty_digest, str))
        self.failUnless(len(empty_digest) == 32)
        self.failUnless(b2a_hex(empty_digest) == h0)
        #empty_hexdigest = sha256.SHA256().hexdigest()

    def test_onebyte_1(self):
        d = sha256.SHA256("\xbd").digest()
        self.failUnless(b2a_hex(d) == h_bd)

    def test_onebyte_2(self):
        s = sha256.SHA256()
        s.update("\xbd")
        d = s.digest()
        self.failUnless(b2a_hex(d) == h_bd)

    def test_update(self):
        s = sha256.SHA256("\x5f")
        s.update("\xd4")
        d = s.digest()
        self.failUnless(b2a_hex(d) == h_5fd4)

    def test_update_type_check(self):
        h = sha256.SHA256()
        try:
            h.update(None)
        except sha256.Error, le:
            self.failUnless("recondition violation: you are required to pass a Python string" in str(le), le)

    def test_digest_twice(self):
        h = sha256.SHA256()
        d1 = h.digest()
        self.failUnless(isinstance(d1, str))
        d2 = h.digest()
        self.failUnless(d1 == d2)

    def test_digest_then_update_fail(self):
        h = sha256.SHA256()
        d1 = h.digest()
        try:
            h.update("oops")
        except sha256.Error, le:
            self.failUnless("digest() has been called" in str(le), le)

if __name__ == "__main__":
    unittest.main()
