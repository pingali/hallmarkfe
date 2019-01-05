"""
Utils
-----

Helper functions 
"""
import json

def generate_attribute(name):
    
    @property
    def prop(self):
        return self.spec[name] 
    
    @prop.setter
    def prop(self, value):
        self.spec[name] = value 

    return prop 
