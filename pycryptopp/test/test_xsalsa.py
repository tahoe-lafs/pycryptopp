#!/usr/bin/env python

import random, re
import unittest

from binascii import a2b_hex, b2a_hex
from pkg_resources import resource_string

from pycryptopp.cipher import xsalsa
TEST_XSALSA_RE=re.compile("\nCOUNT=([0-9]+)\nKEY=([0-9a-f]+)\nIV=([0-9a-f]+)\nPLAINTEXT=([0-9a-f]+)\nCIPHERTEXT=([0-9a-f]+)")

class XSalsaTest(unittest.TestCase):

    enc0="eea6a7251c1e72916d11c2cb214d3c252539121d8e234e652d651fa4c8cff880309e645a74e9e0a60d8243acd9177ab51a1beb8d5a2f5d700c093c5e5585579625337bd3ab619d615760d8c5b224a85b1d0efe0eb8a7ee163abb0376529fcc09bab506c618e13ce777d82c3ae9d1a6f972d4160287cbfe60bf2130fc0a6ff6049d0a5c8a82f429231f0080"

    def test_zero_XSalsa(self):
        key="1b27556473e985d462cd51197a9a46c76009549eac6474f206c4ee0844f68389"
        iv="69696ee955b62b73cd62bda875fc73d68219e0036b7a0b37"
        computedcipher=xsalsa.XSalsa(a2b_hex(key),a2b_hex(iv)).process('\x00'*139)
        self.failUnlessEqual(a2b_hex(self.enc0), computedcipher, "enc0: %s, computedciper: %s" % (self.enc0, b2a_hex(computedcipher)))

        cryptor=xsalsa.XSalsa(a2b_hex(key),a2b_hex(iv))

        computedcipher1=cryptor.process('\x00'*69)
        computedcipher2=cryptor.process('\x00'*69)
        computedcipher3=cryptor.process('\x00')
        computedcipher12=b2a_hex(computedcipher1)+b2a_hex(computedcipher2)+b2a_hex(computedcipher3)
        self.failUnlessEqual(self.enc0, computedcipher12)


    def test_XSalsa(self):
        # The test vector is from Crypto++'s TestVectors/salsa.txt, comment there is:
        # Source: created by Wei Dai using naclcrypto-20090308
        # naclcrypto being DJB's crypto library and of course DJB designed XSalsa20
        curfile = open( '../testvectors/testx1.txt', 'r')
        s = curfile.read()
        print s,"\n"
        return self._test_XSalsa(s)

    def _test_XSalsa(self, vects_str):
        for mo in TEST_XSALSA_RE.finditer(vects_str):
            count = int(mo.group(1))
            key = a2b_hex(mo.group(2))
            iv = a2b_hex(mo.group(3))
#           plaintext = a2b_hex(mo.group(4))
#           ciphertext= a2b_hex(mo.group(5))
            plaintext = mo.group(4)
            ciphertext = mo.group(5)
            computedcipher=xsalsa.XSalsa(key,iv).process(a2b_hex(plaintext))
#           print "ciphertext", b2a_hex(computedcipher), '\n'
#           print "computedtext", ciphertext, '\n'
#           print count, ": \n"
            self.failUnlessEqual(computedcipher,a2b_hex(ciphertext),"computedcipher: %s, ciphertext: %s" % (b2a_hex(computedcipher), ciphertext))

            #the random decomposing
            plaintext1 = ""
            plaintext2 = ""
            length = len(plaintext)
            rccipher = ""
            cryptor = xsalsa.XSalsa(key,iv)
            if length > 2:
                point = random.randint(0,length-3)
                if (point%2) !=0:
                    point -= 1
                plaintext1 += plaintext[:point+2]
                plaintext2 += plaintext[point+2:]
                rccipher += b2a_hex(cryptor.process(a2b_hex(plaintext1)))
                rccipher += b2a_hex(cryptor.process(a2b_hex(plaintext2)))
                self.failUnlessEqual(rccipher, ciphertext, "random computed cipher: %s, ciphertext: %s" % (rccipher, ciphertext))

            #every byte encrypted
            cryptor = xsalsa.XSalsa(key,iv)
            eccipher=""
            l = 0
            while l<=(length-2):
                    eccipher += b2a_hex(cryptor.process(a2b_hex(plaintext[l:l+2])))
                    l += 2
            self.failUnlessEqual(eccipher, ciphertext, "every byte computed cipher: %s, ciphertext: %s" % (eccipher, ciphertext))


    def test_init_type_check(self):
            self.failUnlessRaises(TypeError, xsalsa.XSalsa, None)
            self.failUnlessRaises(xsalsa.Error, xsalsa.XSalsa, "a"*1)
            self.failUnlessRaises(xsalsa.Error, xsalsa.XSalsa, "a"*17)
            self.failUnlessRaises(xsalsa.Error, xsalsa.XSalsa, "a"*18)
#           self.failUnlessRaises(xsalsa.Error, xsalsa.XSalsa, "a"*32)

if __name__ == "__main__":
    unittest.main()
