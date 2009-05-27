import sys, ctypes
flags = sys.getdlopenflags()
try:
    sys.setdlopenflags(flags|ctypes.RTLD_GLOBAL)
    from pycryptopp import _pycryptopp
finally:
    sys.setdlopenflags(flags)

MYNAMEPATTERN="sha256_"

thismodule = globals()
for name in dir(_pycryptopp):
    if name.startswith(MYNAMEPATTERN):
        myname = name[len(MYNAMEPATTERN):]
        thismodule[myname] = getattr(_pycryptopp, name)

for name in ['sys', 'ctypes', 'flags', '_pycryptopp', 'MYNAMEPATTERN', 'myname']:
    if thismodule.has_key(name):
        del thismodule[name]

del name
del thismodule
