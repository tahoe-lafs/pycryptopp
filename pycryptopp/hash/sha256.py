try:
    from ctypes import RTLD_GLOBAL
except ImportError:
    # ctypes was added in Python 2.5 -- we still support Python 2.4, which had dl instead
    from dl import RTLD_GLOBAL

import sys
flags = sys.getdlopenflags()
try:
    sys.setdlopenflags(flags|RTLD_GLOBAL)
    from pycryptopp import _pycryptopp
finally:
    sys.setdlopenflags(flags)

MYNAMEPATTERN="sha256_"

thismodule = globals()
for name in dir(_pycryptopp):
    if name.startswith(MYNAMEPATTERN):
        myname = name[len(MYNAMEPATTERN):]
        thismodule[myname] = getattr(_pycryptopp, name)

for name in ['sys', 'RTLD_GLOBAL', 'flags', '_pycryptopp', 'MYNAMEPATTERN', 'myname']:
    if thismodule.has_key(name):
        del thismodule[name]

del name
del thismodule
