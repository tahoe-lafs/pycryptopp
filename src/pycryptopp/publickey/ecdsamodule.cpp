/**
* Things to do:
* Make it work and pass tests.
* compressed pub keys -- check out Wei Dai's example code on mailinglist as linked to from pycryptopp trac by Brian
* Make new KDF (standard, Crypto++-compatible).
*  in C++
*  in Python
* use Crypto++ Randomize()'s
* provide RNG class which is P1363-SHA-256

* Profit!
* Migrate pair-programming to Bespin.
* Put a Tahoe backend under Bespin.
*/

/**
 * ecdsamodule.cpp -- Python wrappers around Crypto++'s
 * ECDSA(1363)/EMSA1(SHA-256) -- <a
 * href="http://www.weidai.com/scan-mirror/sig.html#ECDSA">ECDSA</a>.
 *
 * The keys (192-bit) use the curve ASN1::secp192r1() and SHA-256 as the
 * hash function.  The Key Derivation Protocol is P1363_KDF2<SHA256>
 * http://www.users.zetnet.co.uk/hopwood/crypto/scan/prf.html#KDF2
 * to generate private (signing) keys from unguessable seeds -- see
 * source code for details and doc string for usage.
 */

#define PY_SSIZE_T_CLEAN
#include <Python.h>
#if (PY_VERSION_HEX < 0x02050000)
typedef int Py_ssize_t;
#endif

#include <math.h>

#include "ecdsamodule.hpp"

/* from Crypto++ */
#ifdef DISABLE_EMBEDDED_CRYPTOPP
#include <cryptopp/filters.h>
#include <cryptopp/osrng.h>
#include <cryptopp/eccrypto.h>
#include <cryptopp/oids.h>
#include <cryptopp/tiger.h>
#include <cryptopp/sha.h>
#include <cryptopp/pubkey.h>
// only needed for debugging -- the _dump() function
#include <iostream>
#include <cryptopp/ecp.h>
#include <cryptopp/hex.h>
#else
#include <embeddedcryptopp/filters.h>
#include <embeddedcryptopp/osrng.h>
#include <embeddedcryptopp/eccrypto.h>
#include <embeddedcryptopp/oids.h>
#include <embeddedcryptopp/tiger.h>
#include <embeddedcryptopp/sha.h>
#include <embeddedcryptopp/pubkey.h>
// only needed for debugging -- the _dump() function
#include <iostream>
#include <embeddedcryptopp/ecp.h>
#include <embeddedcryptopp/hex.h>
#endif

static const int KEY_SIZE_BITS=192;

USING_NAMESPACE(CryptoPP)

static const char*const ecdsa___doc__ = "ecdsa -- ECDSA(1363)/EMSA1(Tiger) signatures\n\
\n\
To create a new ECDSA signing key (deterministically from a 12-byte seed), construct an instance of the class, passing the seed as argument, i.e. SigningKey(seed).\n\
\n\
To get a verifying key from a signing key, call get_verifying_key() on the signing key instance.\n\
\n\
To deserialize an ECDSA verifying key from a string, call VerifyingKey(serialized_verifying_key).";

static PyObject *ecdsa_error;

typedef struct {
    PyObject_HEAD

    /* internal */
    ECDSA<ECP, Tiger>::Verifier *k;
} VerifyingKey;

PyDoc_STRVAR(VerifyingKey__doc__,
"an ECDSA verifying key");

static int
VerifyingKey___init__(PyObject* self, PyObject* args, PyObject* kwdict) {
    static const char *kwlist[] = { "serializedverifyingkey", NULL };
    const char *serializedverifyingkey;
    Py_ssize_t serializedverifyingkeysize = 0;

    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#:VerifyingKey__init__", const_cast<char**>(kwlist), &serializedverifyingkey, &serializedverifyingkeysize))
        return NULL;
    assert (serializedverifyingkeysize >= 0);

    if (serializedverifyingkeysize != 25) {
        PyErr_Format(ecdsa_error, "Precondition violation: size in bits is required to be %d (for %d-bit key), but it was %Zd", 25, KEY_SIZE_BITS, serializedverifyingkeysize);
        return -1;
    }

    VerifyingKey *mself = reinterpret_cast<VerifyingKey*>(self);

    StringSource ss(reinterpret_cast<const byte*>(serializedverifyingkey), serializedverifyingkeysize, true);

    ECP::Element element;
    DL_GroupParameters_EC<ECP> params(ASN1::secp192r1());
    params.SetPointCompression(true);
    try {
        element = params.DecodeElement(reinterpret_cast<const byte*>(serializedverifyingkey), true);
        mself->k = new ECDSA<ECP, Tiger>::Verifier(params, element);
        if (!mself->k) {
            PyErr_NoMemory();
            return -1;
        }
    } catch (InvalidDataFormat le) {
        PyErr_Format(ecdsa_error, "Serialized verifying key was corrupted.  Crypto++ gave this exception: %s", le.what());
        return -1;
    }

    return 0;
}

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

    if (self->k->VerifyMessage(reinterpret_cast<const byte*>(msg), msgsize, reinterpret_cast<const byte*>(signature), signaturesize))
        Py_RETURN_TRUE;
    else
        Py_RETURN_FALSE;
}

