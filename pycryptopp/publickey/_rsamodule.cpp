/**
 * _rsamodule.cpp -- Python wrappers around Crypto++'s RSA-PSS-SHA256
 * more precisely:
 * <a href="http://www.weidai.com/scan-mirror/sig.html#sem_PSS-MGF1">PSS-MGF1</a>
 * with RSA as the public key algorithm and SHA-256 as the hash function
 */

#include <Python.h>

/* from Crypto++ */
#ifdef USE_NAME_CRYPTO_PLUS_PLUS
// for Debian (and Ubuntu, and their many derivatives)
#include "crypto++/filters.h"
#include "crypto++/osrng.h"
#include "crypto++/pssr.h"
#include "crypto++/randpool.h"
#include "crypto++/rsa.h"
#else
// for upstream Crypto++ library
#include "cryptopp/filters.h"
#include "cryptopp/osrng.h"
#include "cryptopp/pssr.h"
#include "cryptopp/randpool.h"
#include "cryptopp/rsa.h"
#endif

USING_NAMESPACE(CryptoPP)

static char rsa__doc__[] = "\
rsa -- RSA-PSS-SHA256 signatures\n\
\n\
To create a new RSA signing key from the operating system's random number generator, call generate().\n\
To create a new RSA signing key from a seed, call generate_from_seed().\n\
To deserialize an RSA signing key from a string, call create_signing_key_from_string().\n\
\n\
To get an RSA verifying key from an RSA signing key, call get_verifying_key() on the signing key.\n\
To deserialize an RSA verifying key from a string, call create_verifying_key_from_string().\n\
";

/* NOTE: if the complete expansion of the args (by vsprintf) exceeds 1024 then memory will be invalidly overwritten. */
/* (We don't use vsnprintf because Microsoft standard libraries don't support it.) */
static PyObject *rsa_error;
static PyObject *
raise_rsa_error(const char *format, ...) {
    char exceptionMsg[1024];
    va_list ap;

    va_start (ap, format);
    vsprintf (exceptionMsg, format, ap); /* Make sure that this can't exceed 1024 chars! */
    va_end (ap);
    exceptionMsg[1023]='\0';
    PyErr_SetString (rsa_error, exceptionMsg);
    return NULL;
}

static char VerifyingKey__doc__[] = "\
An RSA verifying key.\n\
";

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Verifier *k;
} VerifyingKey;

static PyObject *
VerifyingKey_new(PyTypeObject *type, PyObject *args, PyObject *kwdict) {
    VerifyingKey *self = (VerifyingKey*)type->tp_alloc(type, 0);
    self->k = NULL;
    return (PyObject *)self;
}

static void
VerifyingKey_dealloc(VerifyingKey* self) {
    if (self->k != NULL)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
VerifyingKey_verify(VerifyingKey *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "msg",
        "signature",
        NULL
    };
    const char *msg;
    size_t msgsize;
    const char *signature;
    size_t signaturesize;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#s#", const_cast<char**>(kwlist), &msg, &msgsize, &signature, &signaturesize))
        return NULL;

    size_t sigsize = self->k->SignatureLength();
    if (sigsize != signaturesize)
        return raise_rsa_error("Precondition violation: signatures are required to be of size %u, but it was %u", sigsize, signaturesize);

    assert (signaturesize == sigsize);

    if (self->k->VerifyMessage(reinterpret_cast<const byte*>(msg), msgsize, reinterpret_cast<const byte*>(signature), signaturesize))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

static char VerifyingKey_verify__doc__[] = "\
Return whether the signature is a valid signature on the msg.\n\
";

static PyObject *
VerifyingKey_serialize(VerifyingKey *self, PyObject *args, PyObject *kwdict) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

static char VerifyingKey_serialize__doc__[] = "\
Return a string containing the key material.  The string can be passed to \n\
create_verifying_key_from_string() to instantiate a new copy of this key.\n\
";

static PyMethodDef VerifyingKey_methods[] = {
    {"verify", reinterpret_cast<PyCFunction>(VerifyingKey_verify), METH_VARARGS, VerifyingKey_verify__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(VerifyingKey_serialize), METH_VARARGS, VerifyingKey_serialize__doc__},
    {NULL},
};

static PyTypeObject VerifyingKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_rsa.VerifyingKey", /*tp_name*/
    sizeof(VerifyingKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)VerifyingKey_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    VerifyingKey__doc__,           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    VerifyingKey_methods,             /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    VerifyingKey_new,                 /* tp_new */
};

