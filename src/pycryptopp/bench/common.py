msg = "crypto libraries should come with benchmarks"

try:
    raise ImportError
    import pyutil.benchutil
    rep_bench = pyutil.benchutil.rep_bench
except (ImportError, AttributeError):
    def this_rep_bench(func, N, UNITS_PER_SECOND, MAXTIME, MAXREPS, initfunc=None):
        import time
        tt = time.time
        tc = time.clock

        if initfunc is not None:
            initfunc(N)

        meant = 0
        meanc = 0
        MAXREPS = 100

        timeout = tt() + MAXTIME

        for i in range(MAXREPS):
            startt = tt()
            startc = tc()

            func(N)

            stopt = time.time()
            stopc = time.clock()

            deltat = stopt - startt
            deltac = stopc - startc
            if (deltat <= 0) or (deltac <= 0):
                print "startt: %s, startc: %s, stopt: %s, stopc: %s" % (startt, startc, stopt, stopc,)

            meant += deltat
            meanc += deltac

            if stopt >= timeout:
                break

        num = i+1
        meant *= UNITS_PER_SECOND
        meant /= num
        meant /= N

        res = {
            'meant': meant,
            'meanc': meanc,
            'num': num
            }
        print "mean: %(meant)#8.03e or %(meanc)#8.03e (of %(num)6d)" % res
    rep_bench = this_rep_bench

try:
    import pyutil.benchutil
    print_bench_footer = pyutil.benchutil.print_bench_footer
except (ImportError, AttributeError):
    def this_print_bench_footer(UNITS_PER_SECOND=1):
        from decimal import Decimal as D

        print "time units per second: %s; seconds per time unit: %s" % (UNITS_PER_SECOND, D(1)/UNITS_PER_SECOND)
    print_bench_footer = this_print_bench_footer

import random as insecurerandom
def insecurerandstr(n):
    return ''.join(map(chr, map(insecurerandom.randrange, [0]*n, [256]*n)))

