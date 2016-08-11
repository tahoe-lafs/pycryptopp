/**
 * chacha20module.cpp -- Python wrappers around Crypto++'s chacha20
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

#include "chacha20module.hpp"

#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/chacha.h>
#else
#include <src-cryptopp/chacha.h>
#endif

static const char* const chacha20__doc__ = "_chacha20 cipher";

static PyObject *chacha20_error;

typedef struct {
	PyObject_HEAD

	/* internal */
	//CryptoPP::CTR_Mode<CryptoPP::ChaCha20>::Encryption *e;
	CryptoPP::ChaCha20::Encryption *e;
} ChaCha20;

PyDoc_STRVAR(ChaCha20__doc__,
"An ChaCha20 cipher object.\n\
\n\
This object encrypts/decrypts in CTR mode, using a counter that is initialized\n\
to zero when you instantiate the object. Successive calls to .process() will \n\
use the current counter and increment it.\n\
\n\
");

static PyObject *ChaCha20_process(ChaCha20* self, PyObject* msgobj) {
	if(!PyString_CheckExact(msgobj)) {
		PyStringObject* typerepr = reinterpret_cast<PyStringObject*>(PyObject_Repr(reinterpret_cast<PyObject*>(msgobj->ob_type)));
		if (typerepr) {
			PyErr_Format(chacha20_error, "Precondition violation: you are required to pass a Python string object (not a unicode, a subclass of string, or anything else), but you passed %s.", PyString_AS_STRING(reinterpret_cast<PyObject*>(typerepr)));
			Py_DECREF(typerepr);
		} else
			PyErr_Format(chacha20_error, "Precondition violation: you are required to pass a Python string object (not a unicode, a subclass of string, or anything else).");
		return NULL;
	}

	const char* msg;
	Py_ssize_t msgsize;
	if (PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), &msgsize))
		return NULL;
	assert (msgsize >= 0);

	PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, msgsize));
	if (!result)
		return NULL;

	self->e->ProcessString(reinterpret_cast<byte*>(PyString_AS_STRING(result)), reinterpret_cast<const byte*>(msg), msgsize);
	return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(ChaCha20_process__doc__,
"Encrypt or decrypt the next bytes, returning the result.");

static PyMethodDef ChaCha20_methods[] = {
	{"process", reinterpret_cast<PyCFunction>(ChaCha20_process), METH_O, ChaCha20_process__doc__},
	{NULL},
};

static PyObject* ChaCha20_new(PyTypeObject* type, PyObject *args, PyObject *kwdict) {
	ChaCha20* self = reinterpret_cast<ChaCha20*>(type->tp_alloc(type, 0));
	if (!self)
		return NULL;
	self->e = NULL;
	return reinterpret_cast<PyObject*>(self);
}

static void ChaCha20_dealloc(PyObject* self) {
	if (reinterpret_cast<ChaCha20*>(self)->e)
		delete reinterpret_cast<ChaCha20*>(self)->e;
	self->ob_type->tp_free(self);
}

static int ChaCha20_init(PyObject* self, PyObject *args, PyObject *kwdict) {
	static const char *kwlist[] = { "key", "iv", NULL};
	const char *key = NULL;
	Py_ssize_t keysize = 0;
	const char *iv = NULL;
	const char defaultiv[24] = {0};
	Py_ssize_t ivsize = 0;
	if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#|t#:ChaCha20.__init__", const_cast<char**>(kwlist), &key, &keysize, &iv, &ivsize))
		return -1;
	assert (keysize >= 0);
	assert (ivsize >= 0);

	if (!iv)
		iv = defaultiv;
        else if (ivsize != 24) {
            PyErr_Format(chacha20_error, "Precondition violation: if an IV is passed, it must be exactly 24 bytes, not %d", ivsize);
            return -1;
        }

	try {
		reinterpret_cast<ChaCha20*>(self)->e = new CryptoPP::ChaCha20::Encryption(reinterpret_cast<const byte*>(key), keysize, reinterpret_cast<const byte*>(iv));
	}
	catch (CryptoPP::InvalidKeyLength le)
	{
	        PyErr_Format(chacha20_error, "Precondition violation: you are required to pass a valid key size.  Crypto++ gave this exception: %s", le.what());
        	return -1;
	}
	if (!reinterpret_cast<ChaCha20*>(self)->e)
	{
		PyErr_NoMemory();
		return -1;
	}
	return 0;
}


static PyTypeObject ChaCha20_type = {
	PyObject_HEAD_INIT(NULL)
	0,                       /*ob_size*/
	"_xsalsa.ChaCha20",        /*tp_name*/
	sizeof(ChaCha20),	 /*tp_basicsize*/
	0,                       /*tp_itemsize*/
	ChaCha20_dealloc,          /*tp_dealloc*/
	0,			 /*tp_print*/
	0, 			 /*tp_getattr*/
	0,  			 /*tp_setattr*/
	0,  			 /*tp_compare*/
	0,  			 /*tp_repr*/
	0,   			 /*tp_as_number*/
	0,   			 /*tp_as_sequence*/
	0,   			 /*tp_as_mapping*/
	0,    			 /*tp_hash*/
	0,   			 /*tp_call*/
	0,     			 /*tp_str*/
	0,   			 /*tp_getattro*/
	0,    			 /*tp_setattro*/
	0, 			 /*tp_as_buffer*/
	Py_TPFLAGS_DEFAULT | Py_TPFLAGS_BASETYPE, /*tp_flags*/
	ChaCha20__doc__,  	 /*tp_doc*/
	0,   	 		 /*tp_traverse*/
	0,   			 /*tp_clear*/
	0,      		 /*tp_richcompare*/
	0,   			 /*tp_weaklistoffset*/
	0,   			 /*tp_iter*/
	0,   			 /*tp_iternext*/
	ChaCha20_methods,  	 /*tp_methods*/
	0,   			 /*tp_members*/
	0,    			 /*tp_getset*/
	0,   			 /*tp_base*/
	0,   			 /*tp_dict*/
	0,   			 /*tp_descr_get*/
	0,   			 /*tp_descr_set*/
	0,   			 /*tp_dictoffset*/
	ChaCha20_init, 		 /*tp_init*/
	0,   			 /*tp_alloc*/
	ChaCha20_new,   		 /*tp_new*/
};

void init_chacha20(PyObject*const module)
{
	if (PyType_Ready(&ChaCha20_type) < 0)
		return;
	Py_INCREF(&ChaCha20_type);
	PyModule_AddObject(module, "chacha20_ChaCha20", (PyObject *)&ChaCha20_type);

	chacha20_error = PyErr_NewException(const_cast<char*>("_chacha20.Error"), NULL, NULL);
	PyModule_AddObject(module, "chacha20_Error", chacha20_error);

	PyModule_AddStringConstant(module, "chacha20__doc__", const_cast<char*>(chacha20__doc__));
}
