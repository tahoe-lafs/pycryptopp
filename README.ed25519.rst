

=====================================================
 Python Bindings to Ed25519 Digital Signature System
=====================================================

This package provides python bindings to a C implementation of the Ed25519
public-key signature system ¹_. The C code is copied from the SUPERCOP
benchmark suite ²_, using the portable "ref" implementation (not the
high-performance assembly code), and is very similar to the copy in the NaCl
library ³_.

With this library, you can quickly (2ms) create signing+verifying keypairs,
derive a verifying key from a signing key, sign messages, and verify the
signatures. The keys and signatures are very short, making them easy to
handle and incorporate into other protocols. All known attacks take at least
2¹²⁸ operations, providing a security level comparable to AES-128, NIST
P-256, and RSA-3248.


Speed and Key Sizes
-------------------

Signing keys are just 32 bytes (256 bits) of random data, so generating a
signing key is trivial: signingkey = os.urandom(32). Deriving a public
verifying key takes more time, as do the actual signing and verifying
operations.

A 256-bit elliptic curve key is estimated to be as strong as a much larger
RSA key. The "ECRYPT II" cryptographic experts group estimate the strength of
a 256-bit elliptic curve key to similar to the strength of a 3248-bit RSA
public key: http://keylength.com

On Brian Warner's 2010-era Mac laptop (2.8GHz Core2Duo), deriving a verifying
key takes 1.9ms, signing takes 1.9ms, and verification takes 6.3ms. The
high-performance assembly code in SUPERCOP (amd64-51-30k and amd64-64-24k) is
up to 100x faster than the portable reference version, and the python
overhead appears to be minimal (1-2us), so future releases may run even
faster.

Ed25519 private signing keys are 32 bytes long (this is expanded internally
to 64 bytes when necessary). The public verifying keys are also 32 bytes
long.  Signatures are 64 bytes long. All operations provide a 128-bit
security level.


Security
--------

The Ed25519 algorithm and C implementation are carefully designed to prevent
timing attacks. The Python wrapper might not preserve this property. Until it
has been audited for this purpose, do not allow attackers to measure how long
it takes you to generate a keypair or sign a message. Key generation depends
upon a strong source of random numbers. Do not use it on a system where
os.urandom() is weak.

Unlike typical DSA/ECDSA algorithms, signing does *not* require a source of
entropy. Ed25519 signatures are deterministic: using the same key to sign the
same data any number of times will result in the same signature each time.


Usage
-----

The first step is to generate a signing key and store it. At the same time,
you'll probably need to derive the verifying key and give it to someone else.
Signing keys are 32-byte uniformly-random strings. The safest way to generate
a key is with os.urandom(32)::

 import os
 from pycryptopp.publickey import ed25519

 sk_bytes = os.urandom(32)
 signing_key = ed25519.SigningKey(sk_bytes)
 open("my-secret-key","wb").write(sk_bytes)

 vkey_hex = signing_key.get_verifying_key_bytes().encode('hex')
 print "the public key is", vkey_hex

To reconstruct the same key from the stored form later, just pass it back
into SigningKey::

 sk_bytes = open("my-secret-key","rb").read()
 signing_key = ed25519.SigningKey(sk_bytes)


Once you have the SigningKey instance, use its .sign() method to sign a
message. The signature is 64 bytes::

 sig = signing_key.sign("hello world")
 print "sig is:", sig.encode('hex')

On the verifying side, the receiver first needs to construct a
ed25519.VerifyingKey instance from the serialized form, then use its
.verify() method on the signature and message::

 vkey_hex = "1246b84985e1ab5f83f4ec2bdf271114666fd3d9e24d12981a3c861b9ed523c6"
 verifying_key = ed25519.VerifyingKey(vkey_hex.decode('hex'))
 try:
   verifying_key.verify(sig, "hello world")
   print "signature is good"
 except ed25519.BadSignatureError:
   print "signature is bad!"

If you happen to have the SigningKey but not the corresponding VerifyingKey,
you can derive it with .get_verifying_key_bytes(). This allows the sending
side to hold just 32 bytes of data and derive everything else from that.
Deriving a verifying key takes about 1.9ms::

 sk_bytes = open("my-secret-key","rb").read()
 signing_key = ed25519.SigningKey(sk_bytes)
 verifying_key = ed25519.VerifyingKey(signing_key.get_verifying_key_bytes())

There is also a basic command-line keygen/sign/verify tool in bin/edsig .


API Summary
-----------

The complete API is summarized here::

 sk_bytes = os.urandom(32)
 sk = SigningKey(sk_bytes)
 vk_bytes = sk.get_verifying_key_bytes()
 vk = VerifyingKey(vk_bytes)

 signature = sk.sign(message)
 vk.verify(signature, message)


footnotes
---------

.. _¹: http://ed25519.cr.yp.to/
.. _²: http://bench.cr.yp.to/supercop.html
.. _³: http://nacl.cr.yp.to/
