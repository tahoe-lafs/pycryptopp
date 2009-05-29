"""
pycryptopp - Python wrappers for Crypto++
"""

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # We're running in a tree that hasn't run "./setup.py darcsver", and didn't
    # come with a _version.py, so we don't know what our version is. This should
    # not happen very often.
    pass

# we import our glue .so here, and then other modules use the copy in
# sys.modules. We wrap the import with RTLD_GLOBAL to make the C++ symbols in
# our _pycryptopp.so glue match the symbols defined in libcrypto++.so . On
# windows, which has RTLD_GLOBAL but not sys.getdlopenflags), we just import
# it normally, because windows is basically always in RTLD_GLOBAL mode.

import sys

use_RTLD_GLOBAL = hasattr(sys, "getdlopenflags")
if use_RTLD_GLOBAL:
    try:
        from ctypes import RTLD_GLOBAL as RTLD_GLOBAL_FROM_CTYPES
        RTLD_GLOBAL = RTLD_GLOBAL_FROM_CTYPES # hack to hush pyflakes
        del RTLD_GLOBAL_FROM_CTYPES
    except ImportError:
        # ctypes was added in Python 2.5 -- we still support Python 2.4, which
        # had dl instead
        from dl import RTLD_GLOBAL as RTLD_GLOBAL_FROM_DL
        RTLD_GLOBAL = RTLD_GLOBAL_FROM_DL
        del RTLD_GLOBAL_FROM_DL
    flags = sys.getdlopenflags()

try:
    if use_RTLD_GLOBAL:
        sys.setdlopenflags(flags|RTLD_GLOBAL)

    import _pycryptopp # all that work for one little import

finally:
    if use_RTLD_GLOBAL:
        sys.setdlopenflags(flags)
        del flags, RTLD_GLOBAL


def _import_my_names(thismodule, prefix):
    for name in dir(_pycryptopp):
        if name.startswith(prefix):
            myname = name[len(prefix):]
            thismodule[myname] = getattr(_pycryptopp, name)

import publickey, hash, cipher

quiet_pyflakes=[__version__, publickey, hash, cipher, _pycryptopp]
del sys, quiet_pyflakes
