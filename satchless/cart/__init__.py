class InvalidQuantityException(Exception):

    def __init__(self, reason, quantity_delta):
        self.reason = reason
        self.quantity_delta = quantity_delta

    def __str__(self):
        return self.reason