PyDoc_STRVAR(VerifyingKey_verify__doc__,
"Return whether the signature is a valid signature on the msg.");

static PyObject *
VerifyingKey_serialize(VerifyingKey *self, PyObject *dummy) {
    ECDSA<ECP, Tiger>::Verifier *pubkey;
    pubkey = new ECDSA<ECP, Tiger>::Verifier(*(self->k));
    const DL_GroupParameters_EC<ECP>& params = pubkey->GetKey().GetGroupParameters();

    Py_ssize_t len = params.GetEncodedElementSize(true);
    PyObject* result = PyString_FromStringAndSize(NULL, len);
    if (!result)
        return NULL;

    params.EncodeElement(true, pubkey->GetKey().GetPublicElement(),
                         reinterpret_cast<byte*>(PyString_AS_STRING(result)));

    return result;
}

PyDoc_STRVAR(VerifyingKey_serialize__doc__,
"Return a string containing the key material.  The string can be passed to \n\
the constructor of VerifyingKey to instantiate a new copy of this key.");

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
    (destructor)VerifyingKey_dealloc,                         /*tp_dealloc*/
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
    0,                               /* tp_traverse */
    0,                               /* tp_clear */
    0,                               /* tp_richcompare */
    0,                               /* tp_weaklistoffset */
    0,                               /* tp_iter */
    0,                               /* tp_iternext */
    VerifyingKey_methods,             /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    VerifyingKey___init__,       /* tp_init */
};

typedef struct {
    PyObject_HEAD

    /* internal */
    ECDSA<ECP, Tiger>::Signer *k;
} SigningKey;

static void
SigningKey_dealloc(SigningKey* self) {
    if (self->k)
        delete self->k;
    self->ob_type->tp_free((PyObject*)self);
}

static const char* TAG_AND_SALT = "102:pycryptopp v0.5.3 key derivation algorithm using Tiger hash to generate ECDSA 192-bit secret exponents," \
    "16:H1yGNvUONoc0FD1d,";
static const size_t TAG_AND_SALT_len = 127;

/** copied from Crypto++'s integer.cpp */
/** The following is in Crypto++'s integer.cpp and we use them:
* void Integer::Randomize(RandomNumberGenerator &rng, size_t nbits)
* {
* 	const size_t nbytes = nbits/8 + 1;
* 	SecByteBlock buf(nbytes);
* 	rng.GenerateBlock(buf, nbytes);
* 	if (nbytes)
* 		buf[0] = (byte)Crop(buf[0], nbits % 8);
* 	Decode(buf, nbytes, UNSIGNED);
* }
* void Integer::Randomize(RandomNumberGenerator &rng, const Integer &min, const Integer &max)
* {
* 	if (min > max)
* 		throw InvalidArgument("Integer: Min must be no greater than Max");
*
* 	Integer range = max - min;
* 	const unsigned int nbits = range.BitCount();
*
* 	do
* 	{
* 		Randomize(rng, nbits);
* 	}
* 	while (*this > range);
*
* 	*this += min;
* }
*
*/