static char SigningKey__doc__[] = "\
An RSA signing key.\n\
";

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Signer *k;
} SigningKey;

static PyObject *
SigningKey_new(PyTypeObject *type, PyObject *args, PyObject *kwdict) {
    SigningKey *self = (SigningKey*)type->tp_alloc(type, 0);
    self->k = NULL;
    return (PyObject *)self;
}

static void
SigningKey_dealloc(SigningKey* self) {
    if (self->k != NULL)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SigningKey_sign(SigningKey *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "msg",
        NULL
    };
    const char *msg;
    size_t msgsize;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#", const_cast<char**>(kwlist), &msg, &msgsize))
        return NULL;

    size_t sigsize = self->k->SignatureLength();
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, sigsize));
    if (!result)
        return NULL;

    AutoSeededRandomPool randpool(false);
    size_t siglengthwritten = self->k->SignMessage(
        randpool,
        reinterpret_cast<const byte*>(msg),
        msgsize,
        reinterpret_cast<byte*>(PyString_AS_STRING(result)));
    if (siglengthwritten < sigsize)
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, __func__, "INTERNAL ERROR: signature was shorter than expected.");
    else if (siglengthwritten > sigsize) {
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, __func__, "INTERNAL ERROR: signature was longer than expected, so unallocated memory was overwritten.");
        abort();
    }

    return reinterpret_cast<PyObject*>(result);
}

static char SigningKey_sign__doc__[] = "\
Return a signature on the argument.\n\
";

static PyObject *
SigningKey_get_verifying_key(SigningKey *self, PyObject *args, PyObject *kwdict) {
    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_new(&VerifyingKey_type, NULL, NULL));
    if (verifier == NULL)
        return NULL;

    verifier->k = new RSASS<PSS, SHA256>::Verifier(*(self->k));
    if (verifier->k != NULL)
        return reinterpret_cast<PyObject*>(verifier);
    else
        return NULL;
}

static char SigningKey_get_verifying_key__doc__[] = "\
Return the corresponding verifying key.\n\
";

static PyObject *
SigningKey_serialize(SigningKey *self, PyObject *args, PyObject *kwdict) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

static char SigningKey_serialize__doc__[] = "\
Return a string containing the key material.  The string can be passed to \n\
create_signing_key_from_string() to instantiate a new copy of this key.\n\
";

static PyMethodDef SigningKey_methods[] = {
    {"sign", reinterpret_cast<PyCFunction>(SigningKey_sign), METH_VARARGS, SigningKey_sign__doc__},
    {"get_verifying_key", reinterpret_cast<PyCFunction>(SigningKey_get_verifying_key), METH_VARARGS, SigningKey_get_verifying_key__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(SigningKey_serialize), METH_VARARGS, SigningKey_serialize__doc__},
    {NULL},
};

static PyTypeObject SigningKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_rsa.SigningKey", /*tp_name*/
    sizeof(SigningKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)SigningKey_dealloc, /*tp_dealloc*/
    0,                         /*tp_print*/
    0,                         /*tp_getattr*/
    0,                         /*tp_setattr*/
    0,                         /*tp_compare*/
    0,                         /*tp_repr*/
    0,                         /*tp_as_number*/
    0,                         /*tp_as_sequence*/
    0,                         /*tp_as_mapping*/
    0,                         /*tp_hash */
    0,                         /*tp_call*/
    0,                         /*tp_str*/
    0,                         /*tp_getattro*/
    0,                         /*tp_setattro*/
    0,                         /*tp_as_buffer*/
    Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
    SigningKey__doc__,           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    SigningKey_methods,             /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    0,                         /* tp_init */
    0,                         /* tp_alloc */
    SigningKey_new,                 /* tp_new */
};

static const int MIN_KEY_SIZE_BITS=1536; /* recommended minimum by NESSIE in 2003 */
static PyObject *
generate_from_seed(PyObject *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "size",
        "seed",
        NULL
    };
    int size;
    const char* seed;
    int seedlen;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "is#", const_cast<char**>(kwlist), &size, &seed, &seedlen))
        return NULL;

    if (size < MIN_KEY_SIZE_BITS)
        return raise_rsa_error("Precondition violation: size in bits is required to be >= %u, but it was %d", MIN_KEY_SIZE_BITS, size);

    if (seedlen < 8)
        return raise_rsa_error("Precondition violation: seed is required to be of length >= %u, but it was %d", 8, seedlen);

    RandomPool randPool;
    randPool.Put((byte *)seed, seedlen); /* In Crypto++ v5.5.2, the recommended interface is "IncorporateEntropy()", but "Put()" is supported for backwards compatibility.  In Crypto++ v5.2 (the version that comes with Ubuntu dapper), only "Put()" is available. */

    SigningKey *signer = reinterpret_cast<SigningKey*>(SigningKey_new(&SigningKey_type, NULL, NULL));
    if (signer == NULL)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(randPool, size);
    return reinterpret_cast<PyObject*>(signer);
}

