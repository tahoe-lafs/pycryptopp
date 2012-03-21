from pycryptopp.hash import sha256

from common import insecurerandstr, rep_bench, print_bench_footer

INNER_REPS=10**3 # because these are too fast to measure

# This is used to calculate a measurement of how many milliseconds it takes
# to do a 1000-iteration inner loop.
REAL_UNITS_PER_SECOND=10**3 # microseconds

# This is used to report a measurement of how many microseconds it took to do
# 1 of those inner loops.
NOMINAL_UNITS_PER_SECOND=REAL_UNITS_PER_SECOND * INNER_REPS

UNITS_PER_SECOND = NOMINAL_UNITS_PER_SECOND

class SHA256(object):
    def proc_init(self, N):
        self.msg = insecurerandstr(N)

    def proc(self, N):
        for i in range(INNER_REPS):
            h = sha256.SHA256()
            h.update(self.msg)
            h.digest()

def generate_hash_benchers():
    try:
        import hashlib
    except ImportError:
        return [SHA256]
    else:
        class hashlibSHA256(object):
            def proc_init(self, N):
                self.msg = insecurerandstr(N)

            def proc(self, N):
                for i in range(INNER_REPS):
                    h = hashlib.sha256()
                    h.update(self.msg)
                    h.digest()
                
        return [SHA256, hashlibSHA256]
    
def bench_hashes(MAXTIME):
    for klass in generate_hash_benchers():
        print klass
        ob = klass()
        for (legend, size) in [
            ("small (%d B)",  32),
            ("medium (%d B)",  5000),
            ("large (%d B)",  50000),
            ]:
            print legend % size
            rep_bench(ob.proc, size, UNITS_PER_SECOND=UNITS_PER_SECOND, MAXTIME=MAXTIME, MAXREPS=100, initfunc=ob.proc_init)
            print

    print "time units per byte hashed"
    print_bench_footer(UNITS_PER_SECOND=UNITS_PER_SECOND)
    print


def bench(MAXTIME=10.0):
    bench_hashes(MAXTIME)

if __name__ == '__main__':
    bench()
