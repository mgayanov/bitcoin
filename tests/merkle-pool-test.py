#! /usr/bin/python
import merkletree


#see http://thedestitutedeveloper.blogspot.ru/2014/03/stratum-mining-block-headers-worked.html
txHashes = ['50a4a386ab344d40d29a833b6e40ea27dab6e5a79a2f8648d3bc0d1aa65ecd3f',
			'7952ecc836fb104f41b2cb06608eeeaa6d1ca2fe4391708fb13bb10ccf8da179',
			'9400ec6453aac577fb6807f11219b4243a3e50ca6d1c727e6d05663211960c94',
			'c11a630fa9332ab51d886a47509b5cbace844316f4fc52b493359b305fd489ae',
			'85891e7c5773f234d647f1d5fca7fbcabb59b261322d16c0ae486ccf5143383d',
			'faa26bbc17f99659f64136bea29b3fc8d772b339c52707d5f2ccfe1195317f43']

txcoinbase = '0ae66bdd8cf4ff954e4b0cbd91ba0a8d1038712e33a1a15baae46f413449371f'

merkle_tree = merkletree.MerkleTree(txHashes)

#should be 43c4345eb9ad9135836f5c31b697f62429c1be08d55906ff407852adfba680a5
print merkle_tree.getMerkleRootPool(txcoinbase)