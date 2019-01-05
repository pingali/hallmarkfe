"""
Exceptions 
----------

"""

__all__ = ['SpecNoHandler', 'SpecInvalidSchema',
           'SpecMissingSchema', 'SpecInvalidSpecification']

class SpecNoHandler(Exception):
    """
    Not class to handle metadata with a given schema
    """
    pass

class SpecInvalidSchema(Exception):
    """
    Invalid schema definition 
    """
    pass

class SpecMissingSchema(Exception):
    """
    Schema not defined in the given merit subclass 
    """
    pass

class SpecInvalidSpecification(Exception):
    """
    Specification cannot be loaded due to missing or invalid fields.
    """
    pass

