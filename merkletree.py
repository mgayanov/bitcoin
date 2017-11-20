#! /usr/bin/python
import hashlib

class MerkleTree:

	# txHashes are a list of hashes in a string ['txhash0', ... 'txhash1']
	txHashes = None

	def __init__(self, txHashes):

		self.txHashes = txHashes

	def isLenEven(self):
		return len(self.txHashes) % 2 == 0

	def duplicateLastElement(self):
		length = len(self.txHashes)
		last_element = self.txHashes[length - 1 : length].pop()
		self.txHashes.append(last_element)
	
	def prepareList(self):
		if(not self.isLenEven()):
			self.duplicateLastElement()

	#For node
	def getMerkleRoot(self):
	
		if(len(self.txHashes) == 1):
			return self.txHashes.pop()
	
		self.prepareList()
	
		length = len(self.txHashes)
		for i in range(1, length / 2 + 1, 1):
		
			''' bits are need to be reversed before they are hashed '''
			item = self.txHashes[i].decode('hex')[::-1]
			self.txHashes.remove(self.txHashes[i])

			self.txHashes[i - 1] = self.txHashes[i - 1].decode('hex')[::-1] + item

			self.txHashes[i - 1] = hashlib.sha256(self.txHashes[i - 1]).digest()
			self.txHashes[i - 1] = hashlib.sha256(self.txHashes[i - 1]).digest()
			self.txHashes[i - 1] = self.txHashes[i - 1][::-1].encode('hex')
	
		return self.getMerkleRoot()

	#For pool
	def getMerkleRootPool(self, txcoinbase):
		root = txcoinbase.decode('hex')

		for txHash in self.txHashes:
			root += txHash.decode('hex')
			root = hashlib.sha256(hashlib.sha256(root).digest()).digest()

		return root.encode('hex')