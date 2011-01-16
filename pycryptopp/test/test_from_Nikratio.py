import unittest

# This was reported as triggering a "Use of uninitialised value of
# size 4" under valgrind by Nikratio in pycryptopp-0.5.17 and Crypto++
# 5.6.0. See http://tahoe-lafs.org/trac/pycryptopp/ticket/67

class T(unittest.TestCase):
    def test_t(self):
        import hmac
        import pycryptopp
        try:
            import hashlib
        except ImportError:
            # Oh nevermind.
            return
        import struct

        def encrypt(buf, passphrase, nonce):

            key = hashlib.sha256(passphrase + nonce).digest()
            cipher = pycryptopp.cipher.aes.AES(key)
            hmac_ = hmac.new(key, digestmod=hashlib.sha256)

            hmac_.update(buf)
            buf = cipher.process(buf)
            hash_ = cipher.process(hmac_.digest())

            return ''.join(
                            (struct.pack('<B', len(nonce)),
                            nonce, hash_, buf))

        encrypt('foobar', 'passphrase', 'nonce')
