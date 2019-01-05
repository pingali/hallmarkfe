"""
Specification Interface 
------------------------

"""

from .base import *
from .exceptions import *

from . import exceptions, base 

__all__ = ['parse', 'register', 'unregister'] + \
          base.__all__ + \
          exceptions.__all__ 
           


def parse(dct):
    """
    Create Hallmark specification object 
   
    :param dict dct: Specification (a dictionary) 
    """
    cls = SpecRegistry.find_handler_for_dict(dct)
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

