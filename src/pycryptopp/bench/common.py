msg = "crypto libraries should come with benchmarks"

try:
    import pyutil.benchutil
    rep_bench = pyutil.benchutil.rep_bench
except (ImportError, AttributeError):
    def this_rep_bench(func, N, UNITS_PER_SECOND, MAXTIME, MAXREPS, initfunc=None):
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
        mean /= N

        res = {
            'mean': mean/num,
            'num': num
            }
        print "mean: %(mean)#8.03e (of %(num)6d)" % res
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

