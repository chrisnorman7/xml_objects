Installation
============

Installing Using pip
====================

It is recommended that you install xml_python using pip::

    pip install xml_python

Install Using Git
=================

Alternatively, you could install using git::

    git clone https://github.com/chrisnorman7/xml_python.git
    cd xml_python
    python setup.py install

Running Tests
=============

To run the tests, you will need to install `pytest <https://pytest.org/>`_::

    pip install pytest

Then to run the tests::

    py.test

Building Documentation
======================

You can always find the most up to date version of the docs on `Read the Docs <https://xml_python.readthedocs.io/en/latest/>`_, but you can also build them yourself::

    pip install -Ur docs/requirements.txt
    python setup.py build_sphinx
