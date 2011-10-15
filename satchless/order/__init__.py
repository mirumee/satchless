'''
Order handling
'''
from . import listeners

listeners.start_listening()


class Partitioner(object):
    '''
    Base Partitioner class

    Class responsible for slicing orders into delivery groups.
    '''
    def partition(self, cart, items):
        raise NotImplementedError()

