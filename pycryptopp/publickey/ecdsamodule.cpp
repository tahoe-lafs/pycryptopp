/**
 * ecdsamodule.cpp -- Python wrappers around Crypto++'s
 * ECDSA(1363)/EMSA1(SHA-256), more precisely: <a
 * href="http://www.weidai.com/scan-mirror/sig.html#ECDSA">ECDSA</a> with GF(P)
 * ("ECP") as the elliptic curve group parameters and SHA-256 as the hash
 * function
 */

#include <Python.h>

#include <math.h>

#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/* from Crypto++ */
#include "filters.h"
#include "osrng.h"
#include "eccrypto.h"
#include "oids.h"

USING_NAMESPACE(CryptoPP)

PyDoc_STRVAR(ecdsa__doc__,
"ecdsa -- ECDSA(1363)/EMSA1(SHA-256) signatures\n\
\n\
To create a new ECDSA signing key from the operating system's random number generator, call generate().\n\
To deserialize an ECDSA signing key from a string, call create_signing_key_from_string().\n\
\n\
To get an ECDSA verifying key from an ECDSA signing key, call get_verifying_key() on the signing key.\n\
To deserialize an ECDSA verifying key from a string, call create_verifying_key_from_string().");

static PyObject *ecdsa_error;

typedef struct {
    PyObject_HEAD

    /* internal */
    ECDSA<ECP, SHA256>::Verifier *k;
} VerifyingKey;

PyDoc_STRVAR(VerifyingKey__doc__,
"an ECDSA verifying key");

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
        return PyErr_Format(ecdsa_error, "Precondition violation: signatures are required to be of size %zu, but it was %zu", sigsize, signaturesize);
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
    "ecdsa.VerifyingKey", /*tp_name*/
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

/** This function is only for internal use by ecdsamodule.cpp. */
static VerifyingKey*
VerifyingKey_construct() {
    VerifyingKey *self = reinterpret_cast<VerifyingKey*>(VerifyingKey_type.tp_alloc(&VerifyingKey_type, 0));
    if (!self)
        return NULL;
    self->k = NULL;
    return self;
}

PyDoc_STRVAR(SigningKey__doc__,
"an ECDSA signing key");

typedef struct {
    PyObject_HEAD

    /* internal */
    ECDSA<ECP, SHA256>::Signer *k;
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

    verifier->k = new ECDSA<ECP, SHA256>::Verifier(*(self->k));
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(SigningKey_get_verifying_key__doc__,
"Return the corresponding verifying key.");

static PyObject *
SigningKey_serialize(SigningKey *self, PyObject *dummy) {
    Py_ssize_t len = self->k->GetKey().GetGroupParameters().GetSubgroupOrder().ByteCount();
    PyObject* result = PyString_FromStringAndSize(NULL, len);

    const DL_PrivateKey_EC<ECP>& privkey = dynamic_cast<const DL_PrivateKey_EC<ECP>&>(self->k->GetPrivateKey());

    privkey.GetPrivateExponent().Encode(reinterpret_cast<byte*>(PyString_AS_STRING(result)), len);

    return result;
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
    "ecdsa.SigningKey", /*tp_name*/
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

/** This function is only for internal use by ecdsamodule.cpp. */
static SigningKey*
SigningKey_construct() {
    SigningKey *self = reinterpret_cast<SigningKey*>(SigningKey_type.tp_alloc(&SigningKey_type, 0));
    if (!self)
        return NULL;
    self->k = NULL;
    return self;
}

/* The smaller ECDSA key size that pycryptopp supports -- you should do your 
   own research, and I recommend http://keylength.com , but basically this is 
   probably secure for most purposes for at least the next few years, and 
   possibly for longer. */
static const int SMALL_KEY_SIZE_BITS=192;

/* The larger ECDSA key size that pycryptopp supports -- you should do your 
   own research, and I recommend http://keylength.com , but basically this is 
   probably secure for many years, unless there is a surprising breakthrough in 
   the theory of elliptic curve cryptography. */
static const int LARGE_KEY_SIZE_BITS=521;

static PyObject *
generate(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "sizeinbits",
        NULL
    };
    int sizeinbits;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "i:generate", const_cast<char**>(kwlist), &sizeinbits))
        return NULL;

    if (sizeinbits != SMALL_KEY_SIZE_BITS && sizeinbits != LARGE_KEY_SIZE_BITS)
        return PyErr_Format(ecdsa_error, "Precondition violation: size in bits is required to be either %d or %d, but it was %d", SMALL_KEY_SIZE_BITS, LARGE_KEY_SIZE_BITS, sizeinbits);

    AutoSeededRandomPool osrng(false);
    SigningKey *signer = SigningKey_construct();
    if (!signer)
        return NULL;

    OID curve;
    if (sizeinbits == 192)
        curve = ASN1::secp192r1();
    else
        curve = ASN1::secp521r1();

    signer->k = new ECDSA<ECP, SHA256>::Signer(osrng, curve);
    if (!signer->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(signer);
}

