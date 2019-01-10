"""
Specification Interface 
------------------------

"""

from .base import *
from .exceptions import *

from . import exceptions, base 

__all__ = ['parse_generic', 'register', 'unregister'] + \
          base.__all__ + \
          exceptions.__all__

def parse_generic(dct):
    """
    Create Hallmark specification object 
   
    :param dict dct: Specification (a dictionary) or file location (a string)

    """
    dct,cls = SpecRegistry.find_handler_generic(dct)
    obj = cls() 
    obj.load(dct)
    return obj 

def register(cls):
    """
    Register specification handler

    :param class cls: Handler class
    """    
    SpecRegistry.register(cls)

def unregister(cls):
    """
    Unregister specification handler

    :param class cls: Handler class
    """
    SpecRegistry.unregister(cls)
