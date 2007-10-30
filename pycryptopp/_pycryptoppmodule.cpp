/**
 * pycryptopp -- Python wrappers around Crypto++
 */

#include <Python.h>

#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

/* from Crypto++ */
#include "cryptopp/rsa.h"

static PyObject *pycryptopp_error;
static PyObject *raise_pycryptopp_error (const char *format, ...);

static char pycryptopp__doc__[] = "\
pycryptopp - Python wrappers around Crypto++ \n\
";

/* NOTE: if the complete expansion of the args (by vsprintf) exceeds 1024 then memory will be invalidly overwritten. */
static PyObject *
raise_pycryptopp_error(const char *format, ...) {
    char exceptionMsg[1024];
    va_list ap;

    va_start (ap, format);
    vsprintf (exceptionMsg, format, ap); /* Make sure that this can't exceed 1024 chars! */
    va_end (ap);
    exceptionMsg[1023]='\0';
    PyErr_SetString (pycryptopp_error, exceptionMsg);
    return NULL;
}

static char RSA_key__doc__[] = "\
Holds an RSA public key, and possibly the private key as well. \n\
";

typedef struct {
    PyObject_HEAD

    /* expose these */
    //xxx

    /* internal */
    //xxx
} RSA_key;

static const int MIN_RSA_KEY_SIZE_BITS=16; /* by experimentation, Crypto++ gives an exception for sizes fewer than 16 bits. */

static PyObject *
generate(PyObject *self, PyObject *args, PyObject *kwdict) {
    static char *kwlist[] = {
        "size",
        NULL
    };
    int size;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "i", kwlist, &size))
        return NULL;
    if (size < MIN_RSA_KEY_SIZE_BITS) {
        raise_pycryptopp_error("Precondition violation: size in bits is required to be >= 16, but it was %d", size);
        return NULL;
    }

    printf("WHEEE!\n");

    Py_INCREF(Py_None);
    return Py_None;
}

static PyMethodDef pycryptopp_methods[] = { 
    {"generate", (PyCFunction)generate, METH_VARARGS | METH_KEYWORDS, "Generate an RSA key."},
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC	/* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_pycryptopp(void) {
    PyObject *module;
    PyObject *module_dict;

    //XXXif (PyType_Ready(&Encoder_type) < 0)
//XXX        return;
//XXX    if (PyType_Ready(&Decoder_type) < 0)
//XXX        return;

    module = Py_InitModule3("_pycryptopp", pycryptopp_methods, pycryptopp__doc__);
    if (module == NULL)
      return;

//XXXxxx    Py_INCREF(&Encoder_type);
//XXXxxx    Py_INCREF(&Decoder_type);

//XXXxxx    PyModule_AddObject(module, "Encoder", (PyObject *)&Encoder_type);
//XXXxxx    PyModule_AddObject(module, "Decoder", (PyObject *)&Decoder_type);

    module_dict = PyModule_GetDict(module);
    pycryptopp_error = PyErr_NewException("_pycryptopp.Error", NULL, NULL);
    PyDict_SetItemString(module_dict, "Error", pycryptopp_error);
}

