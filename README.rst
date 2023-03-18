yaclipy
=======

Yet another python command-line interface that has a consistent way to call any kind of function/method from the command line.

Features
--------

* Sub commands are known deterministically.  They are parsed before any commands are executed.
* Easy-to-read documentation automatically shown from the docstring with `=h` or `--help`.
* The function's annotations and default values are used to coerce the command line arguments to the correct type.
* A consistent way to call all kinds of function signatures (using inspect.signature to the fullest extent).
* Ability to accept multiple list-typed parameters.
* \*args and \*\*kwargs have useful abilities.



Getting Started
===============

While not the recommended way of using yaclipy, this is the simplest yet meaningful example.

Given the following file named `cli.py`:

.. code-block:: python

    #!/usr/bin/env python
    import sys
    from print_ext import print, PrettyException
    import yaclipy as CLI

    def main(say, times__t=1) -> str:
        ''' Say something multiple times

        Parameters:
            <message>, --say <message>
                What you want to say
            <int>, --times <int>, -t <int>
                How many times you want to say it.
        '''
        return ' '.join([say] * times__t)

    if __name__ == '__main__':
        try:
            CLI.Command(main)(sys.argv[1:]).run()
        except PrettyException as e:
            print.pretty(e)


Given that the file is executable ``chmod +x cli.py``, you can use it as follows.

.. code-block:: console

   $ ./cli.py -h
   <doc string>

Using ``-h`` or ``--help`` will show the docstring documentation, along with a list of possible sub-commands.
Sub-commands are determined explicitly with the ``sub_cmds`` decorator, or by the return type annotation.

.. code-block:: console

    $ ./cli.py -t 3 --say Ho
    Ho Ho Ho

You may use a single dash for single character names, otherwise use double-dashes.
Names defined with double underscores separate the aliases that can be used on the command line (``--times`` or ``-t``).

The ``say`` parameter has no type information so it will be a string.
The ``times__t`` parameter's default value is an int, so you can only pass integers.  ``-t hi`` will fail with an error.

.. code-block:: console

   $ ./cli.py "Hello World" 2
   Hello World Hello World

Since the parameters are defined as keyword *or* positional, you can pass them positionally.

.. code-block:: console

   $ ./cli.py go --times 3 upper
   GO GO GO

When positional and keyword parameters are used simultaneously, positional arguments always come first.
``upper`` is the start of a new command.  In this case it is executed on the return value ``str`` of the previous command.

If the value returned from a command is not ``None`` then the value is pretty printed.

.. code-block:: console

   $ ./cli.py \\--times
   --times

Keyword arguments are identified with dashes.
If you want to use a value that starts with a dash then it must be escaped with a backslash.  
The shell eats one backslash if you don't surround the argument in quotes.

Only the leading backslash is removed.  If you specify only a backslash ``./cli.py \\`` then an empty string will be consumed as the first argument.

Negative numbers such as ``-.3``, ``-0.5e33`` don't need to be escaped.

----

The following examples introduce more complicated examples.
They just show the function declaration for brevity.



Positional vs. Keyword
----------------------

.. code-block:: python

    def foo(a=3, /, banana__b='hi', *, carrot__c:int=None):
        ''' Foo

        Parameters:
            <int>
                Positional only
            <str>, --banana <str>, -b <str>
                Positional or keyword
            --carrot <int>, -c <int>
                Keyword only
        '''
        # foo 4 bye --carrot 42
        # foo 4 -c 42 -b bye
        a == 4
        banana__b == 'bye'
        carrot__c == 42

The distinction between position-only, positional or keyword and keyword-only parameters is important.
Parameters before the ``/`` cannot be specified by name.  Parameters after the ``*`` `must` be given by name.
Other parameters may be given either way.

Notice how the docstring documentation indicates the positionally.



Flags
-----

.. code-block:: python

    def foo(*, verbose__v=False, times__t:int):
        ''' Flags example

        Parameters:
            --verbose, -v
                More verbose
            --times <int>, -t <int>
                How many times
        '''
        # foo -vt 3 --verbose
        # foo -vv --times 3
        verbose__v == 2
        times__t == 3

Flags are specified by a default value of ``False``.
You can't use ``bool`` as a type in any other way such as ``x:bool`` or ``y:[bool]``.

