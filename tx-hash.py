import hashlib
import struct

def getCoinBaseTxHash(version, tx_in_count, tx_in, tx_out_count, tx_out, lock_time):
    raw_tx = struct.pack('<L', version)
    raw_tx += struct.pack('b', tx_in_count) # 1 byte
    raw_tx += tx_in['prev_tx'].decode('hex')
    
    raw_tx += struct.pack('<L', tx_in['prev_output_index'])
    
    raw_tx += struct.pack('b', tx_in['bytes_in_coinbase']) # 1 byte
    
    raw_tx += struct.pack('b', tx_in['bytes_in_heigth']) # 1 byte
    
    raw_tx += tx_in['heigth'].decode('hex')[::-1]
    
    raw_tx += (tx_in['arbitrary_data'] + tx_in['sequence']).decode('hex')
    raw_tx += struct.pack('<b', tx_out_count) # 1 byte
    raw_tx += tx_out['satoshis'].decode('hex')
    raw_tx += tx_out['p2pkh'].decode('hex')
    raw_tx += lock_time.decode('hex')
    
    print raw_tx.encode('hex')
    
    hash_ = hashlib.sha256(raw_tx).digest()
    hash_ = hashlib.sha256(hash_).digest()

    return hash_[::-1].encode("hex")
    

version = 0x01
tx_in_count = 0x01

tx_in = {}
tx_in['prev_tx'] = "%064x" % 0x00
tx_in['prev_output_index'] = 0xffffffff
tx_in['bytes_in_heigth'] = 0x03
tx_in['heigth'] = '05014e' #328014 block
tx_in['arbitrary_data'] = '062f503253482f0472d35454085fffedf2400000f90f54696d652026204865616c74682021'
tx_in['sequence'] = '00000000'
tx_in['bytes_in_coinbase'] = len(tx_in['arbitrary_data'] + tx_in['sequence']) / 2

tx_out_count = 0x01

tx_out = {}
tx_out['satoshis'] = '2c37449500000000' #25.04275756 BTC
tx_out['p2pkh'] = '1976a914a09be8040cbf399926aeb1f470c37d1341f3b46588ac'

lock_time = '00000000'

print getCoinBaseTxHash(version, tx_in_count, tx_in, tx_out_count, tx_out, lock_time)