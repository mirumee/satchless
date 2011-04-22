from decimal import Decimal
import locale

def decimal_format(value, min_decimal_places=0):
    decimal_tuple = value.as_tuple()
    have_decimal_places = -decimal_tuple.exponent
    digits = list(decimal_tuple.digits)
    while have_decimal_places < min_decimal_places:
        digits.append(0)
        have_decimal_places += 1
    while have_decimal_places > min_decimal_places and not digits[-1]:
        digits = digits[:-1]
        have_decimal_places -= 1
    return Decimal((decimal_tuple.sign, digits, -have_decimal_places))
