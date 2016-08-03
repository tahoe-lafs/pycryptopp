// chacha.h - written and placed in the public domain by Jeffrey Walton.
//            Copyright assigned to the Crypto++ project.
//            Based on Wei Dai's Salsa20 and Bernstein's reference ChaCha
//            family implementation at http://cr.yp.to/chacha.html.

//! \file chacha.h
//! \brief Classes for ChaCha8, ChaCha12 and ChaCha20 stream ciphers

#ifndef CRYPTOPP_CHACHA_H
#define CRYPTOPP_CHACHA_H

#include "strciphr.h"
#include "secblock.h"

NAMESPACE_BEGIN(CryptoPP)

//! \class ChaCha_Info
//! \brief ChaCha stream cipher information
template <unsigned int R>
struct ChaCha_Info : public VariableKeyLength<32, 16, 32, 16, SimpleKeyingInterface::UNIQUE_IV, 8>, public FixedRounds<R>
{
	static const char *StaticAlgorithmName() {static const std::string name = "ChaCha" + IntToString(R); return name.c_str();}
};

//! \class ChaCha_Policy
//! \brief ChaCha stream cipher implementation
template <unsigned int R>
class CRYPTOPP_NO_VTABLE ChaCha_Policy : public AdditiveCipherConcretePolicy<word32, 16>
{
protected:
	CRYPTOPP_CONSTANT(ROUNDS=FixedRounds<R>::ROUNDS)

	void CipherSetKey(const NameValuePairs &params, const byte *key, size_t length);
	void OperateKeystream(KeystreamOperation operation, byte *output, const byte *input, size_t iterationCount);
	void CipherResynchronize(byte *keystreamBuffer, const byte *IV, size_t length);
	bool CipherIsRandomAccess() const {return false;} // TODO
	void SeekToIteration(lword iterationCount);
	unsigned int GetAlignment() const;
	unsigned int GetOptimalBlockSize() const;

	FixedSizeAlignedSecBlock<word32, 16> m_state;
};

//! \class ChaCha8
//! \brief ChaCha8 stream cipher
//! \sa <a href="http://cr.yp.to/chacha/chacha-20080128.pdf">ChaCha, a variant of Salsa20</a> (2008.01.28).
struct ChaCha8 : public ChaCha_Info<8>, public SymmetricCipherDocumentation
{
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<8>, AdditiveCipherTemplate<> >, ChaCha_Info<8> > Encryption;
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<8>, AdditiveCipherTemplate<> >, ChaCha_Info<8> > Decryption;
};

//! \class ChaCha12
//! \brief ChaCha12 stream cipher
//! \sa <a href="http://cr.yp.to/chacha/chacha-20080128.pdf">ChaCha, a variant of Salsa20</a> (2008.01.28).
struct ChaCha12 : public ChaCha_Info<12>, public SymmetricCipherDocumentation
{
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<12>, AdditiveCipherTemplate<> >, ChaCha_Info<12> > Encryption;
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<12>, AdditiveCipherTemplate<> >, ChaCha_Info<12> > Decryption;
};

//! \class ChaCha20
//! \brief ChaCha20 stream cipher
//! \sa <a href="http://cr.yp.to/chacha/chacha-20080128.pdf">ChaCha, a variant of Salsa20</a> (2008.01.28).
struct ChaCha20 : public ChaCha_Info<20>, public SymmetricCipherDocumentation
{
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<20>, AdditiveCipherTemplate<> >, ChaCha_Info<20> > Encryption;
	typedef SymmetricCipherFinal<ConcretePolicyHolder<ChaCha_Policy<20>, AdditiveCipherTemplate<> >, ChaCha_Info<20> > Decryption;
};

NAMESPACE_END

#endif  // CRYPTOPP_CHACHA_H
