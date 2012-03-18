from keys import (BadSignatureError, SigningKey, VerifyingKey, __doc__)

(BadSignatureError, SigningKey, VerifyingKey, __doc__) # hush pyflakes

from _version import get_versions
__version__ = get_versions()['version']
del get_versions
