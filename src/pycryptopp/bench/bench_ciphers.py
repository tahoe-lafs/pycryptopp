from pycryptopp.cipher import aes, xsalsa20

from common import insecurerandstr, rep_bench

UNITS_PER_SECOND = 10**9

class BenchCrypt(object):
    def __init__(self, klass, keysize):
        self.klass = klass
        self.keysize = keysize

    def __repr__(self):
        return "<%s-%d>" % (self.klass.__name__, self.keysize*8)

    def crypt_init(self, N):
        self.msg = insecurerandstr(N)
        self.key = insecurerandstr(self.keysize)

    def crypt(self, N):
        cryptor = self.klass(self.key)
        cryptor.process(self.msg)
        
def bench_ciphers(MAXTIME):
    for (klass, keysize) in [
        (aes.AES, 16),
        (aes.AES, 32),
        (xsalsa20.XSalsa20, 32),
        ]:
        ob = BenchCrypt(klass, keysize)
        print ob
        for (legend, size) in [
            ("large (%d B)",  10**7),
            ]:
            print legend % size
            rep_bench(ob.crypt, size, UNITS_PER_SECOND=UNITS_PER_SECOND, MAXTIME=MAXTIME, MAXREPS=100, initfunc=ob.crypt_init)
            print

    print "nanoseconds per byte crypted"
    print

def bench(MAXTIME=10.0):
    bench_ciphers(MAXTIME)

if __name__ == '__main__':
    bench()
