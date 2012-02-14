
from pycryptopp import _import_my_names

# These initializations to None are just to pacify pyflakes, which
# doesn't understand that we have to do some funky import trickery
# below in _import_my_names() in order to get sensible namespaces.
AES=None
Error=None

_import_my_names(globals(), "aes_")

del _import_my_names

def start_up_self_test():
    """
    This is a quick test intended to detect major errors such as the library being
    miscompiled and segfaulting or returning incorrect answers.  We've had problems
    of that kind many times, thus justifying running this self-test on import.
    This idea was suggested to me by the second edition of "Practical
    Cryptography" by Ferguson, Schneier, and Kohno.
    These tests were copied from pycryptopp/test/test_aes.py on 2009-10-30.
    """
    enc0 = "dc95c078a2408989ad48a21492842087530f8afbc74536b9a963b4f1c4cb738b"
    from binascii import a2b_hex, b2a_hex

    cryptor = AES(key="\x00"*32)
    ct = cryptor.process("\x00"*32)
    if enc0 != b2a_hex(ct):
        raise Error("pycryptopp failed startup self-test. Please run pycryptopp unit tests.")

    cryptor = AES(key="\x00"*32)
    ct1 = cryptor.process("\x00"*15)
    ct2 = cryptor.process("\x00"*17)
    if enc0 != b2a_hex(ct1+ct2):
        raise Error("pycryptopp failed startup self-test. Please run pycryptopp unit tests.")

    enc0 = "66e94bd4ef8a2c3b884cfa59ca342b2e"
    cryptor = AES(key="\x00"*16)
    ct = cryptor.process("\x00"*16)
    if enc0 != b2a_hex(ct):
        raise Error("pycryptopp failed startup self-test. Please run pycryptopp unit tests.")

    cryptor = AES(key="\x00"*16)
    ct1 = cryptor.process("\x00"*8)
    ct2 = cryptor.process("\x00"*8)
    if enc0 != b2a_hex(ct1+ct2):
        raise Error("pycryptopp failed startup self-test. Please run pycryptopp unit tests.")

    def _test_from_Niels_AES(keysize, result):
        def fake_ecb_using_ctr(k, p):
            return AES(key=k, iv=p).process('\x00'*16)

        E = fake_ecb_using_ctr
        b = 16
        k = keysize
        S = '\x00' * (k+b)
        for i in range(1000):
            K = S[-k:]
            P = S[-k-b:-k]
            S += E(K, E(K, P))

        if S[-b:] != a2b_hex(result):
            raise Error("pycryptopp failed startup self-test. Please run pycryptopp unit tests.")

    _test_from_Niels_AES(16, 'bd883f01035e58f42f9d812f2dacbcd8')
    _test_from_Niels_AES(32, 'c84b0f3a2c76dd9871900b07f09bdd3e')

start_up_self_test()
