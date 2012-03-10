#include <Python.h>

#include "publickey/ecdsamodule.hpp"
#include "publickey/rsamodule.hpp"
#include "hash/sha256module.hpp"
#include "cipher/aesmodule.hpp"
#include "cipher/xsalsa20module.hpp"

/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/config.h>
#else
#include <src-cryptopp/config.h>
#endif

PyDoc_STRVAR(_pycryptopp__doc__,
"_pycryptopp -- Python wrappers for a few algorithms from Crypto++\n\
\n\
from pycryptopp import publickey\n\
from pycryptopp.publickey import ecdsa\n\
from pycryptopp.publickey import rsa\n\
from pycryptopp import cipher\n\
from pycryptopp.cipher import aes\n\
from pycryptopp.cipher import xsalsa20\n\
from pycryptopp import hash\n\
from pycryptopp.hash import sha256");

static PyMethodDef _pycryptopp_functions[] = {
    {"rsa_generate", reinterpret_cast<PyCFunction>(rsa_generate), METH_KEYWORDS, const_cast<char*>(rsa_generate__doc__)},
    {"rsa_create_verifying_key_from_string", reinterpret_cast<PyCFunction>(rsa_create_verifying_key_from_string), METH_KEYWORDS, const_cast<char*>(rsa_create_verifying_key_from_string__doc__)},
    {"rsa_create_signing_key_from_string", reinterpret_cast<PyCFunction>(rsa_create_signing_key_from_string), METH_KEYWORDS, const_cast<char*>(rsa_create_signing_key_from_string__doc__)},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_pycryptopp(void) {
    PyObject *module;

    module = Py_InitModule3("_pycryptopp", _pycryptopp_functions, _pycryptopp__doc__);
    if (!module)
      return;

    PyObject* version;

    /* a tuple of (Crypto++ version, extra-version) */
    #ifndef DISABLE_EMBEDDED_CRYPTOPP
    /* In the version of Crypto++ which is included in pycryptopp, there is a
       symbol named `cryptopp_extra_version' which is declared (external
       variable) in config.h and defined in cryptlib.cpp. Of course it is
       possible that the header file we've #include'd is from the
       embedded-in-pycryptopp version of Crypto++ but the dynamically linked
       library that we load is from an older version which doesn't have this
       symbol. In that case, the load will fail before we get this far. */
    version = Py_BuildValue("is", CRYPTOPP_VERSION, cryptopp_extra_version);
    #else
    version = Py_BuildValue("iO", CRYPTOPP_VERSION, Py_None);
    #endif

    int succ = PyModule_AddObject(module, "cryptopp_version", version);
    if (succ != 0)
        return;


    init_ecdsa(module);
    init_rsa(module);
    init_sha256(module);
    init_aes(module);
    init_xsalsa20(module);
}