Flags can be specified multiple times in which case its value won't be ``True``, but an integer specifying how many times it was given.
Since ``int(True) == 1`` you can use ``int(verbose__v)`` to get the number of times it was specified.

Since flag arguments don't take value, single letter flags can be combined together in the usual way.
The last letter of the group may be a non-flag type that consumes the succeeding value.



Special Names
-------------

.. code-block:: python

    def foo(*, if_=1, happy_days=2, lots__of__aliases__t__q=3, _hidden=4):
        # foo --if 10 --happy-days 20 --happy_days 200 --lots 30 --of 40 --aliases 50 -t 60 -q 70
        if_ == 10
        happy_days == 200
        lots__of__aliases__t__q == 70
        _hidden= == 4

This shows the various naming schemes that exist.

* A trailing underscore is ignored and used to alias keywords.
* Single underscores may be given as dashes instead
* Double dashes separate aliases.  There can be multiple.
* Leading underscores indicate private variables that cannot be set from the command line.
  They must have a default value or be set from the previous call in the call chain (described below).



Sub-Commands
------------

.. code-block:: python

    import yaclipy as CLI

    def foo(*, name, _value): pass

    def bar(*, name, _value): pass

    @CLI.sub_cmds(foo, baz=bar)
    def root(*, verbose__v=False):
        return dict(name='jim', _value = 'hi' * int(verbose__v))

    # root -v foo -h
    # root -v baz --name bob

Commands can be chained together.
The sub-commands available are known deterministically, either explicitly with the ``sub_cmds`` decorator, or implicitly from the return type annotation.

The complete chain of commands is fully parsed before any commands are actually executed.
By making the sub-command lookup deterministic we can provide better help and documentation support.
Also, any command-line syntax errors in sub-commands are caught before anything is executed.

The return value of the previous command is passed to the next command.
If the return value is a dictionary then its values will be initially applied to the function's keyword parameters.

The values override the parameter's default value, but a matching command line argument has highest priority.
In the second example above, the name argument ``bob`` overwrites ``jim`` that was provided in the return value.

If the function defines a special ``_input`` parameter then the return value of the parent will be applied to it directly.



Generators
----------

.. code-block:: python
    
    def show(*, _input):
        x, xxx = _input
        print(f'3^{x} == {xxx}')

    @CLI.sub_cmds(show)
    def foo(*, times__t=3):
        for i in range(times__t):
            yield i, pow(3,i)

    # foo -t 4 show
    
If a generator is used then it can yield a value to the sub-command and then continue with cleanup-code after the sub-command completes.

By returning or yielding a dictionary you can set keyword parameters of the sub-command.
If the function defines a special ``_input`` parameter then the return value of the parent will be applied to it directly.



Lists
-----

.. code-block:: python

    def foo(a:int, b:[float], c=[]):
        # foo 3 1.1 -.1 1e3 - 66 \\-apples
        # foo -c 66 -c \\-apples -b#3 1.1 -0.1 1e3 -a 3
        # 3 1.1 - -c# 66 \\-apples - -b#2 -.1 1e3
        a == 3
        b == [1.1, -0.1, 1e3]
        c == ['66', '-apples']

In this example type annotations are used for the first two parameters.
Since the inside of the third list is unknown, `str` is assumed.

The two examples above are equivalent ways of setting the parameters.

There are three ways to set lists.

1. For positional parameter lists, values are taken until a value that starts with a dash is encountered.
   A single dash ``-`` may be used to to indicate that we are done with this positional parameter.
   To include a value that starts with a dash (such as a single dash) the leading dash needs to be escaped ``\\-``.
   Negative numbers don't need to be escaped.
2. For keyword parameters you can use repeated application of the argument ``-c 66 -c \\-apples``.
   If the argument's value starts with a dash then it needs to be escaped or it will be treated as the next keyword argument.
3. For keyword parameters you can use the ``--arg#N`` syntax to specify that the following ``N`` values are in the list.  If you don't specify N, ``--arg#``, then values are taken just like a positional parameter until a single dash, or another keyword argument, is encountered.

The three ways can be mixed and matched, but positional arguments must always precede keyword arguments.



JSON
----

.. code-block::python

    def foo(*, x={}, y:dict):
        # foo -x "{"x":[1,2,3]}" -y null
        x == {'x':[1,2,3]}
        y == None

A parameter of type ``dict`` is parsed as json.  It may, or may not parse to a dict.



\*args
------

