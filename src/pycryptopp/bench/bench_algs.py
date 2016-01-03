import bench_sigs, bench_ciphers, bench_hashes

def print_versions():
    import pycryptopp
    print "pycryptopp: ", pycryptopp
    print "pycryptopp.__version__: ", pycryptopp.__version__,
    print "pycryptopp._pycryptopp.cryptopp_version: ", pycryptopp._pycryptopp.cryptopp_version
    print "pycryptopp.publickey.ed25519._version.get_versions(): ", pycryptopp.publickey.ed25519._version.get_versions()
    import pkg_resources
    print "pkg_resources.require('pycryptopp'): ", pkg_resources.require('pycryptopp')

def bench(MAXTIME=10.0):
    print_versions()
    bench_sigs.bench(MAXTIME)
    bench_ciphers.bench(MAXTIME)
    bench_hashes.bench(MAXTIME)

if __name__ == '__main__':
    bench()
