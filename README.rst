========
Overview
========

.. start-badges

.. list-table::
    :stub-columns: 1

    * - docs
      - |docs|
    * - tests
      - | |requires|
        |
    * - package
      - | |version| |wheel| |supported-versions| |supported-implementations|
        | |commits-since|

.. |docs| image:: https://readthedocs.org/projects/hackery2/badge/?style=flat
    :target: https://readthedocs.org/projects/hackery2
    :alt: Documentation Status

.. |requires| image:: https://requires.io/github/koo5/hackery2/requirements.svg?branch=master
    :alt: Requirements Status
    :target: https://requires.io/github/koo5/hackery2/requirements/?branch=master

.. |version| image:: https://img.shields.io/pypi/v/hackery2.svg
    :alt: PyPI Package latest release
    :target: https://pypi.python.org/pypi/hackery2

.. |commits-since| image:: https://img.shields.io/github/commits-since/koo5/hackery2/v0.1.0.svg
    :alt: Commits since latest release
    :target: https://github.com/koo5/hackery2/compare/v0.1.0...master

.. |wheel| image:: https://img.shields.io/pypi/wheel/hackery2.svg
    :alt: PyPI Wheel
    :target: https://pypi.python.org/pypi/hackery2

.. |supported-versions| image:: https://img.shields.io/pypi/pyversions/hackery2.svg
    :alt: Supported versions
    :target: https://pypi.python.org/pypi/hackery2

.. |supported-implementations| image:: https://img.shields.io/pypi/implementation/hackery2.svg
    :alt: Supported implementations
    :target: https://pypi.python.org/pypi/hackery2


.. end-badges

my bin files and various utils and nonsense stuff

* Free software: BSD license

Installation
============

::

    pip install hackery2
sudo pip3 install  dateutils

Documentation
=============

https://hackery2.readthedocs.io/

Development
===========

To run the all tests run::

    tox

Note, to combine the coverage data from all the tox environments run:

.. list-table::
    :widths: 10 90
    :stub-columns: 1

    - - Windows
      - ::

            set PYTEST_ADDOPTS=--cov-append
            tox

    - - Other
      - ::

            PYTEST_ADDOPTS=--cov-append tox
