#!/usr/bin/env python

import random, re

import unittest

from binascii import b2a_hex, a2b_hex

global VERBOSE
VERBOSE=False

from pycryptopp.hash import sha256

from pkg_resources import resource_string

def resource_string_lines(pkgname, resname):
    return split_on_newlines(resource_string(pkgname, resname))

from base64 import b32encode
def ab(x): # debuggery
    if len(x) >= 3:
        return "%s:%s" % (len(x), b32encode(x[-3:]),)
    elif len(x) == 2:
        return "%s:%s" % (len(x), b32encode(x[-2:]),)
    elif len(x) == 1:
        return "%s:%s" % (len(x), b32encode(x[-1:]),)
    elif len(x) == 0:
        return "%s:%s" % (len(x), "--empty--",)

def randstr(n):
    return ''.join(map(chr, map(random.randrange, [0]*n, [256]*n)))

h0 = a2b_hex("e3b0c44298fc1c149afbf4c8996fb92427ae41e4649b934ca495991b7852b855")
h_bd = a2b_hex("68325720aabd7c82f30f554b313d0570c95accbb7dc4b5aae11204c08ffe732b")
h_5fd4 = a2b_hex("7c4fbf484498d21b487b9d61de8914b2eadaf2698712936d47c3ada2558f6788")

class SHA256(unittest.TestCase):
    def test_digest(self):
        empty_digest = sha256.SHA256().digest()
        self.failUnless(isinstance(empty_digest, str))
        self.failUnlessEqual(len(empty_digest), 32)
        self.failUnlessEqual(empty_digest, h0)

    def test_hexdigest(self):
        empty_hexdigest = sha256.SHA256().hexdigest()
        self.failUnlessEqual(a2b_hex(empty_hexdigest), h0)
    test_hexdigest.todo = "Not yet implemented: SHA256.hexdigest()."

    def test_onebyte_1(self):
        d = sha256.SHA256("\xbd").digest()
        self.failUnlessEqual(d, h_bd)

    def test_onebyte_2(self):
        s = sha256.SHA256()
        s.update("\xbd")
        d = s.digest()
        self.failUnlessEqual(d, h_bd)

    def test_update(self):
        s = sha256.SHA256("\x5f")
        s.update("\xd4")
        d = s.digest()
        self.failUnlessEqual(d, h_5fd4)

    def test_constructor_type_check(self):
        self.failUnlessRaises(TypeError, sha256.SHA256, None)

    def test_update_type_check(self):
        h = sha256.SHA256()
        self.failUnlessRaises(TypeError, h.update, None)

    def test_digest_twice(self):
        h = sha256.SHA256()
        d1 = h.digest()
        self.failUnless(isinstance(d1, str))
        d2 = h.digest()
        self.failUnlessEqual(d1, d2)

    def test_digest_then_update_fail(self):
        h = sha256.SHA256()
        h.digest()
        try:
            h.update("oops")
        except sha256.Error, le:
            self.failUnless("digest() has been called" in str(le), le)

    def test_chunksize(self):
        # hashes can be computed on arbitrarily-sized chunks
        problems = False
        for length in range(2, 140):
            s = "a"*length
            expected = sha256.SHA256(s).hexdigest()
            for a in range(0, length):
                h = sha256.SHA256()
                h.update(s[:a])
                h.update(s[a:])
                got = h.hexdigest()
                if got != expected:
                    problems = True
                    print len(s[:a]), len(s[a:]), len(s), got, expected
        self.failIf(problems)

    def test_recursive_different_chunksizes(self):
        """
        Test that updating a hasher with various sized inputs yields
        the expected answer. This is somewhat redundant with
        test_chunksize(), but that's okay. This one exercises some
        slightly different situations (such as finalizing a hash after
        different length inputs.) This one is recursive so that there
        is a single fixed result that we expect.
        """
        hx = sha256.SHA256()
        s = ''.join([ chr(c) for c in range(65) ])
        for i in range(0, 65):
            hy = sha256.SHA256(s[:i]).digest()
            hx.update(hy)
        for i in range(0, 65):
            hx.update(chr(0xFE))
            hx.update(s[:64])
        self.failUnlessEqual(hx.hexdigest().lower(), '5191c7841dd4e16aa454d40af924585dffc67157ffdbfd0236acddd07901629d')


VECTS_RE=re.compile("\nLen = ([0-9]+)\nMsg = ([0-9a-f]+)\nMD = ([0-9a-f]+)")

# split_on_newlines() copied from pyutil.strutil
def split_on_newlines(s):
    """
    Splits s on all of the three newline sequences: "\r\n", "\r", or "\n".
    """
    res = []
    for x in s.split('\r\n'):
        for y in x.split('\r'):
           res.extend(y.split('\n'))
    return res

class SHSVectors(unittest.TestCase):
    """
    All of the SHA-256 test vectors from the NIST SHS, in the files distributed
    by NIST.  (NIST distributes them in a .zip, but we expect them to be
    unpacked and in a subdirectory named 'testvectors').
    """
    def test_short(self):
        return self._test_vect(resource_string('pycryptopp', 'testvectors/SHA256ShortMsg.txt'))

    def test_long(self):
        return self._test_vect(resource_string('pycryptopp', 'testvectors/SHA256LongMsg.txt'))

    def _test_vect(self, vects_str):
        for mo in VECTS_RE.finditer(vects_str):
            msglenbits = int(mo.group(1))
            assert msglenbits % 8 == 0
            msglen = msglenbits / 8
            msg = a2b_hex(mo.group(2))[:msglen] # The slice is necessary because NIST seems to think that "00" is a reasonable representation for the zero-length string.
            assert len(msg) == msglen, (len(msg), msglen)
            md = a2b_hex(mo.group(3))

            computed_md = sha256.SHA256(msg).digest()
            self.failUnlessEqual(computed_md, md)

    def test_monte(self):
        inlines = resource_string_lines('pycryptopp', 'testvectors/SHA256Monte.txt')
        for line in inlines:
            line = line.strip()
            if line[:7] == 'Seed = ':
                seed = a2b_hex(line[7:])
                break

        j = 0
        for line in inlines:
            line = line.strip()
            if line[:8] == 'COUNT = ':
                assert int(line[8:]) == j
            elif line[:5] == 'MD = ':
                mds = []
                mds.append(seed);mds.append(seed);mds.append(seed);
                for i in range(1000):
                    m = mds[-3]+mds[-2]+mds[-1]
                    mds.append(sha256.SHA256(m).digest())
                seed = mds[-1]
                self.failUnlessEqual(line[5:], b2a_hex(seed))
                j += 1
