class PriceException(Exception):
    pass

class PriceDoesNotExist(PriceException):
    pass

class MultiplePricesReturned(PriceException):
    pass
