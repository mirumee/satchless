'''
Order handling
'''
from . import listeners

listeners.start_listening()


class Partition(list):
    '''
    It's likely custom Partioner classes will need to distinguish the groups they
    emit. By not using a raw list it is possible to setattr on the Partitions.
    '''
    def __init__(self, items, shipping=False):
        super(Partition, self).__init__(items)
        self.is_shipping = shipping


class Partitioner(object):
    '''
    Base Partitioner class

    Class responsible for slicing orders into delivery groups.
    '''
    def partition(self, cart, items):
        raise NotImplementedError()

