from pycryptopp import _pycryptopp

MYNAMEPATTERN="ecdsa_"

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
