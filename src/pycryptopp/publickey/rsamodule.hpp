#ifndef __INCL_RSAMODULE_HPP
#define __INCL_RSAMODULE_HPP

void
init_rsa(PyObject* module);

extern PyMethodDef rsa_functions[];

extern PyObject *
rsa_generate(PyObject *dummy, PyObject *args, PyObject *kwdict);
extern const char*const rsa_generate__doc__;

extern PyObject *
rsa_create_verifying_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict);
extern const char*const rsa_create_verifying_key_from_string__doc__;

extern PyObject *
rsa_create_signing_key_from_string(PyObject *dummy, PyObject *args, PyObject *kwdict);
extern const char*const rsa_create_signing_key_from_string__doc__;

#endif /* #ifndef __INCL_RSAMODULE_HPP */
