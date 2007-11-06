#!/usr/bin/env python

import cStringIO, os, random, re

import unittest

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

class SHA256(unittest.TestCase):
    def test_digest_twice(self):
        h = sha256.SHA256()
        d1 = h.digest()
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
