'''
Order handling
'''
from . import listeners

listeners.start_listening()


class Partitioner(object):
    def partition(self, cart):
        raise NotImplementedError()