PyDoc_STRVAR(generate__doc__,
"Create a signing key using the operating system's random number generator.\n\
\n\
@param sizeinbits size of the key in bits\n\
\n\
@precondition sizeinbits in (192, 521)");

static PyObject *
create_verifying_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
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

    verifier->k = new ECDSA<ECP, SHA256>::Verifier(ss);
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(create_verifying_key_from_string__doc__,
"Create a verifying key from its serialized state.");

static PyObject *
create_signing_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = {
        "serializedsigningkey",
        NULL
    };
    const char *serializedsigningkey;
    Py_ssize_t serializedsigningkeysize = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#:create_signing_key_from_string", const_cast<char**>(kwlist), &serializedsigningkey, &serializedsigningkeysize))
        return NULL;
    if (serializedsigningkeysize != 24 && serializedsigningkeysize != 66)
        return PyErr_Format(ecdsa_error, "Precondition violation: size in bytes of the serialized signing key is required to be either %d (for %d-bit keys) or %d (for %d-bit keys), but it was %d", 24, SMALL_KEY_SIZE_BITS, 66, LARGE_KEY_SIZE_BITS, serializedsigningkeysize);


    SigningKey *verifier = SigningKey_construct();
    if (!verifier)
        return NULL;

    OID curve;
    if (serializedsigningkeysize == 24)
        curve = ASN1::secp192r1();
    else
        curve = ASN1::secp521r1();
    Integer privexponent(reinterpret_cast<const byte*>(serializedsigningkey), serializedsigningkeysize);

    verifier->k = new ECDSA<ECP, SHA256>::Signer(curve, privexponent);
    if (!verifier->k)
        return PyErr_NoMemory();
    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(create_signing_key_from_string__doc__,
"Create a signing key from its serialized state.");

static PyMethodDef ecdsa_functions[] = {
    {"generate", reinterpret_cast<PyCFunction>(generate), METH_KEYWORDS, generate__doc__},
    {"create_verifying_key_from_string", reinterpret_cast<PyCFunction>(create_verifying_key_from_string), METH_KEYWORDS, create_verifying_key_from_string__doc__},
    {"create_signing_key_from_string", reinterpret_cast<PyCFunction>(create_signing_key_from_string), METH_KEYWORDS, create_signing_key_from_string__doc__},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initecdsa(void) {
    PyObject *module;
    PyObject *module_dict;

    if (PyType_Ready(&VerifyingKey_type) < 0)
        return;
    if (PyType_Ready(&SigningKey_type) < 0)
        return;

    module = Py_InitModule3("ecdsa", ecdsa_functions, ecdsa__doc__);
    if (!module)
      return;

    Py_INCREF(&SigningKey_type);
    Py_INCREF(&VerifyingKey_type);

    PyModule_AddObject(module, "SigningKey", (PyObject *)&SigningKey_type);
    PyModule_AddObject(module, "VerifyingKey", (PyObject *)&VerifyingKey_type);

    module_dict = PyModule_GetDict(module);
    ecdsa_error = PyErr_NewException(const_cast<char*>("ecdsa.Error"), NULL, NULL);
    PyDict_SetItemString(module_dict, "Error", ecdsa_error);
}
