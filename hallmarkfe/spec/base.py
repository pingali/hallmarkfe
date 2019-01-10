"""
Base 
----

Base classes for the specification handlers
"""
import os
import sys
import json
import yaml
import collections 
import abc
import glob
import texttable 
from .exceptions import *
from .utils import *

__all__ = ['SpecRegistry', 'SpecMeta', 'SpecBase', 'SpecManagerBase']

class SpecRegistry(object):
    """
    Registry of all the loaded specification handlers
    """
    _registry = [] 

    @classmethod
    def register(registrycls, cls):
        """
        Add handler to the registry 
        """
        registrycls._registry.append(cls)

    @classmethod
    def unregister(registrycls, cls):
        """
        Add handler to the registry 
        """
        registrycls._registry = [c for c in SpecRegistry._registry if c.__name__ != cls.__name__] 
        
    @classmethod    
    def schema_list(cls):
        """
        List known schemas and handling classes
        """
        summary = [('Schema', 'Class', 'Module')]
        for c in cls._registry:
            mod = sys.modules[c.__module__]
            summary.append((c.schema, c.__name__, mod.__file__))

        return summary

    @classmethod    
    def schema_get(cls, schema):
        """
        List known schemas and handling classes
        """
        for c in cls._registry:
            if c.schema == schema:
                return c 
        raise Exception("Unknown schema: {}".format(schema))

    #############################################
    # Helper methods 
    #############################################
    @classmethod 
    def find_handler_for_schema(cls, schema_handler):
        """
        Find loader for a given schema. 

        A class can load one or more schema types.
        """
        if isinstance(schema_handler,dict):
            schema = schema_handler['schema']

        if isinstance(schema_handler,list):
            schema = []
            for i in schema_handler:
                schema.append(i["schema"])

        for h in cls._registry: 
            if ((isinstance(schema, str)) and
                (h.schema == schema)):
                return h 

            elif isinstance(schema, list):
                if set(h.schema_list) == set(schema):
                    return h

        raise SpecNoHandler()


    @classmethod 
    def find_handler_generic(cls, dct):
        """
        Find the handler class and load file 

        A class can load one or more schema types.
        """
        if os.path.isfile(str(dct)):
            with open(dct) as f:
                fh = (f.read()) 
            if dct.lower().endswith('.json'):
                handler_ = json.loads(fh)            
            elif dct.lower().endswith(('.yaml','.yml')):
                handler_ = yaml.load(fh)
            else:
                raise SpecInvalidSpecification("Not an accepted file format")
        else:
            handler_ = dct
            if isinstance(handler_,dict) and 'schema' not in handler_:
                raise SpecMissingSchema() 

        if isinstance(handler_,list):
            if any(not isinstance(item,dict) for item in handler_):
                raise SpecInvalidSpecification("Not a valid specification list.")

        elif not isinstance(handler_, dict):
            raise SpecInvalidSpecification("Not a dictionary")


        return (handler_,cls.find_handler_for_schema(handler_))
    
    
class SpecMeta(abc.ABCMeta):
    """
    Meta class for all elements with schemas. This allows for
    registration, validation, and tracking of the schema implementors.
    """
    def __init__(cls, name, bases, dct):

        # Check whether the class is defined correctly
        cls.validate_handler(dct)        

        # Register
        SpecRegistry.register(cls)

        # Now initialize 
        super().__init__(name, bases, dct)

    def validate_handler(self, dct):
        """
        Validate the class implementing schema
        """
        self.validate_handler_schema(dct) 

    def validate_handler_schema(self, dct):
        """
        Validate schema specification 
        """
        schema = dct.get('schema', None)        
        if isinstance(schema, str) and len(schema) > 0: 
            self._schema = schema 
        elif isinstance(schema, list) and len(schema) > 0:
            for v in schema:
                if not (isinstance(v, str) and len(v) > 0):
                    raise SpecInvalidSchema()
            self._schema = schema
        else:
            raise SpecInvalidSchema("Schema type or value error")

        
