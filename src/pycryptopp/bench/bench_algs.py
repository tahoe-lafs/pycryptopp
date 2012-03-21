import bench_sigs, bench_ciphers, bench_hashes

def bench(MAXTIME=10.0):
    bench_sigs.bench(MAXTIME)
    bench_ciphers.bench(MAXTIME)
    bench_hashes.bench(MAXTIME)

if __name__ == '__main__':
    bench()
