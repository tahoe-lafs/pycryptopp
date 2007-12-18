/**
 * aesmodule.cpp -- Python wrappers around Crypto++'s AES-CTR
 */

#include <Python.h>

#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/* from Crypto++ */
#ifdef USE_NAME_CRYPTO_PLUS_PLUS
#include "crypto++/modes.h"
#include "crypto++/aes.h"
#else
#include "cryptopp/modes.h"
#include "cryptopp/aes.h"
#endif

static char aes__doc__[] = "\
aes counter mode cipher\
";

static PyObject *aes_error;

typedef struct {
    PyObject_HEAD

    /* internal */
	CryptoPP::CTR_Mode<CryptoPP::AES>::Encryption * e;
} AES;

PyDoc_STRVAR(AES__doc__,
"An AES cipher object.\n\
\n\
This object encrypts/decrypts in CTR mode, using a counter that is initialized \
to zero when you instantiate the object.  Successive calls to .process() will \
use the current counter value and increment it.\
\n\
@param key: the symmetric encryption key\
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
    size_t msgsize;
    if (PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), reinterpret_cast<Py_ssize_t*>(&msgsize)))
        return NULL;

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
    static char *kwlist[] = { "key", NULL };
    const char *key = NULL;
    size_t keysize;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#", const_cast<char**>(kwlist), &key, &keysize))
        return -1;
    if (keysize != static_cast<size_t>(CryptoPP::AES::DEFAULT_KEYLENGTH)) {
        PyErr_Format(aes_error, "Precondition violation: key size is expected to be the default for AES, which is %d, but a key of size %d was provided.", CryptoPP::AES::DEFAULT_KEYLENGTH, keysize);
        return -1;
    }

    byte iv[CryptoPP::AES::DEFAULT_KEYLENGTH];
    memset(iv, 0, CryptoPP::AES::DEFAULT_KEYLENGTH);
    reinterpret_cast<AES*>(self)->e = new CryptoPP::CTR_Mode<CryptoPP::AES>::Encryption(reinterpret_cast<const byte*>(key), keysize, iv);
    if (!reinterpret_cast<AES*>(self)->e) {
        PyErr_NoMemory();
        return -1;
    }
    return 0;
}

static PyTypeObject AES_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "aes.AES", /*tp_name*/
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

static struct PyMethodDef aes_functions[] = {
    {NULL,     NULL}            /* Sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
initaes(void) {
    PyObject *module;
    PyObject *module_dict;

    if (PyType_Ready(&AES_type) < 0)
        return;

    module = Py_InitModule3("aes", aes_functions, aes__doc__);
    if (!module)
      return;

    Py_INCREF(&AES_type);

    PyModule_AddObject(module, "AES", (PyObject *)&AES_type);

    module_dict = PyModule_GetDict(module);
    aes_error = PyErr_NewException("aes.Error", NULL, NULL);
    PyDict_SetItemString(module_dict, "Error", aes_error);
}
