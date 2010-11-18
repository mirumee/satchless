from decimal import Decimal

class Price(object):
    gross = Decimal('NaN')
    net = Decimal('NaN')
    tax_name = None

    def __init__(self, net=None, gross=None, tax_name=''):
        if net is not None:
            self.net = Decimal(net)
        if gross is None:
            self.gross = self.net
        else:
            self.gross = Decimal(gross)
        self.tax_name = tax_name

    def __unicode__(self):
        if self.tax_name:
            return u"net=%s,gross=%s (%s)" % (self.net, self.gross, self.tax_name)
        else:
            return u"net=%s,gross=%s" % (self.net, self.gross)

    def __repr__(self):
        return "net=%s,gross=%s" % (self.net, self.gross)

    def __eq__(self, other):
        if isinstance(other, Price):
            return self.gross == other.gross and self.net == other.net
        return False

    def __mul__(self, other):
        return Price(net=self.net * other, gross=self.gross * other, tax_name=self.tax_name)

    def __add__(self, other):
        if self.tax_name == other.tax_name:
            return Price(net=self.net + other.net, gross=self.gross + other.gross, tax_name=self.tax_name)
        return Price(net=self.net + other.net, gross=self.gross + other.gross)

    def has_value(self):
        return not (self.net.is_nan() and self.gross.is_nan())


class StopPropagation(Exception):
    pass
