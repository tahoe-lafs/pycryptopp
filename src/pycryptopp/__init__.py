"""
pycryptopp - Python wrappers for Crypto++
"""

# we import our glue .so here, and then other modules use the copy in
# sys.modules.

import _pycryptopp
__doc__ = _pycryptopp.__doc__

__version__ = "unknown"
try:
    import _version
except ImportError:
    # We're running in a tree that hasn't run "python ./setup.py
    # update_version", and didn't come with a _version.py, so we don't know
    # what our version is. This should not happen very often.
    pass
else:
    __version__ = _version.__version__

def _import_my_names(thismodule, prefix):
    for name in dir(_pycryptopp):
        if name.startswith(prefix):
            myname = name[len(prefix):]
            thismodule[myname] = getattr(_pycryptopp, name)

import publickey, hash, cipher

quiet_pyflakes=[__version__, publickey, hash, cipher, _pycryptopp, __doc__, _import_my_names]
del quiet_pyflakes
