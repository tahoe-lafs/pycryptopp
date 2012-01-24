
#include <Python.h>

PyDoc_STRVAR(_testdoubleload__doc__,
             "_testdoubleload -- just for testing ticket #9 per ticket #44\n\
");

static PyMethodDef _testdoubleload_functions[] = {
    {NULL, NULL, 0, NULL}  /* sentinel */
};

/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/cryptlib.h>
#else
#include <embeddedcryptopp/cryptlib.h>
#endif

#ifndef PyMODINIT_FUNC /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_testdoubleload(void) {
    const CryptoPP::NameValuePairs &my_nullNameValuePairs = CryptoPP::g_nullNameValuePairs;
    PyObject *module;


    printf("HELLO WORLD i'm testdoubleload\n");
    printf("%d\n", my_nullNameValuePairs.GetVoidValue("anything", typeid(0), NULL));
    printf("GOODBYE i'm testdoubleload\n");

    module = Py_InitModule3("_testdoubleload", _testdoubleload_functions, _testdoubleload__doc__);
    if (!module)
        return;
}
