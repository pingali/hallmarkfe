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

def parse_generic(arg):
    """
    Create Hallmark specification object 
   
    :param object arg: Specification (a dictionary) or file location (a string)

    """
    dct, cls = SpecRegistry.find_handler_generic(arg)
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

def schema_list():
    """
    Get a list of available schemas 
    """
    return SpecRegistry.schema_list()
    

def schema_list():
    """
    Get a list of available schemas 
    """
    return SpecRegistry.schema_list()
    
def schema_get(schema):
    """
    Get a list of available schemas 
    """
    return SpecRegistry.schema_get(schema) 
    
