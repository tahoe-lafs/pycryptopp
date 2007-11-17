#!/usr/bin/env python

import cStringIO, os, random, re

import unittest

from binascii import b2a_hex

global VERBOSE
VERBOSE=False

from pycryptopp.cipher import aes

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

enc0 = "66e94bd4ef8a2c3b884cfa59ca342b2e"

class AES(unittest.TestCase):
    def test_encrypt_zeroes(self):
        cryptor = aes.AES(key="\x00"*16)
        ct = cryptor.process("\x00"*16)
        self.failUnlessEqual(enc0, b2a_hex(ct))

    def test_init_type_check(self):
        self.failUnlessRaises(TypeError, aes.AES, None)
        self.failUnlessRaises(aes.Error, aes.AES, "a") # too short

    def test_encrypt_zeroes_in_two_parts(self):
        cryptor = aes.AES(key="\x00"*16)
        ct1 = cryptor.process("\x00"*8)
        ct2 = cryptor.process("\x00"*8)
        self.failUnlessEqual(enc0, b2a_hex(ct1+ct2))

if __name__ == "__main__":
    unittest.main()
