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
from multiprocessing import Pool, TimeoutError, Process

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



def getNonce(start, params, event_for_stop=None):

	time1 = time.time()
	print "thread start"

	coinb1 = params['coinb1']
	coinb2 = params['coinb2']
	extranonce1 = params['extranonce1']
	merkle_branch = params['merkle_branch']
	version = params['version']
	previous_block = params['previous_block']
	time_ = params['time_']
	bits = params['bits']
	target = params['target']

	for i in range(start, start + 20000000):

		if((event_for_stop != None and event_for_stop.isSet())):
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
			if event_for_stop != None:
				event_for_stop.set()
			break

	time2 = time.time()
	print 'thread time: %s sec' % int(time2 - time1)


if __name__ == '__main__':

	time1 = time.time()
	pool = "eu.stratum.slushpool.com"
	stratumconn = StratumConnection(pool)
	stratumconn.miningSubscribe()

	params = {}
	params['extranonce1'] = stratumconn.getExtranonce1()
	extranonce2_size = stratumconn.getExtranonce2Size()
	job_id = stratumconn.getJobId()
	params['coinb1'] = stratumconn.getCoinb1()
	params['coinb2'] = stratumconn.getCoinb2()
	params['merkle_branch'] = stratumconn.getMerkleBranch()
	params['version'] = stratumconn.getVersion()
	params['bits'] = stratumconn.getBits()
	params['time_'] = stratumconn.getTime()
	params['previous_block'] = stratumconn.getPrevHash()

	difficulty = stratumconn.getDifficulty()
	target = stratumconn.getTarget(difficulty)
	params['target'] = "%.64x" % target
	print "target: %s" % params['target']

	print "coinb1: %s" % params['coinb1']
	print "extra1: %s" % params['extranonce1']
	print "coinb2: %s" % params['coinb2']

	procs = []
	proc_cnt = 4
	for i in range(0, proc_cnt):
		start = i * 20000000 + 4000000000
		procs.append(Process(target=getNonce, args=(start, params)))

	for i in range(0, proc_cnt):
		procs[i].start()

	for i in range(0, proc_cnt):
		procs[i].join()

	time2 = time.time()
	print 'all time: %s sec' % int(time2 - time1)
	print 'finish'
