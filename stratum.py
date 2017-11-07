#! /usr/bin/python
import socket
import json
import re
import struct
import hashlib
from merkleroot import getMerkleRoot
from blockhash import getBlockHash

class StratumConnection:
	
	def __init__(self, pool, port=3333):
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((pool, port))
		
	def send(self, cmd):
		self.socket.send(cmd)
		return self.socket.recv(4000)
	
	def miningSubscribe(self):
		cmd = """{"id": 1, "method": "mining.subscribe", "params": []}\n"""
		response = self.send(cmd)
		self.subscription_details = re.findall('(\{[\s\S]+?\})', response)
	
	def getExtranonce1(self):
		return json.loads(self.subscription_details[0])['result'][1]
	
	def getExtranonce2Size(self):
		return json.loads(self.subscription_details[0])['result'][2]
	
	def getJobId(self):
		return json.loads(self.subscription_details[2])['params'][0]
	
	def getPrevHash(self):
		reversed_ = json.loads(self.subscription_details[2])['params'][1]
		prev_hash = ''
		for i in range(0, 8):
			pos = i*8
			prev_hash += reversed_[pos:pos + 8][::-1]
		
		return prev_hash[::-1]
	
	def getCoinb1(self):
		return json.loads(self.subscription_details[2])['params'][2]
	
	def getCoinb2(self):
		return json.loads(self.subscription_details[2])['params'][3]
	
	def getMerkleBranch(self):
		return json.loads(self.subscription_details[2])['params'][4]
	
	def getVersion(self):
		return int(json.loads(self.subscription_details[2])['params'][5], 16)
	
	def getBits(self):
		return int(json.loads(self.subscription_details[2])['params'][6], 16)
	
	def getTime(self):
		return int(json.loads(self.subscription_details[2])['params'][7], 16)
		
def getTarget(bits):
    exp = bits >> 24
    mantisa = bits & 0x00ffffff
    return ('%064x' % (mantisa * (1 << (8 * (exp - 3))))).decode('hex')

def isSuccess(binhash, bintarget):
	return binhash < bintarget

def hash2(bin_):
	return hashlib.sha256(hashlib.sha256(coinbase).digest()).digest()[::-1].encode('hex')


pool = "eu.stratum.slushpool.com"
stratumconn = StratumConnection(pool)
stratumconn.miningSubscribe()

extranonce1 = stratumconn.getExtranonce1()
extranonce2_size = stratumconn.getExtranonce2Size()
job_id = stratumconn.getJobId()
coinb1 = stratumconn.getCoinb1()
coinb2 = stratumconn.getCoinb2()
merkle_branch = stratumconn.getMerkleBranch()
version = stratumconn.getVersion()
bits = stratumconn.getBits()
time = stratumconn.getTime()
previous_block = stratumconn.getPrevHash()

target = getTarget(bits)

#print coinb1
#print extranonce1
#print coinb2
#print extranonce2_size

for i in range(0, 1000):
	''' get coinbase '''
	extranonce2 = '%08x' % i
	coinbase = (coinb1 + extranonce1 + extranonce2 + coinb2).decode('hex')
	coinbase_txid = hash2(coinbase)
	#print coinbase_txid
	
	''' get merkle root '''
	merkle_branch = [coinbase_txid] + merkle_branch
	merkle_root = getMerkleRoot(merkle_branch)
	
	''' get block hash '''
	nonce = 0x00000000
	blockhash = getBlockHash(version, previous_block, merkle_root, time, bits, nonce)
	
	if(isSuccess(blockhash, target)):
		print blockhash.encode('hex')
		print extranonce2
	

print extranonce2