static int
SigningKey___init__(PyObject* self, PyObject* args, PyObject* kwdict) {
    static const char *kwlist[] = { "seed", NULL };
    const char* seed;
    Py_ssize_t seedlen;
    if (!PyArg_ParseTupleAndKeywords(args, kwdict, "t#:SigningKey___init__", const_cast<char**>(kwlist), &seed, &seedlen)) {
        return -1;
    }

    if (seedlen != 12) {
        PyErr_Format(ecdsa_error, "Precondition violation: seed is required to be of length 12, but it was %zd", seedlen);
        return -1;
    }

    OID curve;
    Integer grouporderm1;
    byte privexpbytes[24] = {0};
    Integer privexponentm1;
    privexponentm1.Decode(privexpbytes, sizeof(privexpbytes)); assert (privexponentm1 == 0); // just checking..

    DL_GroupParameters_EC<ECP> params(ASN1::secp192r1());
    params.SetPointCompression(true);
    grouporderm1 = params.GetGroupOrder() - 1;
    Tiger t;

    t.Update(reinterpret_cast<const byte*>(TAG_AND_SALT), TAG_AND_SALT_len);
    t.Update(reinterpret_cast<const byte*>(seed), seedlen);
    t.TruncatedFinal(privexpbytes, Tiger::DIGESTSIZE);
    privexponentm1.Decode(privexpbytes, sizeof(privexpbytes));

    while (privexponentm1 >= grouporderm1) {
        Tiger t2;
        t2.Update(reinterpret_cast<const byte*>(TAG_AND_SALT), TAG_AND_SALT_len);
        std::cerr << "WHEE " << sizeof(privexpbytes) << "\n";std::cerr.flush();
        t2.Update(privexpbytes, sizeof(privexpbytes));
        t2.TruncatedFinal(privexpbytes, Tiger::DIGESTSIZE);
        privexponentm1.Decode(privexpbytes, sizeof(privexpbytes));
    }

    SigningKey* mself = reinterpret_cast<SigningKey*>(self);

    mself->k = new ECDSA<ECP, Tiger>::Signer(params, privexponentm1+1);

    if (!mself->k) {
        PyErr_NoMemory();
        return -1;
    }

    return 0;
}

PyDoc_STRVAR(SigningKey__init____doc__,
"Create a signing key (192 bits) deterministically from the given seed.\n\
\n\
This implies that if someone can guess the seed then they can learn the signing key.  A good way to get an unguessable seed is os.urandom(12).\n\
\n\
@param seed seed\n\
\n\
@precondition len(seed) >= ceil(sizeinbits/16.0)");

static PyObject *
SigningKey__dump(SigningKey *self, PyObject *dummy) {
    const DL_GroupParameters_EC<ECP>& gp = self->k->GetKey().GetGroupParameters();
    std::cout << "whee " << gp.GetEncodedElementSize(true) << "\a";
    std::cout << "booo " << gp.GetEncodedElementSize(false) << "\n";

    ECPPoint p = gp.GetSubgroupGenerator();
    std::cout << "generator " << p.x << ", " << p.y << "\n";

    std::cout << "GroupOrder: ";
    std::cout << gp.GetGroupOrder();
    std::cout << "\n";

    std::string s;
    StringSink* ss = new StringSink(s);
    HexEncoder he(ss);
    std::cout << "AlgorithmID: ";
    gp.GetAlgorithmID().DEREncode(he);
    std::cout << s << "\n";

    const ECP& ec = gp.GetCurve();
    Integer fieldsize = ec.FieldSize();
    std::cout << "field size " << fieldsize.BitCount() << " " << fieldsize.ByteCount() << " " << ec.FieldSize() << "\n";
    std::cout << "Curve: ";
    std::cout << "curve field max element bit length: " << ec.GetField().MaxElementBitLength() << "\n";
    std::cout << "curve field modulus: " << ec.GetField().GetModulus() << "\n";
    std::cout << "curve A: " << ec.GetA() << ", curve B: " << ec.GetB();

    const ECP::Field& f = ec.GetField();
    std::cout << "curve field modulus: " << f.GetModulus() << "\n";
    std::cout << "curve field identity: " << f.Identity() << "\n";

    std::string cfs;
    StringSink* cfss = new StringSink(cfs);
    HexEncoder cfhe(cfss);
    f.DEREncode(cfhe);
    std::cout << "curve field derencoding: " << cfs << "\n";

    const CryptoMaterial& cm = self->k->GetMaterial();
    Integer i;
    cm.GetValue("SubgroupOrder", i);
    std::cout << "\n";
    std::cout << "SubgroupOrder: ";
    std::cout << i;
    std::cout << "\n";
    ECP::Element e;
    cm.GetValue("SubgroupGenerator", e);
    std::cout << "SubgroupGenerator: ";
    std::cout << e.x << ", " << e.y;
    std::cout << "\n";

    std::cout << "private key: ";

    const PrivateKey& privkey = self->k->GetPrivateKey();

    std::cout << privkey.GetValueNames() << "\n";

    Integer privi;
    privkey.GetValue("PrivateExponent", privi);
    std::cout << privi << "\n";
    std::cout << "numbits: " << privi.BitCount() << "\n";
    std::cout << "numbytes: " << privi.ByteCount() << "\n";

    Py_RETURN_NONE;
}

PyDoc_STRVAR(SigningKey__dump__doc__,
"Print to stdout some descriptions of the math pieces.");

