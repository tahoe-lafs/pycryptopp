import bench_sigs, bench_ciphers, bench_hashes

def bench(MAXTIME=10.0):
    import pycryptopp
    print pycryptopp
    print pycryptopp.__version__,
    print pycryptopp._pycryptopp.cryptopp_version
    import pkg_resources
    print pkg_resources.require('pycryptopp')
    bench_sigs.bench(MAXTIME)
    bench_ciphers.bench(MAXTIME)
    bench_hashes.bench(MAXTIME)

if __name__ == '__main__':
    bench()
