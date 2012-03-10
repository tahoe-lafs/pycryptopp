
#include <Python.h>

PyDoc_STRVAR(_doubleloadtester__doc__,
             "_doubleloadtester -- just for testing ticket #9 per ticket #44\n\
");

static PyMethodDef _doubleloadtester_functions[] = {
    {NULL, NULL, 0, NULL}  /* sentinel */
};

/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/cryptlib.h>
#else
#include <src-cryptopp/cryptlib.h>
#endif

#ifndef PyMODINIT_FUNC /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_doubleloadtester(void) {
    const CryptoPP::NameValuePairs &my_nullNameValuePairs = CryptoPP::g_nullNameValuePairs;
    PyObject *module;


    printf("HELLO WORLD i'm doubleloadtester\n");
    printf("%d\n", my_nullNameValuePairs.GetVoidValue("anything", typeid(0), NULL));
    printf("GOODBYE i'm doubleloadtester\n");

    module = Py_InitModule3("_doubleloadtester", _doubleloadtester_functions, _doubleloadtester__doc__);
    if (!module)
        return;
}
