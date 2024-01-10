"""
Satchless

An e-commerce framework for Python
"""

from warnings import warn

from . import process
from . import item
from . import cart

__all__ = ['cart', 'item', 'process']

warn(
    "Satchless is no longer actively developed or supported.",
    DeprecationWarning,
    stacklevel=2,
)
