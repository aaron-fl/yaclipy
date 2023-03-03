yaclipy
=======

Yet another python command-line interface...

This is similar to `python-fire <https://github.com/google/python-fire>`_ with a few important distinctions:
 * Parameter types are defined by the function definition and not by what was given on the command line
 * Sub commands are given explicitly.  This gives the ability to show and create documentation for sub commands without executing them.  You can still call methods of the returned values though.
 * Better documentation of the commands.

Define functions and annotate them with a `@CLI` decorator.  Then those functions can be called from the command line.


.. _Get Started:

Get Started
===========

Create a file named ``cli.py`` (or anything) with the following code.
Make it executable: ``chmod +x cli.py``.

.. code-block:: python

    #!/usr/bin/env python
    import os, sys
    from subprocess import call # Just in case the system python is crazy-old
    from os.path import join, abspath, split, exists

    VENV_DIR='.python' # This can be moved if needed

    def abort(*reason):
        print('\n'+'!'*75,'\nERROR:', *reason)
        print('Look above for the specific error.','\n'+'!'*75,'\n')
        import shutil
        shutil.rmtree(VENV_DIR, ignore_errors=True)
        sys.exit(1)

    os.chdir(split(abspath(__file__))[0]) # Make the cwd the same as this file
    if sys.prefix == sys.base_prefix: # Not in the virtual env
        new = not exists(VENV_DIR)
        if new and call(['python3', '-m','venv',VENV_DIR]):
            abort("Couldn't create python3 virtual environment at", VENV_DIR)
        os.environ['PATH'] = join(VENV_DIR,'bin') + os.pathsep + os.environ['PATH']
        if new and call(['python', '-m', 'pip', 'install', 'yaclipy']):
            abort("Couldn't install yaclipy into the virtual environment")
        os.execvp('python', ['python', './cli.py'] + sys.argv[1:])

    # Now we are running in the virtual environment.  Turn control over to yaclipy
    from yaclipy.boot import bootstrap
    bootstrap(sys.argv[1:])


This file simply bootstraps a project-local virtual environment ``VENV_DIR``, installs yaclipy into it and then turns control over to yaclipy.

Next create a ``requirements.txt`` file which holds the package dependencies that need to be installed into the virtual environment.

.. code-block:: text

    # *NOTE*
    # If you edit this file then delete the `requirements.lock` 
    # file and run `./cli.py` to update the new dependencies
    
    PyYAML
    numpy
    # etc...


Finally, you can start using ``cli.py``.

.. code-block:: console
    
    $ ./cli.py -h



Installation
============

Don't install this package manually.
Instead use the bootstrapping method show in `Get Started`.

.. code-block:: console
   
   $ pip install yaclipy # Don't do this!


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
