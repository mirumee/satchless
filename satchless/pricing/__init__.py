from decimal import Decimal

class Price(object):
    gross = Decimal('NaN')
    net = Decimal('NaN')

    def __unicode__(self):
        return u"net=%s,gross=%s" % (self.net, self.gross)

    def __repr__(self):
        return "net=%s,gross=%s" % (self.net, self.gross)

    def __init__(self, net=None, gross=None):
        if net is not None:
            self.net = Decimal(net)
        if gross is None:
            self.gross = self.net
        else:
            self.gross = Decimal(gross)

    def __eq__(self, other):
        if isinstance(other, Price):
            return self.gross == other.gross and self.net == other.net
        return False

    def __mul__(self, other):
        return Price(net=self.net * other, gross=self.gross * other)

    def __add__(self, other):
        return Price(net=self.net + other.net, gross=self.gross + other.gross)
