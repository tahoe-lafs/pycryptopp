#!/usr/bin/env python

import random, re

import unittest

from binascii import a2b_hex, b2a_hex

global VERBOSE
VERBOSE=False

from pycryptopp.cipher import aes

from pkg_resources import resource_string, resource_listdir

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

class AES256(unittest.TestCase):
    enc0 = "dc95c078a2408989ad48a21492842087530f8afbc74536b9a963b4f1c4cb738b"

    def test_encrypt_zeroes(self):
        cryptor = aes.AES(key="\x00"*32)
        ct = cryptor.process("\x00"*32)
        self.failUnlessEqual(self.enc0, b2a_hex(ct))

    def test_init_type_check(self):
        self.failUnlessRaises(TypeError, aes.AES, None)
        self.failUnlessRaises(aes.Error, aes.AES, "a"*1) # too short
        self.failUnlessRaises(aes.Error, aes.AES, "a"*17) # not one of the valid key sizes for AES (16, 24, 32)

    def test_encrypt_zeroes_in_two_parts(self):
        cryptor = aes.AES(key="\x00"*32)
        ct1 = cryptor.process("\x00"*15)
        ct2 = cryptor.process("\x00"*17)
        self.failUnlessEqual(self.enc0, b2a_hex(ct1+ct2))

class AES128(unittest.TestCase):
    enc0 = "66e94bd4ef8a2c3b884cfa59ca342b2e"

    def test_encrypt_zeroes(self):
        cryptor = aes.AES(key="\x00"*16)
        ct = cryptor.process("\x00"*16)
        self.failUnlessEqual(self.enc0, b2a_hex(ct))

    def test_init_type_check(self):
        self.failUnlessRaises(TypeError, aes.AES, None)
        self.failUnlessRaises(aes.Error, aes.AES, "a") # too short

    def test_encrypt_zeroes_in_two_parts(self):
        cryptor = aes.AES(key="\x00"*16)
        ct1 = cryptor.process("\x00"*8)
        ct2 = cryptor.process("\x00"*8)
        self.failUnlessEqual(self.enc0, b2a_hex(ct1+ct2))

def fake_ecb_using_ctr(k, p):
    return aes.AES(key=k, iv=p).process('\x00'*16)

NIST_KAT_VECTS_RE=re.compile("\nCOUNT = ([0-9]+)\nKEY = ([0-9a-f]+)\nPLAINTEXT = ([0-9a-f]+)\nCIPHERTEXT = ([0-9a-f]+)")

class AES_from_NIST_KAT(unittest.TestCase):
    def test_NIST_KAT(self):
        for vectname in resource_listdir('pycryptopp', 'testvectors/KAT_AES'):
            self._test_KAT_file(resource_string('pycryptopp', '/'.join(['testvectors/KAT_AES', vectname])))

    def _test_KAT_file(self, vects_str):
        for mo in NIST_KAT_VECTS_RE.finditer(vects_str):
            key = a2b_hex(mo.group(2))
            plaintext = a2b_hex(mo.group(3))
            ciphertext = a2b_hex(mo.group(4))

            computedciphertext = fake_ecb_using_ctr(key, plaintext)
            self.failUnlessEqual(computedciphertext, ciphertext, "computedciphertext: %s, ciphertext: %s, key: %s, plaintext: %s" % (b2a_hex(computedciphertext), b2a_hex(ciphertext), b2a_hex(key), b2a_hex(plaintext)))

class AES_from_Niels_Ferguson(unittest.TestCase):
    # http://blogs.msdn.com/si_team/archive/2006/05/19/aes-test-vectors.aspx
    def _test_from_Niels_AES(self, keysize, result):
        E = fake_ecb_using_ctr
        b = 16
        k = keysize
        S = '\x00' * (k+b)
        for i in range(1000):
            K = S[-k:]
            P = S[-k-b:-k]
            S += E(K, E(K, P))

        self.failUnlessEqual(S[-b:], a2b_hex(result))

    def test_from_Niels_AES128(self):
        return self._test_from_Niels_AES(16, 'bd883f01035e58f42f9d812f2dacbcd8')

    def test_from_Niels_AES256(self):
        return self._test_from_Niels_AES(32, 'c84b0f3a2c76dd9871900b07f09bdd3e')

class PartialIV(unittest.TestCase):
    def test_partial(self):
        k = "k"*16
        for iv_len in range(0, 16)+range(17,70): # all are wrong, 16 is right
            self.failUnlessRaises(aes.Error,
                                  aes.AES, k, iv="i"*iv_len)

if __name__ == "__main__":
    unittest.main()
