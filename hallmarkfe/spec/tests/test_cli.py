import os
import sys
import pytest
import click
from click.testing import CliRunner

from hallmarkfe.cli import main as climain 

def test_main():
    """
    Test cli main 
    """

    runner = CliRunner()
    result = runner.invoke(climain, [])

    assert result.exit_code == 0
    assert "Commandline for Hallmark" in result.output 

def test_schema():
    """
    Test cli schema 
    """

    runner = CliRunner()
    result = runner.invoke(climain, ['schema'])

    assert result.exit_code == 0
    assert "Discovery and operation" in result.output 
    assert "List available schemas" in result.output 

def test_schema_list():
    """
    Test cli schema list
    """

    runner = CliRunner()
    result = runner.invoke(climain, ['schema', 'list'])

    assert result.exit_code == 0
    assert "global:default:v1" in result.output 
    

