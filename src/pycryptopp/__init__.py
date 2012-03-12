"""
pycryptopp - Python wrappers for Crypto++
"""

# we import our glue .so here, and then other modules use the copy in
# sys.modules.

import _pycryptopp
__doc__ = _pycryptopp.__doc__
__version__ = _pycryptopp.__version__

def _import_my_names(thismodule, prefix):
    for name in dir(_pycryptopp):
        if name.startswith(prefix):
            myname = name[len(prefix):]
            thismodule[myname] = getattr(_pycryptopp, name)

import publickey, hash, cipher

quiet_pyflakes=[__version__, publickey, hash, cipher, _pycryptopp, __doc__, _import_my_names]
del quiet_pyflakes
