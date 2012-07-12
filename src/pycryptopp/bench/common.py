msg = "crypto libraries should come with benchmarks"

try:
    import pyutil.benchutil
    rep_bench = pyutil.benchutil.rep_bench
except (ImportError, AttributeError):
    import platform, time
    if 'windows' in platform.system().lower():
        clock = time.clock
    else:
        clock = time.time

    def this_rep_bench(func, N, UNITS_PER_SECOND, MAXTIME, MAXREPS, initfunc=None):
        tt = time.time

        if initfunc is not None:
            initfunc(N)

        meanc = 0
        MAXREPS = 100

        timeout = tt() + MAXTIME

        for i in range(MAXREPS):
            startc = clock()

            func(N)

            stopc = clock()

            deltac = stopc - startc
            if deltac <= 0:
                print "clock jump backward or wrapped -- ignoring this sample. startc: %s, stopc: %s, deltac: %s" % (startc, stopc, deltac,)
            else:
                meanc += deltac

            if time.time() >= timeout:
                break

        num = i+1
        meanc *= UNITS_PER_SECOND
        meanc /= num
        meanc /= N

        res = {
            'meanc': meanc,
            'num': num
            }
        print "mean: %(meanc)#8.03e (of %(num)6d)" % res
    rep_bench = this_rep_bench

import random as insecurerandom
def insecurerandstr(n):
    return ''.join(map(chr, map(insecurerandom.randrange, [0]*n, [256]*n)))

def calib_clock():
    interval = 1.0
    
    import time
    tc = time.clock
    tt = time.time

    def measure_sleep(x, clock):
        st = clock()
        time.sleep(x)
        
    
