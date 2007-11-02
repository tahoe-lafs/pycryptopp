/**
 * _rsamodule.cpp -- Python wrappers around Crypto++'s RSA-PSS-SHA256
 * more precisely:
 * <a href="http://www.weidai.com/scan-mirror/sig.html#sem_PSS-MGF1">PSS-MGF1</a>* <a href="http://www.weidai.com/scan-mirror/sig.html#sem_PSS-MGF1">PSS-MGF1</a>
 */

#include <Python.h>

#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/* from Crypto++ */
#ifdef USE_NAME_CRYPTO_PLUS_PLUS
// For Debian (and Ubuntu, and their many derivatives)
#include "crypto++/filters.h"
#include "crypto++/osrng.h"
#include "crypto++/pssr.h"
#include "crypto++/randpool.h"
#include "crypto++/rsa.h"
#else
// For upstream Crypto++ library
#include "cryptopp/filters.h"
#include "cryptopp/osrng.h"
#include "cryptopp/pssr.h"
#include "cryptopp/randpool.h"
#include "cryptopp/rsa.h"
#endif

USING_NAMESPACE(CryptoPP)

static char rsa__doc__[] = "\
pycryptopp - Python wrappers around Crypto++ \n\
\n\
To create a new RSA signing key from a seed, call generate_from_seed().\n\
To create a new RSA signing key from the operating system's random number generator, call generate().\n\
To deserialize an RSA signing key from a string, call create_signing_key_from_string().\n\
\n\
To get an RSA verifying key from an RSA signing key, call get_verifying_key() on the signing key.\n\
To deserialize an RSA verifying key from a string, call create_verifying_key_from_string().\n\
\n\
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
    VerifyingKey *self;

    self = (VerifyingKey*)type->tp_alloc(type, 0);

    return (PyObject *)self;
}

/* This is not intended to be used. */
/* XXX What's the polite way to tell Python that nobody should use this? */
static int
VerifyingKey_init(VerifyingKey *self, PyObject *args, PyObject *kwdict) {
    return 0;
}

static void
VerifyingKey_dealloc(VerifyingKey* self) {
    self->ob_type->tp_free((PyObject*)self);
}

static PyMethodDef VerifyingKey_methods[] = {
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
    (initproc)VerifyingKey_init,      /* tp_init */
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
    SigningKey *self;

    self = (SigningKey*)type->tp_alloc(type, 0);

    return (PyObject *)self;
}

/* This is not intended to be used. */
/* XXX What's the polite way to tell Python that nobody should use this? */
static int
SigningKey_init(SigningKey *self, PyObject *args, PyObject *kwdict) {
    return 0;
}

static void
SigningKey_dealloc(SigningKey* self) {
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SigningKey_sign(SigningKey *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "msg",
        NULL
    };
    const char *msg;
    int msgsize;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "s#", const_cast<char**>(kwlist), &msg, &msgsize))
        return NULL;

    assert (msgsize >= 0);

    size_t sigsize = self->k->SignatureLength();
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, sigsize));
    if (!result)
        return NULL;

    AutoSeededRandomPool osrng;
    ArraySink* arraysinkp = new ArraySink(reinterpret_cast<byte*>(PyString_AS_STRING(result)), sigsize);
    SignerFilter* signerfilterp = new SignerFilter(osrng, *(self->k), arraysinkp, false);
    StringSource(reinterpret_cast<const byte*>(msg), static_cast<size_t>(msgsize), true, signerfilterp);

    return reinterpret_cast<PyObject*>(result);
}

static char RSASigningKey_sign__doc__[] = "\
Return a signature on the argument.\n\
";

static PyMethodDef SigningKey_methods[] = {
    {"sign", reinterpret_cast<PyCFunction>(SigningKey_sign), METH_VARARGS, RSASigningKey_sign__doc__},
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
    (initproc)SigningKey_init,      /* tp_init */
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
\n\
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

    AutoSeededRandomPool osrng;
    SigningKey *signer = reinterpret_cast<SigningKey*>(SigningKey_new(&SigningKey_type, NULL, NULL));
    if (signer == NULL)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(osrng, size);
    return reinterpret_cast<PyObject*>(signer);
}

static char generate__doc__[] = "\
Create a signing key using the operating system's random number generator.\n\
\n\
";

static PyMethodDef rsa_methods[] = { 
    {"generate_from_seed", reinterpret_cast<PyCFunction>(generate_from_seed), METH_VARARGS, generate_from_seed__doc__},
    {"generate", reinterpret_cast<PyCFunction>(generate), METH_VARARGS, generate__doc__},
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
