===========
 hallmarkfe
===========

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

This package is in early stages of the development. So please get in
touch with the developers before using.

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

::

  (venv)$ pip3 install hallmarkfe

Usage
=====

::

  $ python
  >>> import hallmarkfe
  >>> hallmarkfe.sample.hello()
  'hello'
  >>>

