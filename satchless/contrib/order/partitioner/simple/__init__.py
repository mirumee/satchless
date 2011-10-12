from satchless.order import Partitioner

class SimplePartitioner(Partitioner):
	'''
	Simple order partitioner

	Gets whatever products are left in the cart and puts them all in a single
	delivery group.
	'''

	def partition(self, cart, items):
	    handled_groups = [list(items)]
	    remaining_items = ()
	    return handled_groups, remaining_items