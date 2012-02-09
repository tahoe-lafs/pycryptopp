"""
pycryptopp - Python wrappers for Crypto++
"""

def _build_versions():
    from pycryptopp._version import get_versions
    versions = get_versions()
    # versions_from_git (as copied from python-versioneer) returns strings
    # like "1.9.0-25-gb73aba9-dirty", which means we're in a tree with
    # uncommited changes (-dirty), the latest checkin is revision b73aba9,
    # the most recent tag was 1.9.0, and b73aba9 has 25 commits that weren't
    # in 1.9.0 . The narrow-minded NormalizedVersion parser that takes our
    # output (meant to enable sorting of version strings) refuses most of
    # that, but accepts things like "1.9.0.post25", or "1.9.0.post25.dev0",
    # so dumb down our output to match.
    pieces = versions["version"].split("-")
    if len(pieces) == 1:
        normalized_version = pieces[0]
    else:
        normalized_version = "%s.post%s" % (pieces[0], pieces[1])
    if pieces[-1] == "dirty":
        normalized_version += ".dev0"
    # this returns e.g.:
    #  0.5.29.post51,
    #  0.5.29-51-ga81fad1,
    #  a81fad1d4afae353a40cf56fe88aa6ef0eea31a8
    return versions["version"], normalized_version, versions["full"]
__real_version__, __version__, __full_version__ = _build_versions()
del _build_versions

# we import our glue .so here, and then other modules use the copy in
# sys.modules.

import _pycryptopp
__doc__ = _pycryptopp.__doc__

def _import_my_names(thismodule, prefix):
    for name in dir(_pycryptopp):
        if name.startswith(prefix):
            myname = name[len(prefix):]
            thismodule[myname] = getattr(_pycryptopp, name)

import publickey, hash, cipher

quiet_pyflakes=[__version__, publickey, hash, cipher, _pycryptopp, __doc__, _import_my_names]
del quiet_pyflakes