static PyObject *
SigningKey_sign(SigningKey *self, PyObject *msgobj) {
    const char *msg;
    Py_ssize_t msgsize;
    PyString_AsStringAndSize(msgobj, const_cast<char**>(&msg), reinterpret_cast<Py_ssize_t*>(&msgsize));
    assert (msgsize >= 0);

    Py_ssize_t sigsize;
    sigsize = self->k->SignatureLength();

    PyStringObject* result = reinterpret_cast<PyStringObject*>(PyString_FromStringAndSize(NULL, sigsize));
    if (!result)
        return NULL;
    assert (sigsize >= 0);

    AutoSeededRandomPool randpool(false); //XXX

    Py_ssize_t siglengthwritten;
    try {
        siglengthwritten = self->k->SignMessage(
            randpool,
            reinterpret_cast<const byte*>(msg),
            msgsize,
            reinterpret_cast<byte*>(PyString_AS_STRING(result)));
    } catch (InvalidDataFormat le) {
        Py_DECREF(result);
        return PyErr_Format(ecdsa_error, "Signing key was corrupted.  Crypto++ gave this exception: %s", le.what());
    }

    if (siglengthwritten < sigsize)
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, "SigningKey_sign", "INTERNAL ERROR: signature was shorter than expected.");
    else if (siglengthwritten > sigsize) {
        fprintf(stderr, "%s: %d: %s: %s", __FILE__, __LINE__, "SigningKey_sign", "INTERNAL ERROR: signature was longer than expected, so memory was invalidly overwritten.");
        abort();
    }
    assert (siglengthwritten >= 0);

    return reinterpret_cast<PyObject*>(result);
}

PyDoc_STRVAR(SigningKey_sign__doc__,
     "Return a signature on the argument."); //XXX  If randseed is not None then it is required to be an  "); // XXX randseed!

static PyObject *
SigningKey_get_verifying_key(SigningKey *self, PyObject *dummy) {
    VerifyingKey *verifier = PyObject_New(VerifyingKey, &VerifyingKey_type);
    if (!verifier)
        return NULL;

    verifier->k = new ECDSA<ECP, Tiger>::Verifier(*(self->k));
    if (!verifier->k)
        return PyErr_NoMemory();
    verifier->k->AccessKey().AccessGroupParameters().SetPointCompression(true);

    return reinterpret_cast<PyObject*>(verifier);
}

PyDoc_STRVAR(SigningKey_get_verifying_key__doc__,
"Return the corresponding verifying key.");

static PyMethodDef SigningKey_methods[] = {
    {"sign", reinterpret_cast<PyCFunction>(SigningKey_sign), METH_O, SigningKey_sign__doc__},
    {"_dump", reinterpret_cast<PyCFunction>(SigningKey__dump), METH_NOARGS, SigningKey__dump__doc__},
    {"get_verifying_key", reinterpret_cast<PyCFunction>(SigningKey_get_verifying_key), METH_NOARGS, SigningKey_get_verifying_key__doc__},
    {NULL},
};

static PyTypeObject SigningKey_type = {
    PyObject_HEAD_INIT(NULL)
    0,                         /*ob_size*/
    "ecdsa.SigningKey", /*tp_name*/
    sizeof(SigningKey),             /*tp_basicsize*/
    0,                         /*tp_itemsize*/
    (destructor)SigningKey_dealloc,                         /*tp_dealloc*/
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
    Py_TPFLAGS_DEFAULT,        /*tp_flags*/
    SigningKey__init____doc__,         /* tp_doc */
    0,                               /* tp_traverse */
    0,                               /* tp_clear */
    0,                               /* tp_richcompare */
    0,                               /* tp_weaklistoffset */
    0,                               /* tp_iter */
    0,                               /* tp_iternext */
    SigningKey_methods,             /* tp_methods */
    0,                         /* tp_members */
    0,                         /* tp_getset */
    0,                         /* tp_base */
    0,                         /* tp_dict */
    0,                         /* tp_descr_get */
    0,                         /* tp_descr_set */
    0,                         /* tp_dictoffset */
    SigningKey___init__,       /* tp_init */
};

void
init_ecdsa(PyObject*const module) {
    VerifyingKey_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&VerifyingKey_type) < 0)
        return;
    Py_INCREF(&VerifyingKey_type);
    PyModule_AddObject(module, "ecdsa_VerifyingKey", (PyObject *)&VerifyingKey_type);

    SigningKey_type.tp_new = PyType_GenericNew;
    if (PyType_Ready(&SigningKey_type) < 0)
        return;
    Py_INCREF(&SigningKey_type);
    PyModule_AddObject(module, "ecdsa_SigningKey", (PyObject *)&SigningKey_type);

    ecdsa_error = PyErr_NewException(const_cast<char*>("_ecdsa.Error"), NULL, NULL);
    PyModule_AddObject(module, "ecdsa_Error", ecdsa_error);

    PyModule_AddStringConstant(module, "ecdsa___doc__", const_cast<char*>(ecdsa___doc__));
}