The `lists` section above discussed how to get lists of values.
But that way has a couple of limitations.
Keyword arguments must follow the position arguments which is unnatural for commands that deal with file globs.
Also, values starting with a dash must be escaped.

By specifying ``*args`` you can get around these limitations because it just captures all un-processed trailing arguments.
This comes with its own limitations.  Obviously, it can't have any sub-commands.

.. code-block:: python

    def foo(first=None, *files, verbose__v=False):
        # foo *
        # foo - *
        # foo - - *
        # foo -- *

In the first example, the first file name is captured by ``first`` and the remaining files would go to ``files``.
In the second example, ``first`` is skipped so all files go to ``files``.  

Both the first and second examples have a tricky corner-case.
If you have a file named ``-v`` *(Why!?)* then it would try to set the verbose flag and (hopefully) generate an error.

By explicitly ending the positional and keyword sections with ``-`` you can safely capture all of the files.  The two separate dashes in the third example can be combined together for aesthetics.
If you know that there are no crazy files starting with a dash then the first two ways are fine.



\*\*kwargs
----------

.. code-block:: python

    def foo(a=False, **kwargs) -> str:
        # foo -axd 33 -d 44 --apple x --banana - upper
        a == True
        kwargs == {'x':True, 'd':['33','44'], 'apple':'x', 'banana':True}
        return str(kwargs)

The rules for capturing arbitrary key-values are as follows.

* If it must be a flag, either because it is at the end or in the middle of a flag group, then assume the type is a flag.
* Otherwise, assume a ``str`` if the argument appears once, otherwise ``[str]``

A single dash can be used to stop taking keyword arguments and go to the next command.



Config
======

Often programs need configuration values that can be set for a specific user's environment, or to configure environments such production or test.

The Config system of yaclipy uses the standard python import system for namespacing.
`ConfigVar` objects are declared with ``Config.var()``. 

.. code-block:: python
    
    answer = Config.var("The answer to everything.", 42)
    speech = Config.var("What does the leader say?", "I declare that...")
    a, b = Config.var(), Config.var() # These names will not be 'a' and 'b'.  They will be 'unk'.

The variable name is grepped from the stacktrace, so anything other than ``var = Config.var()`` will result in a name being "unk".

When a variable needs be used, or set it can be brought into scope in the usual way and then read ``a()`` or set ``a("Hello World")``.

Config vars should only be set from special ``@Config.option()`` decorated functions.  This creates a ``ConfigOption`` class that can configure all of the necessary variables for a specific application environment or purpose.

.. code-block:: python

    @Config.option()
    def one():
        answer(1)
        speech("I am the one")

    @Config.option()
    def two():
        answer(2)
        speech("I am not the one")

This creates two different configuration options.
Use ``Config.configure('one')`` to execute the ``one()`` option and set the corresponding config vars.

Additional config files can be imported in the usual way from your main ``config.py`` root file.
``with Config.include: import local.config`` can be used for optional, possibly non-existent modules.

In these local config modules it is common to want to override and existing option.

.. code-block:: python

    # local/config.py
    import config

    @config.two.override()
    def two(super):
        super() # This is the old two() function
        answer(-answer())



cli.py
======

Instead of installing yaclipy into the system, it is better to manage python packages on a per-project basis with virtual environments.

To easily facilitate this style, copy the contents of `examples/venv` to your project directory and then run `./cli.py`.

The `cli.py` file simply bootstraps a project-local virtual environment ``VENV_DIR``, installs yaclipy into it, and then turns control over to yaclipy.

The ``requirements.txt`` file holds the package dependencies that need to be installed into the virtual environment.  When changing dependencies make sure to delete the corresponding lock file so that the changes are picked-up.



Installation
============

Instead of installing this manually, use the bootstrapping method shown above in ``examples/venv``.

.. code-block:: console
   
   $ pip install yaclipy


.. image:: https://img.shields.io/pypi/v/yaclipy.svg
   :target: https://pypi.org/project/yaclipy


.. image:: https://img.shields.io/pypi/pyversions/yaclipy.svg
   :target: https://pypi.org/project/yaclipy



Plugins
=======

Other libraries may be imported and used as sub-commands.



Test
====

.. code-block:: console

   $ hatch shell
   $ pytest



License
=======

`yaclipy` is distributed under the terms of the `MIT <https://spdx.org/licenses/MIT.html>`_ license.
