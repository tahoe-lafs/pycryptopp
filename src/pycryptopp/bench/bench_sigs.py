from pycryptopp.publickey import ecdsa, ed25519

import os

msg = "crypto libraries should come with benchmarks"

N = 1000

class ECDSA192(object):
    def __init__(self):
        self.seed = os.urandom(32)
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
        
class ED25519(object):
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
        
def main():
    from pyutil.benchutil import rep_bench, print_bench_footer

    for klass in [ECDSA192, ED25519]:
        print klass
        ob = klass()
        print "gen"
        rep_bench(ob.gen, N, UNITS_PER_SECOND=1000)
        print "sign"
        rep_bench(ob.sign, N, UNITS_PER_SECOND=1000, initfunc=ob.sign_init)
        print "ver"
        rep_bench(ob.ver, N, UNITS_PER_SECOND=1000, initfunc=ob.ver_init)

    print_bench_footer(UNITS_PER_SECOND=1000)

if __name__ == '__main__':
    main()
