.. image:: https://coveralls.io/repos/github/abhiramr/hallmarkfe/badge.svg?branch=master
    :target: https://coveralls.io/github/abhiramr/hallmarkfe?branch=master


.. image:: https://img.shields.io/travis/abhiramr/hallmarkfe/master.svg 
    :target: https://travis-ci.org/abhiramr/hallmarkfe



**[NOTE] This package is in early stages of the development. So please get in
touch with the developers before using.**


===========
 hallmarkfe
===========

.. important::
   This library is still under development. Wait for the release.

Python package to specify and process ML features over flexible data
sources - batch and streaming. 

The problem that this package solves is that:

(a) Usually the codebases of batch and realtime feature engineering
    diverge causing errors.
(b) Feature are specified in code and not easily verifiable
(c) Features are not reusable and often implemented in non-standard
    ways

This package helps:

(a) Share code bases across batch and realtime paths
(b) Provides a way to explicitly specify the features
(c) One implementation of the feature specification called supernova
(d) Allows unit testing of the features before they are put into
    production


See `documentation`_ for interface details.

.. _documentation: https://hallmarkfe.readthedocs.io


Requirements
============

* Python 3.5 over or PyPy 2.4.0 over

Features
========

* Embeddeable python package across batch and realtime (e.g., pyspark)
* Extensible schema for feature specification
* Custom feature handlers/executors 

Setup
=====

  Clone and download the package.
::

  (venv)$ pip3 install -e .

Usage
=====

API
---

::

  # A feature specification 
  $ cat spec_user.json
  {
      "schema": "user:default:v1",
      "name": "completed_orders",
      "owner": "example@example.com",
      "description": "This feature represents a user's total completed orders",
  
      "id": "user.completed_orders",
      "entity": "user",
      "granularity": "NONE",
      ...
  }

  # Now parse it..
  $ python
  >>> import json 
  >>> import hallmarkfe
  >>> handler = hallmarkfe.parse_generic('spec_user.json')
  >>> handler 
  <hallmarkfe.spec.base.SpecBase at 0x7f08edf366d8>
  >>> print(handler.prettyprint())
  +-------------+----------------------------------------------------------------+
  |  Dimension  |                            Summary                             |
  +=============+================================================================+
  | schema      | global:default:v1                                              |
  +-------------+----------------------------------------------------------------+
  | name        | completed_orders                                               |
  +-------------+----------------------------------------------------------------+
  | description | This feature represents a user's total completed orders        |
  +-------------+----------------------------------------------------------------+
  | owner       | feast@example.com                                              |
  +-------------+----------------------------------------------------------------+
  | dataStores  | {'warehouse': {'id': 'example_warehouse'}, 'serving': {'id':   |
  |             | 'example_serving'}}                                            |
  +-------------+----------------------------------------------------------------+
  | entity      | user                                                           |
  +-------------+----------------------------------------------------------------+
  | granularity | NONE                                                           |
  +-------------+----------------------------------------------------------------+
  | id          | user.none.completed_orders                                     |
  +-------------+----------------------------------------------------------------+
  | options     | {}                                                             |
  +-------------+----------------------------------------------------------------+
  | tags        |                                                                |
  +-------------+----------------------------------------------------------------+
  | uri         | https://example.com/                                           |
  +-------------+----------------------------------------------------------------+
  | valueType   | INT32                                                          |
  +-------------+----------------------------------------------------------------+
    
CLI
---

::
   
  $ hfe 
  Usage: hfe [OPTIONS] COMMAND [ARGS]...
  
    Commandline for Hallmark Specifications
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    schema  Discovery and operation specification formats
  $ hfe schema
  Usage: hfe schema [OPTIONS] COMMAND [ARGS]...
  
    Discovery and operation specification formats
  
  Options:
    --help  Show this message and exit.
  
  Commands:
    list  List available schemas
  $ hfe schema list
  +-------------------+----------+-----------------------------------------------+
  |      Schema       |  Class   |                    Module                     |
  +===================+==========+===============================================+
  | global:default:v1 | SpecBase | /work/pingali/Code/pingali-                   |
  |                   |          | hallmarkfe/hallmarkfe/spec/base.py            |
  +-------------------+----------+-----------------------------------------------+
  
