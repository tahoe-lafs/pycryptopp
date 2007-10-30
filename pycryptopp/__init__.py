"""
pycryptopp -- Python wrappers for Crypto++
"""

__version__ = "unknown"
try:
    from _version import __version__
except ImportError:
    # we're running in a tree that hasn't run darcsver, so we don't
    # know what our version is. This should not happen very often.
    pass

from _pycryptopp import generate, generate_from_seed
