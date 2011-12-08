from .....order import Partitioner, Partition


class SimplePartitioner(Partitioner):
    '''
    Simple order partitioner

    Gets whatever products are left in the cart and puts them all in a single
    delivery group.
    '''
    shipping = False

    def partition(self, cart, items):
        handled_groups = [Partition(list(items), shipping=self.shipping)]
        remaining_items = ()
        return handled_groups, remaining_items


class SimplePhysicalPartitioner(SimplePartitioner):
    '''
    Simple order partitioner

    Gets whatever products are left in the cart and puts them all in a single
    delivery group, which is marked as needing a shipping address.
    '''
    shipping = True