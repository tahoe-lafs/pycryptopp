/**
 * rsamodule.cpp -- Python wrappers around Crypto++'s RSA-PSS-SHA256
 * more precisely:
 * <a href="http://www.weidai.com/scan-mirror/sig.html#sem_PSS-MGF1">PSS-MGF1</a>
 * with RSA as the public key algorithm and SHA-256 as the hash function
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

#include "rsamodule.hpp"

/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/filters.h>
#include <cryptopp/osrng.h>
#include <cryptopp/pssr.h>
#include <cryptopp/rsa.h>
#else
#include <embeddedcryptopp/filters.h>
#include <embeddedcryptopp/osrng.h>
#include <embeddedcryptopp/pssr.h>
#include <embeddedcryptopp/rsa.h>
#endif

USING_NAMESPACE(CryptoPP)

static const char*const rsa___doc__ = "_rsa -- RSA-PSS-SHA256 signatures\n\
\n\
To create a new RSA signing key from the operating system's random number generator, call generate().\n\
To deserialize an RSA signing key from a string, call create_signing_key_from_string().\n\
\n\
To get an RSA verifying key from an RSA signing key, call get_verifying_key() on the signing key.\n\
To deserialize an RSA verifying key from a string, call create_verifying_key_from_string().";

static PyObject *rsa_error;

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Verifier *k;
} VerifyingKey;

PyDoc_STRVAR(VerifyingKey__doc__,
"an RSA verifying key");

static void
VerifyingKey_dealloc(VerifyingKey* self) {
    if (self->k)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
VerifyingKey_verify(VerifyingKey *self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = { "msg", "signature", NULL };
    const char *msg;
    Py_ssize_t msgsize;
    const char *signature;
    Py_ssize_t signaturesize = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#t#:verify", const_cast<char**>(kwlist), &msg, &msgsize, &signature, &signaturesize))
        return NULL;
    assert (msgsize >= 0);
    assert (signaturesize >= 0);

    Py_ssize_t sigsize = self->k->SignatureLength();
    if (sigsize != signaturesize)
        return PyErr_Format(rsa_error, "Precondition violation: signatures are required to be of size %zu, but it was %zu", sigsize, signaturesize);
    assert (sigsize >= 0);

    assert (signaturesize == sigsize);

    if (self->k->VerifyMessage(reinterpret_cast<const byte*>(msg), msgsize, reinterpret_cast<const byte*>(signature), signaturesize))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyDoc_STRVAR(VerifyingKey_verify__doc__,
"Return whether the signature is a valid signature on the msg.");

static PyObject *
VerifyingKey_serialize(VerifyingKey *self, PyObject *dummy) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(VerifyingKey_serialize__doc__,
"Return a string containing the key material.  The string can be passed to \n\
create_verifying_key_from_string() to instantiate a new copy of this key.");

static PyMethodDef VerifyingKey_methods[] = {
    {"verify", reinterpret_cast<PyCFunction>(VerifyingKey_verify), METH_KEYWORDS, VerifyingKey_verify__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(VerifyingKey_serialize), METH_NOARGS, VerifyingKey_serialize__doc__},
    {NULL},
};

static PyTypeObject VerifyingKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_rsa.VerifyingKey", /*tp_name*/
    sizeof(VerifyingKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    reinterpret_cast<destructor>(VerifyingKey_dealloc), /*tp_dealloc*/
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
};

/** This function is only for internal use by rsamodule.cpp. */
static VerifyingKey*
VerifyingKey_construct() {
    VerifyingKey *self = reinterpret_cast<VerifyingKey*>(VerifyingKey_type.tp_alloc(&VerifyingKey_type, 0));
    if (!self)
        return NULL;
    self->k = NULL;
    return self;
}

PyDoc_STRVAR(SigningKey__doc__,
"an RSA signing key");

typedef struct {
    PyObject_HEAD

    /* internal */
    RSASS<PSS, SHA256>::Signer *k;
} SigningKey;

static void
SigningKey_dealloc(SigningKey* self) {
    if (self->k)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static PyObject *
SigningKey_sign(SigningKey *self, PyObject *msgobj) {
    const char *msg;
    Py_ssize_t msgsize;
    PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), reinterpret_cast<Py_ssize_t*>(&msgsize));
    assert (msgsize >= 0);

    Py_ssize_t sigsize = self->k->SignatureLength();
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, sigsize));
    if (!result)
        return NULL;
    assert (sigsize >= 0);

    AutoSeededRandomPool randpool(false);
    Py_ssize_t siglengthwritten = self->k->SignMessage(
        randpool,
        reinterpret_cast<const byte*>(msg),
        msgsize,
        reinterpret_cast<byte*>(PyString_AS_STRING(result)));
    if (siglengthwritten < sigsize)
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, "SigningKey_sign", "INTERNAL ERROR: signature was shorter than expected.");
    else if (siglengthwritten > sigsize) {
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, "SigningKey_sign", "INTERNAL ERROR: signature was longer than expected, so invalid memory was overwritten.");
        abort();
    }
    assert (siglengthwritten >= 0);

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(SigningKey_sign__doc__,
"Return a signature on the argument.");

