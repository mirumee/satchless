from .....order import Partitioner, Partition


class SimplePartitioner(Partitioner):
    '''
    Simple order partitioner

    Gets whatever products are left in the cart and puts them all in a single
    delivery group.
    '''

    def partition(self, cart, items):
        handled_groups = [Partition(list(items))]
        remaining_items = ()
        return handled_groups, remaining_items



class SimplePhysicalPartitioner(Partitioner):
    '''
    Simple order partitioner

    Gets whatever products are left in the cart and puts them all in a single
    delivery group, which is marked as needing PhysicalShippingDetails.
    '''

    def partition(self, cart, items):
        partition = Partition(list(items))
        partition.use_shipping = True
        handled_groups = [partition]
        remaining_items = ()
        return handled_groups, remaining_items