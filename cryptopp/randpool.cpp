// randpool.cpp - written and placed in the public domain by Wei Dai
// RandomPool used to follow the design of randpool in PGP 2.6.x,
// but as of version 5.5 it has been redesigned to reduce the risk
// of reusing random numbers after state rollback (which may occur
// when running in a virtual machine like VMware).

#include "pch.h"

#ifndef CRYPTOPP_IMPORTS

#include "randpool.h"
#include "aes.h"
#include "sha.h"

NAMESPACE_BEGIN(CryptoPP)

RandomPool::RandomPool()
	: m_pCipher(new AES::Encryption), m_keySet(false)
{
	memset(m_key, 0, m_key.SizeInBytes());
	memset(m_seed, 0, m_seed.SizeInBytes());
}

void RandomPool::IncorporateEntropy(const byte *input, size_t length)
{
	SHA256 hash;
	hash.Update(m_key, 32);
	hash.Update(input, length);
	hash.Final(m_key);
	m_keySet = false;
}

void RandomPool::GenerateIntoBufferedTransformation(BufferedTransformation &target, const std::string &channel, lword size)
{
	if (size > 0)
	{
		if (!m_keySet)
			m_pCipher->SetKey(m_key, 32);

		do
		{
			m_pCipher->ProcessBlock(m_seed);
			size_t len = UnsignedMin(16, size);
			target.ChannelPut(channel, m_seed, len);
			size -= len;
		} while (size > 0);
	}
}

NAMESPACE_END

#endif