static PyObject *
SigningKey_get_verifying_key(SigningKey *self, PyObject *dummy) {
    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_construct());
    if (!verifier)
        return NULL;

    verifier->k = new RSASS<PSS, SHA256>::Verifier(*(self->k));
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(SigningKey_get_verifying_key__doc__,
"Return the corresponding verifying key.");

static PyObject *
SigningKey_serialize(SigningKey *self, PyObject *dummy) {
    std::string outstr;
    StringSink ss(outstr);
    self->k->DEREncode(ss);
    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(outstr.c_str(), outstr.size()));
    if (!result)
        return NULL;

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(SigningKey_serialize__doc__,
"Return a string containing the key material.  The string can be passed to \n\
create_signing_key_from_string() to instantiate a new copy of this key.");

static PyMethodDef SigningKey_methods[] = {
    {"sign", reinterpret_cast<PyCFunction>(SigningKey_sign), METH_O, SigningKey_sign__doc__},
    {"get_verifying_key", reinterpret_cast<PyCFunction>(SigningKey_get_verifying_key), METH_NOARGS, SigningKey_get_verifying_key__doc__},
    {"serialize", reinterpret_cast<PyCFunction>(SigningKey_serialize), METH_NOARGS, SigningKey_serialize__doc__},
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
    SigningKey_methods             /* tp_methods */
};

/** This function is only for internal use by rsamodule.cpp. */
static SigningKey*
SigningKey_construct() {
    SigningKey *self = reinterpret_cast<SigningKey*>(SigningKey_type.tp_alloc(&SigningKey_type, 0));
    if (!self)
        return NULL;
    self->k = NULL;
    return self;
}

// static const int MIN_KEY_SIZE_BITS=3675; /* according to Lenstra 2001 "Unbelievable security: Matching AES security using public key systems", you should use RSA keys of length 3675 bits if you want it to be as hard to factor your RSA key as to brute-force your AES-128 key in the year 2030. */
static const int MIN_KEY_SIZE_BITS=522; /* minimum that can do PSS-SHA256 -- totally insecure and allowed only for faster unit tests */

PyObject *
rsa_generate(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "sizeinbits",
        NULL
    };
    int sizeinbits;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "i:generate", const_cast<char**>(kwlist), &sizeinbits))
        return NULL;

    if (sizeinbits < MIN_KEY_SIZE_BITS)
        return PyErr_Format(rsa_error, "Precondition violation: size in bits is required to be >= %d, but it was %d", MIN_KEY_SIZE_BITS, sizeinbits);

    AutoSeededRandomPool osrng(false);
    SigningKey *signer = SigningKey_construct();
    if (!signer)
        return NULL;
    signer->k = new RSASS<PSS, SHA256>::Signer(osrng, sizeinbits);
    if (!signer->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(signer);
}

const char*const rsa_generate__doc__ = "Create a signing key using the operating system's random number generator.\n\
\n\
@param sizeinbits size of the key in bits\n\
\n\
@precondition sizeinbits >= 522";

PyObject *
rsa_create_verifying_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedverifyingkey",
        NULL
    };
    const char *serializedverifyingkey;
    Py_ssize_t serializedverifyingkeysize = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#:create_verifying_key_from_string", const_cast<char**>(kwlist), &serializedverifyingkey, &serializedverifyingkeysize))
        return NULL;
    assert (serializedverifyingkeysize >= 0);

    VerifyingKey *verifier = reinterpret_cast<VerifyingKey*>(VerifyingKey_construct());
    if (!verifier)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedverifyingkey), serializedverifyingkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Verifier(ss);
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

const char*const rsa_create_verifying_key_from_string__doc__ = "Create a verifying key from its serialized state.";

PyObject *
rsa_create_signing_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedsigningkey",
        NULL
    };
    const char *serializedsigningkey;
    Py_ssize_t serializedsigningkeysize = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#:create_signing_key_from_string", const_cast<char**>(kwlist), &serializedsigningkey, &serializedsigningkeysize))
        return NULL;
    assert (serializedsigningkeysize >= 0);

    SigningKey *verifier = SigningKey_construct();
    if (!verifier)
        return NULL;
    StringSource ss(reinterpret_cast<const byte*>(serializedsigningkey), serializedsigningkeysize, true);

    verifier->k = new RSASS<PSS, SHA256>::Signer(ss);
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

const char*const rsa_create_signing_key_from_string__doc__ = "Create a signing key from its serialized state.";

void
init_rsa(PyObject*const module) {
    VerifyingKey_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&VerifyingKey_type) < 0)
        return;
    Py_INCREF(&VerifyingKey_type);
    PyModule_AddObject(module, "rsa_VerifyingKey", (PyObject *)&VerifyingKey_type);

    SigningKey_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&SigningKey_type) < 0)
        return;
    Py_INCREF(&SigningKey_type);
    PyModule_AddObject(module, "rsa_SigningKey", (PyObject *)&SigningKey_type);

    rsa_error = PyErr_NewException(const_cast<char*>("_rsa.Error"), NULL, NULL);
    PyModule_AddObject(module, "rsa_Error", rsa_error);

    PyModule_AddStringConstant(module, "rsa___doc__", const_cast<char*>(rsa___doc__));
}
