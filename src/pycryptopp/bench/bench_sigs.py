from pycryptopp.publickey import ecdsa, ed25519, rsa

import os

msg = "crypto libraries should come with benchmarks"

class ECDSA192(object):
    def __init__(self):
        self.seed = os.urandom(12)
        self.signer = None

    def gen(self, N):
        for i in xrange(N):
             ecdsa.SigningKey(self.seed)
        
    def sign_init(self, N):
        self.signer = ecdsa.SigningKey(self.seed)
        
    def sign(self, N):
        signer = self.signer
        for i in xrange(N):
            signer.sign(msg)
        
    def ver_init(self, N):
        signer = ecdsa.SigningKey(self.seed)
        self.sig = signer.sign(msg)
        self.verifier = signer.get_verifying_key()
        
    def ver(self, N):
        sig = self.sig
        verifier = self.verifier
        for i in xrange(N):
            verifier.verify(sig, msg)
        
class Ed25519(object):
    def __init__(self):
        self.seed = os.urandom(32)
        self.signer = None

    def gen(self, N):
        for i in xrange(N):
             ed25519.SigningKey(self.seed)
        
    def sign_init(self, N):
        self.signer = ed25519.SigningKey(self.seed)
        
    def sign(self, N):
        signer = self.signer
        for i in xrange(N):
            signer.sign(msg)
        
    def ver_init(self, N):
        signer = ed25519.SigningKey(self.seed)
        self.sig = signer.sign(msg)
        self.verifier = ed25519.VerifyingKey(signer.get_verifying_key_bytes())
        
    def ver(self, N):
        sig = self.sig
        verifier = self.verifier
        for i in xrange(N):
            verifier.verify(sig, msg)
        
class RSA(object):
    SIZEINBITS=2048

    def __init__(self):
        self.signer = None

    def gen(self, N):
        for i in xrange(N):
             rsa.generate(sizeinbits=self.SIZEINBITS)
        
    def sign_init(self, N):
        self.signer = rsa.generate(sizeinbits=self.SIZEINBITS)
        
    def sign(self, N):
        signer = self.signer
        for i in xrange(N):
            signer.sign(msg)
        
    def ver_init(self, N):
        signer = rsa.generate(sizeinbits=self.SIZEINBITS)
        self.sig = signer.sign(msg)
        self.verifier = signer.get_verifying_key()
        
    def ver(self, N):
        sig = self.sig
        verifier = self.verifier
        for i in xrange(N):
            verifier.verify(msg, sig)
        

def bench_with_pyutil(duration):
    from pyutil.benchutil import rep_bench, print_bench_footer

    for klass in [ECDSA192, Ed25519, RSA]:
        print klass
        ob = klass()
        print "generate key"
        rep_bench(ob.gen, 100, UNITS_PER_SECOND=1000, MAXTIME=duration, MAXREPS=100)
        print "sign"
        rep_bench(ob.sign, 100, UNITS_PER_SECOND=1000, initfunc=ob.sign_init, MAXTIME=duration, MAXREPS=100)
        print "verify"
        rep_bench(ob.ver, 100, UNITS_PER_SECOND=1000, initfunc=ob.ver_init, MAXTIME=duration, MAXREPS=100)

    print
    print_bench_footer(UNITS_PER_SECOND=1000)


def bench_without_pyutil(duration):
    def rep_bench(func, N, UNITS_PER_SECOND, MAXTIME, MAXREPS, initfunc=None):
        import time

        if initfunc is not None:
            initfunc(N)

        mean = 0
        MAXREPS = 100

        timeout = time.time() + MAXTIME

        for i in range(MAXREPS):
            start = time.time()

            func(N)

            stop = time.time()

            mean += (stop - start)

            if stop >= timeout:
                break

        num = i+1
        mean *= UNITS_PER_SECOND
        mean /= num

        res = {
            'mean': mean/num,
            'num': num
            }
        print "mean: %(mean)#8.03e (of %(num)6d)" % res

    def print_bench_footer(UNITS_PER_SECOND=1):
        from decimal import Decimal
        print "all results are in time units per N"
        print "time units per second: %s; seconds per time unit: %s" % (UNITS_PER_SECOND, Decimal(1)/UNITS_PER_SECOND)

    for klass in [ECDSA192, Ed25519, RSA]:
        print klass
        ob = klass()
        print "generate key"
        rep_bench(ob.gen, 100, UNITS_PER_SECOND=1000, MAXTIME=duration, MAXREPS=100)
        print "sign"
        rep_bench(ob.sign, 100, UNITS_PER_SECOND=1000, initfunc=ob.sign_init, MAXTIME=duration, MAXREPS=100)
        print "verify"
        rep_bench(ob.ver, 100, UNITS_PER_SECOND=1000, initfunc=ob.ver_init, MAXTIME=duration, MAXREPS=100)

    print
    print_bench_footer(UNITS_PER_SECOND=1000)

def bench(duration=10.0):
    try:
        bench_with_pyutil(duration=duration)
    except ImportError:
        bench_without_pyutil(duration=duration)

if __name__ == '__main__':
    bench()