class SpecBase(metaclass=SpecMeta): 
    """
    Base abstract class for spec implementors 
    """        

    schema = "global:default:v1"
    schema_list = ["global:default:v1"]
    """
    Every Spec metadata class should specify a schema (a 
    string or a list of strings) 
    """
    def __init__(self, *args, **kwargs):
        self.spec = {}
        """
        Internal dict representation of the specification

        required elements: name, description
        """
        self.required = [
            'name',
            'description',
            'owner'
        ]

        # Now initialize
        self.initialize()

    name = generate_attribute('name')
    """
    Property-like access to specification's name element
    """
    
    description = generate_attribute('description')
    """
    Property-like access to specification's description element 
    """

    owner = generate_attribute('owner')
    """
    Property-like access to specification's owner element 
    """    

    def validate(self, spec=None):
        """
        Check if the metadata is valid 

        :param dict metadata: Optional metadata dict to be validated. 
              If not specified, will use the class's metadata attribute. 
        """

        if spec is None:
            spec = self.spec

        def check_required(spec):
            for r in self.required:
                if r not in spec:
                    raise SpecInvalidSpecification("Missing: {}".format(r))
                if hasattr(self, 'validate_' + r):
                    func = getattr(self, 'validate_' + r)
                    func(metadata[r])
  
        if isinstance(spec,dict):
                check_required(spec)


        elif isinstance(spec,list):
            for i in spec:
                check_required(i)



    # @abc.abstractmethod             
    def initialize(self, *args, **kwargs):
        """
        Initialize the state of the metadata object 
        """
        pass 

    def dump(self):
        """
        Return the metadata as a dictionary 
        """
        self.validate()

        d = [('schema', self.schema)]

        # Take a union of order and required 
        order = self.order
        for k in self.required:
            if k not in order:
                order.append(k)

        # => Now follow the order computed
        for k in order:

            if hasattr(self, 'dump_' + k):
                func = getattr(self, 'dump_' + k)
            else:
                func = lambda x: x 
            d.append((k, func(self.metadata[k])))
            
        for k,v in self.metadata.items():
            if k in self.order:
                continue
            if hasattr(self, 'dump_' + k):
                func = getattr(self, 'dump_' + k)
            else:
                func = lambda x: x                 
            d.append((k, func(v)))

        return collections.OrderedDict(d)

    def load(self, spec):
        """
        Load a dictionary. Call element-specific handler if it exists. 
        """

        if isinstance(spec,list):
            final = []
            for i in spec:
                final.append(i)

        elif isinstance(spec,dict):
            final = {} 
            for k, v in spec.items():
                if hasattr(self, 'load_' + k):
                    func = getattr(self, 'load_' + k)
                else:
                    func = lambda x: x
                final[k] = func(v)

        # Check to make sure the spec is complete and valid 
        self.validate(final)

        # Save 
        self.spec = final  
    
    def dumps(self):
        """
        Dump the internal structure into JSON-formatted string
        """
        return json.dumps(self.dump(), indent=4)

    def loads(self, s):
        """
        Load a serialized string into a object
        """
        self.load(json.loads(s))

    def prettyprint(self, max_width=80):
        """
        Dump content in a neat form..
        """

        rows = [
            ('Dimension', 'Summary'),
            ('schema', self.schema)
        ]

        # Take a union of order and required 
        order = self.order
        for k in self.required:
            if k not in order:
                order.append(k)

        allkeys = sorted(list(self.spec.keys()))
        for k in allkeys:
            if k in self.order or k == 'schema':
                continue
            order.append(k) 
        # => Now follow the order computed
        for k in order:
            summary = "" 
            if isinstance(self.spec[k],list): 
                for v in self.spec[k]:
                    if hasattr(v, 'prettyprint'):
                        v = v.prettyprint(max_width=max_width-20)
                    else:
                        v = str(v)
                    summary += v + "\n"
            else:
                v = self.spec[k]
                if hasattr(v, 'prettyprint'):
                    summary = v.prettyprint(max_width=max_width-20)
                else:
                    summary = str(v)                    
            rows.append((k, summary))
            
        table = texttable.Texttable(max_width=max_width)
        table.add_rows(rows) 
        return table.draw() 

class SpecManagerBase():
    def __init__(self, *args, **kwargs):
        self.spec_files = []
        """
        Accept path and read list of spec files available in path. 

        required prefix: spec_
        """
    @classmethod
    def scan_dir(self,path_):
        return glob.glob(os.path.join(path_,'spec_*.json'))+ glob.glob(os.path.join(path_,'spec_*.yaml'))