static char generate_from_seed__doc__[] = "\
Create a signing key deterministically from the given seed.\n\
\n\
This implies that if someone can guess the seed then they can learn the signing key.\n\
See also generate().\n\
\n\
@param size length of the key in bits\n\
@param seed seed\n\
\n\
@precondition size >= 1536\n\
@precondition len(seed) >= 8\n\
";

static PyObject *
generate(PyObject *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "size",
        NULL
    };
    int size;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "i", const_cast<char**>(kwlist), &size))
        return NULL;

    if (size < MIN_KEY_SIZE_BITS)
        return raise_rsa_error("Precondition violation: size in bits is required to be >= %u, but it was %d", MIN_KEY_SIZE_BITS, size);

    AutoSeededRandomPool osrng(false);
    SigningKey *signer = reinterpret_cast<SigningKey*>(SigningKey_new(&SigningKey_type, NULL, NULL));
    if (signer == NULL)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(osrng, size);
    return reinterpret_cast<PyObject*>(signer);
}

static char generate__doc__[] = "\
Create a signing key using the operating system's random number generator.\n\
";

static PyObject *
create_verifying_key_from_string(PyObject *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedverifyingkey",
        NULL
    };
    const char *serializedverifyingkey;
    size_t serializedverifyingkeysize;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#", const_cast<char**>(kwlist), &serializedverifyingkey, &serializedverifyingkeysize))
        return NULL;

    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_new(&VerifyingKey_type, NULL, NULL));
    if (verifier == NULL)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedverifyingkey), serializedverifyingkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Verifier(ss);
    return reinterpret_cast<PyObject*>(verifier);
}

static char create_verifying_key_from_string__doc__[] = "\
Create a verifying key from its serialized state.\n\
";

static PyObject *
create_signing_key_from_string(PyObject *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedsigningkey",
        NULL
    };
    const char *serializedsigningkey;
    size_t serializedsigningkeysize;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#", const_cast<char**>(kwlist), &serializedsigningkey, &serializedsigningkeysize))
        return NULL;

    SigningKey *verifier = reinterpret_cast<SigningKey*>(SigningKey_new(&SigningKey_type, NULL, NULL));
    if (verifier == NULL)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedsigningkey), serializedsigningkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Signer(ss);
    return reinterpret_cast<PyObject*>(verifier);
}

static char create_signing_key_from_string__doc__[] = "\
Create a signing key from its serialized state.\n\
";

static PyMethodDef rsa_methods[] = { 
    {"generate_from_seed", reinterpret_cast<PyCFunction>(generate_from_seed), METH_VARARGS, generate_from_seed__doc__},
    {"generate", reinterpret_cast<PyCFunction>(generate), METH_VARARGS, generate__doc__},
    {"create_verifying_key_from_string", reinterpret_cast<PyCFunction>(create_verifying_key_from_string), METH_VARARGS, create_verifying_key_from_string__doc__},
    {"create_signing_key_from_string", reinterpret_cast<PyCFunction>(create_signing_key_from_string), METH_VARARGS, create_signing_key_from_string__doc__},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_rsa(void) {
    PyObject *module;
    PyObject *module_dict;

    if (PyType_Ready(&VerifyingKey_type) < 0)
        return;
    if (PyType_Ready(&SigningKey_type) < 0)
        return;

    module = Py_InitModule3("_rsa", rsa_methods, rsa__doc__);
    if (module == NULL)
      return;

    Py_INCREF(&SigningKey_type);
    Py_INCREF(&VerifyingKey_type);

    PyModule_AddObject(module, "SigningKey", (PyObject *)&SigningKey_type);
    PyModule_AddObject(module, "VerifyingKey", (PyObject *)&VerifyingKey_type);

    module_dict = PyModule_GetDict(module);
    rsa_error = PyErr_NewException("_rsa.Error", NULL, NULL);
    PyDict_SetItemString(module_dict, "Error", rsa_error);
}
