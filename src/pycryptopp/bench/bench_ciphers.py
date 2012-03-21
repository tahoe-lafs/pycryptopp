from pycryptopp.cipher import aes, xsalsa20

from common import insecurerandstr, rep_bench, print_bench_footer

INNER_REPS=10**3 # because these are too fast to measure

# This is used to calculate a measurement of how many milliseconds it takes
# to do a 1000-iteration inner loop.
REAL_UNITS_PER_SECOND=10**3 # microseconds

# This is used to report a measurement of how many microseconds it took to do
# 1 of those inner loops.
NOMINAL_UNITS_PER_SECOND=REAL_UNITS_PER_SECOND * INNER_REPS

UNITS_PER_SECOND = NOMINAL_UNITS_PER_SECOND


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
        for i in range(INNER_REPS):
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
            ("small (%d B)",  500),
            ("medium (%d B)",  5000),
            ("large (%d B)",  50000),
            ]:
            print legend % size
            rep_bench(ob.crypt, size, UNITS_PER_SECOND=UNITS_PER_SECOND, MAXTIME=MAXTIME, MAXREPS=100, initfunc=ob.crypt_init)
            print

    print "time units per byte crypted"
    print_bench_footer(UNITS_PER_SECOND=UNITS_PER_SECOND)
    print

def bench(MAXTIME=10.0):
    bench_ciphers(MAXTIME)

if __name__ == '__main__':
    bench()
