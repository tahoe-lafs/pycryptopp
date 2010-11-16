/**
 * aesmodule.cpp -- Python wrappers around Crypto++'s AES-CTR
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

#include "aesmodule.hpp"


/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/modes.h>
#include <cryptopp/aes.h>
#else
#include <embeddedcryptopp/modes.h>
#include <embeddedcryptopp/aes.h>
#endif

static const char*const aes___doc__ = "_aes counter mode cipher\n\
You are advised to run aes.start_up_self_test() after importing this module.";

static PyObject *aes_error;

typedef struct {
    PyObject_HEAD

    /* internal */
    CryptoPP::CTR_Mode<CryptoPP::AES>::Encryption * e;
} AES;

PyDoc_STRVAR(AES__doc__,
"An AES cipher object.\n\
\n\
This object encrypts/decrypts in CTR mode, using a counter that is initialized\n\
to zero when you instantiate the object.  Successive calls to .process() will\n\
use the current counter value and increment it.\n\
\n\
Note that you must never encrypt different data with the same key, or you\n\
will leak information about your data.  Therefore the only safe way to use\n\
this class is to use a different AES key every time you are going to encrypt\n\
different data.  A good way to generate a different AES key is using AES, like\n\
this:\n\
\n\
    onetimekey = AES(key=masterkey).process(nonce)\n\
\n\
Where 'masterkey' is a secret key used only for generating onetimekeys this\
way, and 'nonce' is a value that is guaranteed to never repeat.\
\n\
@param key: the symmetric encryption key; a string of exactly 16 bytes\
");

static PyObject *
AES_process(AES* self, PyObject* msgobj) {
    if (!PyString_CheckExact(msgobj)) {
        PyStringObject* typerepr = reinterpret_cast<PyStringObject*>(PyObject_Repr(reinterpret_cast<PyObject*>(msgobj->ob_type)));
        if (typerepr) {
            PyErr_Format(aes_error, "Precondition violation: you are required to pass a Python string object (not a unicode, a subclass of string, or anything else), but you passed %s.", PyString_AS_STRING(reinterpret_cast<PyObject*>(typerepr)));
            Py_DECREF(typerepr);
        } else
            PyErr_Format(aes_error, "Precondition violation: you are required to pass a Python string object (not a unicode, a subclass of string, or anything else).");
        return NULL;
    }

    const char *msg;
    Py_ssize_t msgsize;
    if (PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), &msgsize))
        return NULL;
    assert (msgsize >= 0);

    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, msgsize));
    if (!result)
        return NULL;

    self->e->ProcessData(reinterpret_cast<byte*>(PyString_AS_STRING(result)), reinterpret_cast<const byte*>(msg), msgsize);
    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(AES_process__doc__,
"Encrypt or decrypt the next bytes, returning the result.");

static PyMethodDef AES_methods[] = {
    {"process", reinterpret_cast<PyCFunction>(AES_process), METH_O, AES_process__doc__},
    {NULL},
};

static PyObject *
AES_new(PyTypeObject* type, PyObject *args, PyObject *kwdict) {
    AES* self = reinterpret_cast<AES*>(type->tp_alloc(type, 0));
    if (!self)
        return NULL;
    self->e = NULL;
    return reinterpret_cast<PyObject*>(self);
}

static void
AES_dealloc(PyObject* self) {
    if (reinterpret_cast<AES*>(self)->e)
        delete reinterpret_cast<AES*>(self)->e;
    self->ob_type->tp_free(self);
}

static int
AES_init(PyObject* self, PyObject *args, PyObject *kwdict) {
    static const char *kwlist[] = { "key", "iv", NULL };
    const char *key = NULL;
    Py_ssize_t keysize = 0;
    const char *iv = NULL;
    const char defaultiv[CryptoPP::AES::BLOCKSIZE] = {0};
    Py_ssize_t ivsize = 0;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#|t#:AES.__init__", const_cast<char**>(kwlist), &key, &keysize, &iv, &ivsize))
        return -1;
    assert (keysize >= 0);
    assert (ivsize >= 0);

    if (!iv)
        iv = defaultiv;
    try {
        reinterpret_cast<AES*>(self)->e = new CryptoPP::CTR_Mode<CryptoPP::AES>::Encryption(reinterpret_cast<const byte*>(key), keysize, reinterpret_cast<const byte*>(iv));
    } catch (CryptoPP::InvalidKeyLength le) {
        PyErr_Format(aes_error, "Precondition violation: you are required to pass a valid key size.  Crypto++ gave this exception: %s", le.what());
        return -1;
    }
    if (!reinterpret_cast<AES*>(self)->e) {
        PyErr_NoMemory();
        return -1;
    }
    return 0;
}

static PyTypeObject AES_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "_aes.AES", /*tp_name*/
    sizeof(AES),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    AES_dealloc, /*tp_dealloc*/
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
    AES__doc__,           /* tp_doc */
    0,		               /* tp_traverse */
    0,		               /* tp_clear */
    0,		               /* tp_richcompare */
    0,		               /* tp_weaklistoffset */
    0,		               /* tp_iter */
    0,		               /* tp_iternext */
    AES_methods,      /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    AES_init,               /* tp_init */
    0,                         /* tp_alloc */
    AES_new,                /* tp_new */
};

void
init_aes(PyObject*const module) {
    if (PyType_Ready(&AES_type) < 0)
        return;
    Py_INCREF(&AES_type);
    PyModule_AddObject(module, "aes_AES", (PyObject *)&AES_type);

    aes_error = PyErr_NewException(const_cast<char*>("_aes.Error"), NULL, NULL);
    PyModule_AddObject(module, "aes_Error", aes_error);

    PyModule_AddStringConstant(module, "aes___doc__", const_cast<char*>(aes___doc__));
}
