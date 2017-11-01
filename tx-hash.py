import hashlib
import struct

def getTarget(bits):
    exp = bits >> 24
    mantisa = bits & 0x00ffffff
    return "%064x" % (mantisa * (1 << (8 * (exp - 3))))

def getBlockHash(version, previous_block, merkle_root, time, bits, nonce):
    block_header = struct.pack("<L", version)
    block_header += previous_block.decode("hex")[::-1]
    block_header += merkle_root.decode("hex")[::-1]
    block_header += struct.pack("<L", time)
    block_header += struct.pack("<L", bits)
    block_header += struct.pack("<L", nonce)

    hash_ = hashlib.sha256(block_header).digest()
    hash_ = hashlib.sha256(hash_).digest()

    return hash_[::-1].encode("hex")

version = 2
time = 0x53058b35
bits = 0x19015f53
previous_block = "000000000000000117c80378b8da0e33559b5997f2ad55e2f7d18ec1975b9717"
merkle_root = "871714dcbae6c8193a2bb9b2a69fe1c0440399f38d94b3a0f1b447275a29978a"
nonce = 856192328

target = getTarget(bits)

block_hash = getBlockHash(version, previous_block, merkle_root, time, bits, nonce)

difficulty = (0xffff << 52*4) / float(0x404cb << 48*4)