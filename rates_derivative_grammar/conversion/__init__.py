from inspect import isclass

from ._base import *
from ._types import *
from ._shared import *
from ._linear_rate import *

for name in dir():
    item = globals()[name]
    if isclass(item) and issubclass(item, TokenConverterRegistry.registry_type):
        TokenConverterRegistry.register(item)
