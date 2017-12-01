import hashlib
import struct
'''
def getTarget(bits):
    exp = bits >> 24
    mantisa = bits & 0x00ffffff
    return '%064x' % (mantisa * (1 << (8 * (exp - 3))))
'''
#version, time, bits, nonce are hex
#previous_block, merkle_root are string
def getBlockHash(version, previous_block, merkle_root, time, bits, nonce):
    block_header = struct.pack('<L', version)
    block_header += previous_block.decode('hex')[::-1]
    block_header += merkle_root.decode('hex')[::-1]
    block_header += struct.pack('<L', time)
    block_header += struct.pack('<L', bits)
    block_header += struct.pack('<L', nonce)
    block_header += '000000800000000000000000000000000000000000000000000000000000000000000000000000000000000080020000'.decode('hex')

    hash_ = hashlib.sha256(block_header).digest()
    hash_ = hashlib.sha256(hash_).digest()

    return hash_[::-1]

'''
version = 0x20000000
time = 0x5a0071dd #1509978589 sec
bits = 0x1800c1bd #402702781
previous_block = '00000000000000000026280c105cc6ac0117ba7706b631e50d2e15cd74c8ab91'
merkle_root = 'df8b2fd02ae4180cda631b6a7b787b25eb753e619e52e3cf1962d4195664a3d9'
nonce = 0x024105d7 #37815767

print getBlockHash(version, previous_block, merkle_root, time, bits, nonce)
'''