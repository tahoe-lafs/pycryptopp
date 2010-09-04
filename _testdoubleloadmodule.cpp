
#include <Python.h>

PyDoc_STRVAR(_testdoubleload__doc__,
"_testdoubleload -- just for testing ticket #9 per ticket #44\n\
");

static PyMethodDef _testdoubleload_functions[] = {
    {NULL, NULL, 0, NULL}  /* sentinel */
};

#ifndef PyMODINIT_FUNC /* declarations for DLL import/export */
#define PyMODINIT_FUNC void
#endif
PyMODINIT_FUNC
init_testdoubleload(void) {
    PyObject *module;

    module = Py_InitModule3("_testdoubleload", _testdoubleload_functions, _testdoubleload__doc__);
    if (!module)
      return;
}

