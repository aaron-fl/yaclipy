yaclipy
=======

Yet another python command-line interface...

This is similar to `python-fire <https://github.com/google/python-fire>`_ with a few important distinctions:
 * Parameter types are defined by the function definition and not by what was given on the command line
 * Sub commands are given explicitly.  This gives the ability to show and create documentation for sub commands without executing them.  You can still call methods of the returned values though.
 * Better documentation of the commands.

Define functions and annotate them with a `@CLI` decorator.  Then those functions can be called from the command line.


.. _Get Started:

Quick Reference
===============

Given the following file named `cli.py`:

.. code-block:: python
    #!/usr/bin/env python
    import sys
    from yaclipy import boot, SubCmds

    def foo(id, /, arg__a=3, *, cats__c:int):
        ''' Foo stuff

        Parameters:
            <id> *required*
                The foo id to manipulate.  Positional only
            <int>, --arg <int>, -a <int>
                This can be specified by position or by name.
            --cats <int>, -c <int>
                The number of cats.  keyword-only parameter
        '''

    def bar(a:[float], names:[], *, flags__f=['empty']):
        ''' Bar-like things

        Parameters:
            [float]
                Data points
            [name]
                List of names
            --flags [flag], -f [flag]
                Compiler flags
        '''

    @SubCmds(foo, bar)
    def main(*, verbose__v=False, quiet__q=False):
        ''' The main entrypoint for calling foo and bar.

        Parameters:
            --verbose, -v
                More output
            --quiet, -q
                Less output
        '''

    if __name__ == '__main__':
        boot(main, sys.argv[1:])


Then you can call call the 


cli.py
======

Instead of installing yaclipy into the system it is better to manage python packages on a per-project basis with virtual environments.

To easily facilitate this style copy the contents of `examples/venv` to your project directory and then run `./cli.py`.

The `cli.py` file simply bootstraps a project-local virtual environment ``VENV_DIR``, installs yaclipy into it, and then turns control over to yaclipy.

The ``requirements.txt`` file holds the package dependencies that need to be installed into the virtual environment.  When changing dependencies make sure to delete the corrosponding lock file so that the changes are picked-up.



Installation
============

Instead of installing this manually, use the bootstrapping method show in `cli.py`.

.. code-block:: console
   
   $ pip install yaclipy


.. image:: https://img.shields.io/pypi/v/yaclipy.svg
   :target: https://pypi.org/project/yaclipy


.. image:: https://img.shields.io/pypi/pyversions/yaclipy.svg
   :target: https://pypi.org/project/yaclipy



Test
====

.. code-block:: console

   $ hatch shell
   $ pytest



License
=======

`yaclipy` is distributed under the terms of the `MIT <https://spdx.org/licenses/MIT.html>`_ license.
