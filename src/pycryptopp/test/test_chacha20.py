import random, re
import unittest

from binascii import a2b_hex, b2a_hex
from pkg_resources import resource_string

from pycryptopp.cipher import chacha20
TEST_XSALSA_RE=re.compile("\nCOUNT=([0-9]+)\nKEY=([0-9a-f]+)\nIV=([0-9a-f]+)\nPLAINTEXT=([0-9a-f]+)\nCIPHERTEXT=([0-9a-f]+)")

class ChaCha20Test(unittest.TestCase):

    enc0="20b800ca9a9247bcc09a6816b123be47ac0681e23749d35fea22c04e1b1b9bb19782ab297a65c80ab1bac2ff2c4beba4c807bf832fdb57e648b3b677d87f8758123fb0f9d39efa95d7dd3f72fb0abe9b96e68514e758e9de31ae1d694c462de537f7e45188f2dcb912c6a0ed1aee5f6b4d2be8c3a1126e928b6fea91d643f9bbe808d984c2517bcb928161"

    def test_zero_ChaCha20(self):
        key="1b27556473e985d462cd51197a9a46c76009549eac6474f206c4ee0844f68389"
        iv="69696ee955b62b73cd62bda875fc73d68219e0036b7a0b37"
        computedcipher=chacha20.ChaCha20(a2b_hex(key),a2b_hex(iv)).process('\x00'*139)
        self.failUnlessEqual(a2b_hex(self.enc0), computedcipher, "enc0: %s, computedciper: %s" % (self.enc0, b2a_hex(computedcipher)))

        cryptor=chacha20.ChaCha20(a2b_hex(key),a2b_hex(iv))

        computedcipher1=cryptor.process('\x00'*69)
        computedcipher2=cryptor.process('\x00'*69)
        computedcipher3=cryptor.process('\x00')
        computedcipher12=b2a_hex(computedcipher1)+b2a_hex(computedcipher2)+b2a_hex(computedcipher3)
        self.failUnlessEqual(self.enc0, computedcipher12)


    def test_ChaCha20(self):
        # The test vector is from Crypto++'s TestVectors/chacha.txt, comment
        # there is: Source: created by Wei Dai using naclcrypto-20090308 .
        # naclcrypto being DJB's crypto library and of course DJB designed
        # ChaCha20
        s = resource_string("pycryptopp", "testvectors/chacha.txt")
        return self._test_ChaCha20(s)

    def _test_ChaCha20(self, vects_str):
        for mo in TEST_XSALSA_RE.finditer(vects_str):
            #count = int(mo.group(1))
            key = a2b_hex(mo.group(2))
            iv = a2b_hex(mo.group(3))
            #plaintext = a2b_hex(mo.group(4))
            #ciphertext= a2b_hex(mo.group(5))
            plaintext = mo.group(4)
            ciphertext = mo.group(5)
            computedcipher=chacha20.ChaCha20(key,iv).process(a2b_hex(plaintext))
            #print "ciphertext", b2a_hex(computedcipher), '\n'
            #print "computedtext", ciphertext, '\n'
            #print count, ": \n"
            self.failUnlessEqual(computedcipher,a2b_hex(ciphertext),"computedcipher: %s, ciphertext: %s" % (b2a_hex(computedcipher), ciphertext))

            #the random decomposing
            plaintext1 = ""
            plaintext2 = ""
            length = len(plaintext)
            rccipher = ""
            cryptor = chacha20.ChaCha20(key,iv)
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
            cryptor = chacha20.ChaCha20(key,iv)
            eccipher=""
            l = 0
            while l<=(length-2):
                    eccipher += b2a_hex(cryptor.process(a2b_hex(plaintext[l:l+2])))
                    l += 2
            self.failUnlessEqual(eccipher, ciphertext, "every byte computed cipher: %s, ciphertext: %s" % (eccipher, ciphertext))


    def test_types_and_lengths(self):

        # the key= argument must be a bytestring exactly 32 bytes long
        self.failUnlessRaises(TypeError, chacha20.ChaCha20, None)
        for i in range(70):
            key = "a"*i
            if i != 32 and i != 16:
                self.failUnlessRaises(chacha20.Error, chacha20.ChaCha20, key)
            else:
                self.failUnless(chacha20.ChaCha20(key))

        # likewise, iv= (if provided) must be exactly 24 bytes long. Passing
        # None is not treated the same as not passing the argument at all.
        key = "a"*32
        self.failUnlessRaises(TypeError, chacha20.ChaCha20, key, None)
        for i in range(70):
            iv = "i"*i
            if i != 24:
                self.failUnlessRaises(chacha20.Error, chacha20.ChaCha20, key, iv)
            else:
                self.failUnless(chacha20.ChaCha20(key, iv))

    def test_recursive(self):
        # Try to use the same technique as:
        # http://blogs.msdn.com/si_team/archive/2006/05/19/aes-test-vectors.aspx
        # It's not exactly the same, though, because ChaCha20 is a stream
        # cipher, whereas the Ferguson code is exercising a block cipher. But
        # we try to do something similar.

        # the ChaCha20 internal function uses a 32-byte block. We want to
        # exercise it twice for each key, to guard against
        # clobbering-after-key-setup errors. Just doing enc(enc(p)) could let
        # XOR errors slip through. So to be safe, use B=64.
        B=64
        N=24
        K=32
        s = "\x00"*(B+N+K)
        def enc(key, nonce, plaintext):
            p = chacha20.ChaCha20(key=key, iv=nonce)
            return p.process(plaintext)
        for i in range(1000):
            plaintext = s[-K-N-B:-K-N]
            nonce = s[-K-N:-K]
            key = s[-K:]
            ciphertext = enc(key, nonce, plaintext)
            s += ciphertext
            s = s[-K-N-B:]
        output = b2a_hex(s[-B:])
        # I compared test output against pysodium - David
        self.failUnlessEqual(output, "2a84ffcd163b683daafd51b2d10af7338ac5fb25716d5f7b6e6af9cdbe6abd6e63c00d4e8eff8c306b17d71691b6ce1e6e0577c0e8e719abb3dfa7f7b21d955e")



if __name__ == "__main__":
    unittest.main()
