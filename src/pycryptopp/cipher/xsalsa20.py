from pycryptopp import _import_my_names

_import_my_names(globals(), "xsalsa20_")

del _import_my_names

def selftest():
    # pyflakes doesn't know that XSalsa20 is made available above
    XSalsa20 = globals()["XSalsa20"]
    from binascii import unhexlify
    key = unhexlify("ad5eadf7163b0d36e44c126037a03419"
                    "fcda2b3a1bb4ab064b6070e61b0fa5ca")
    iv = unhexlify("6a059adb8c7d4acb1c537767d541506f" "c5ef0ace9a2a65bd")
    encrypted = unhexlify("23a8ed0475150e988c545b11e3660de7"
                          "8bf88e6628c4c99ba36330c05cb919e7"
                          "901295db479c9a8a0401d5e040b8919b"
                          "7d64b2f728c59703c3")
    p = XSalsa20(key, iv)
    decrypted = p.process(encrypted)
    expected = "crypto libraries should always test themselves at powerup"
    assert decrypted == expected

    p = XSalsa20(key, iv)
    decrypted = ""
    offset = 0
    for chunksize in [13,11,1,2,3,20,999]:
        decrypted += p.process(encrypted[offset:offset+chunksize])
        offset += chunksize
    assert decrypted == expected

selftest()
