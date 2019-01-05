"""
Hallmark Command Line 
------------------

"""
import os
import sys
from texttable import Texttable
import click

from . import spec 

@click.group()
def main():
    """ 
    Commandline for Hallmark Specifications 
    """
    pass


@main.group("schema")
def schema():
    """
    Discovery and operation specification formats
    """
    pass 


@schema.command("list")
def _schema_list():
    """
    List available schemas 
    """

    parser = spec.parser() 
    summary = parser.schema_list()
    table = Texttable()
    table.add_rows(summary)
    print(table.draw())

#@schema.command("show")
#@click.argument("schema")
#def _schema_show(schema):
#    """
#    Show details of a schema
#    """
#
#    merit = MeritDefault() 
#    cls = merit.schema_get(schema)
#    help(cls)
#
#@main.group("metadata")
#def metadata():
#    """
#    Metadata processing
#    """
#    pass
#
#@metadata.command("show")
#@click.argument("filename")
#def _metadata_show(filename):
#    """
#    Show metadata content
#    """
#
#    merit = news(open(filename).read())
#    print(merit.prettyprint())
#
