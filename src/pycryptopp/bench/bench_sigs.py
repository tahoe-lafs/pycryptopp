from pycryptopp.publickey import ecdsa, ed25519, rsa

from common import insecurerandstr, rep_bench

msg = 'crypto libraries should come with benchmarks'

class ECDSA256(object):
    def __init__(self):
        self.seed = insecurerandstr(32)
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
        self.seed = insecurerandstr(32)
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
        
class RSA2048(object):
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
        
class RSA3248(object):
    SIZEINBITS=3248

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
        
def bench_sigs(MAXTIME):
    for klass in [ECDSA256, Ed25519,]:
        print klass
        ob = klass()
        print "generate key"
        rep_bench(ob.gen, 1000, UNITS_PER_SECOND=1000, MAXTIME=MAXTIME, MAXREPS=100)
        print "sign"
        rep_bench(ob.sign, 1000, UNITS_PER_SECOND=1000, initfunc=ob.sign_init, MAXTIME=MAXTIME, MAXREPS=100)
        print "verify"
        rep_bench(ob.ver, 1000, UNITS_PER_SECOND=1000, initfunc=ob.ver_init, MAXTIME=MAXTIME, MAXREPS=100)
        print

    for klass in [RSA2048, RSA3248]:
        print klass
        ob = klass()
        print "generate key"
        rep_bench(ob.gen, 1, UNITS_PER_SECOND=1000, MAXTIME=MAXTIME, MAXREPS=100)
        print "sign"
        rep_bench(ob.sign, 1000, UNITS_PER_SECOND=1000, initfunc=ob.sign_init, MAXTIME=MAXTIME, MAXREPS=100)
        print "verify"
        rep_bench(ob.ver, 10000, UNITS_PER_SECOND=1000, initfunc=ob.ver_init, MAXTIME=MAXTIME, MAXREPS=100)
        print

    print "milliseconds per operation"
    print

def bench(MAXTIME=10.0):
    bench_sigs(MAXTIME)

if __name__ == '__main__':
    bench()
