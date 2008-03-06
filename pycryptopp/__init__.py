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

import publickey, hash, cipher

quiet_pyflakes=[__version__, publickey, hash, cipher]
