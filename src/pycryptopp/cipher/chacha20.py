from pycryptopp import _import_my_names

_import_my_names(globals(), "chacha20_")

del _import_my_names

def selftest():
    # pyflakes doesn't know that Chacha20 is made available above
    Chacha20 = globals()["ChaCha20"]
    from binascii import unhexlify
    key = unhexlify("ad5eadf7163b0d36e44c126037a03419"
                    "fcda2b3a1bb4ab064b6070e61b0fa5ca")
    iv = unhexlify("6a059adb8c7d4acb1c537767d541506f" "c5ef0ace9a2a65bd")
    encrypted = unhexlify("6c845801d0df33d8aa5ad8c8ff3ebfd5"
                          "9ab66b64f2157e8c6521e0c34ef0f233"
                          "baf02fa7a2c289d1b725905667696ac9"
                          "ba966d72b2d6cac601")
    p = Chacha20(key, iv)
    decrypted = p.process(encrypted)
    expected = "crypto libraries should always test themselves at powerup"
    assert decrypted == expected

    p = Chacha20(key, iv)
    decrypted = ""
    offset = 0
    for chunksize in [13,11,1,2,3,20,999]:
        decrypted += p.process(encrypted[offset:offset+chunksize])
        offset += chunksize
    assert decrypted == expected

selftest()
