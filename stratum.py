#! /usr/bin/python
import socket
import json
import re
import struct
import hashlib
import merkletree
import blockhash
import time
import threading

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
		print response
		self.subscription_details = re.findall('(\{[\s\S]+?\})', response)

	def getDifficulty(self):
		return int(json.loads(self.subscription_details[0])['result'][0][0][1], 16)

	def getTarget(self, difficulty):
		target = 0x00000000ffff0000000000000000000000000000000000000000000000000000
		return target / difficulty

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


def isSuccess(binhash, bintarget):
	return binhash < bintarget

def hash2(bin_):
	return hashlib.sha256(hashlib.sha256(bin_).digest()).digest()[::-1].encode('hex')

time1 = time.time()
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
time_ = stratumconn.getTime()
previous_block = stratumconn.getPrevHash()

difficulty = stratumconn.getDifficulty()
target = stratumconn.getTarget(difficulty)
target = "%.64x" % target
print "target: %s" % target

print "coinb1: %s" % coinb1
print "extra1: %s" % extranonce1
print "coinb2: %s" % coinb2

def getNonce(start, event_for_stop):
	time1 = time.time()
	print "thread start"
	for i in range(start, start + 2000000):

		if(event_for_stop.isSet()):
			break

		''' coin base '''
		extranonce2 = '%08x' % i
		coinbase = (coinb1 + extranonce1 + extranonce2 + coinb2).decode('hex')
		txcoinbase = hash2(coinbase)
		#print "txcoinbase: %s" % txcoinbase
	
		''' merkle root '''
		merkle_tree = merkletree.MerkleTree(merkle_branch)
		merkle_root = merkle_tree.getMerkleRootPool(txcoinbase)
		#print "merkleroot: %s" % merkle_root
	
		''' block hash '''
		nonce = 0x00000000
		blhash = blockhash.getBlockHash(version, previous_block, merkle_root, time_, bits, nonce)

		if(blhash < target.decode('hex')):
			print "blockhash: %s" % blhash.encode('hex')
			print "extra2: %s" % extranonce2
			event_for_stop.set()
			break

	time2 = time.time()
	print 'time: %s sec' % int(time2 - time1)


event_for_stop = threading.Event()

thread1 = threading.Thread(target=getNonce, args=(0, event_for_stop))
thread2 = threading.Thread(target=getNonce, args=(0, event_for_stop))
thread3 = threading.Thread(target=getNonce, args=(0, event_for_stop))
#thread4 = threading.Thread(target=getNonce, args=(0, event_for_stop))
#thread5 = threading.Thread(target=getNonce, args=(0, event_for_stop))

thread1.start()
thread2.start()
thread3.start()
#thread4.start()
#thread5.start()

thread1.join()
thread2.join()
thread3.join()
#thread4.join()
#thread5.join()

time2 = time.time()
print 'time: %s sec' % int(time2 - time1)
print 'finish'