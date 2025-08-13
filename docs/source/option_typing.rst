More on Option Typing
=====================

This chapter is dedicated entirely to typing of job script input
options.  Some exax-specific types are introduced, followed by a list
of common typing examples, and at the end is a set of formal typing
rules.



Additional Option Types
-----------------------

Exax can use most of Python's basic datatypes, and in addition it
defines a few more for convenience and stricter type checking.


Additional Option Type: ``OptionString``
..........................................

A common special case is to hava a mandatory string option.  The
``OptionStrin()`` function is designed for this.

.. code-block::

   from accelerator import OptionString

   options={
       'name1': OptionString,
       'name2': OptionString('example'),
   }

Both rows mean the sam thing.  The string 'example` is just that: an
example of what is expected.  It is not used as default
value. ``OptionString`` does not accept None as input.



Additional Option Type: ``RequiredOption``
..........................................

If an option (of arbitrary type) is mandatory, this can be specified
using the ``RequiredOption()`` function:

.. code-block::

   from accelerator import RequiredOption

   options={
       'age': RequiredOption(int),
   }

Using this definition, execution will stop if ``age`` is left
unassigned, and a helpful error message will appear.

By default, it is not okay to set the option to None, but permission
is given by setting ``none_ok=True``:

.. code-block::

   options={
       'maybeage': RequiredOption(int, none_ok=True),
   }

in this case is accept an explicit ``None`` as well, but it is not
allowed to leave the option unassigned.



Additional Option Type: ``OptionEnum``
..........................................

Alternatively, if the expected values belong to a closed set, one can
use the ``OptionEnum()`` function:

.. code-block::

   from accelerator import OptionEnum

   options={
       'colour': OptionEnum('red green blue')
       # or
       'color': OptionEnum(['red', 'green', 'blue'])
   }

This will throw an error if the option is not set to one of these
three alternatives.

``OptionEnum`` also accepts a ``none_ok=True`` parameter, allowing the
parameter to be set explicitly to ``None`` as well.

An ``OptionEnum`` cannot be left unassigned, unless a default value is
specified, like this

.. code-block::

   options={
       'color': OptionEnum(['red', 'green', 'blue']).green
   }


Additional Option Type: ``JobWithFile``
.......................................

It is possible to explicitly specify explicit files from specific jobs
in a ``build()`` call using the ``JobWithFile`` class.  Here is an example

.. code-block::

   def main(urd):

       job1 = urd.build('example1')
       job2 = urd.build('example2')

       urd.build('example3',
           firstfile=job1.withfile('myfile1', sliced=True),
           secondfile=job2.withfile('myfile2')
       )

where the options definition part of the job script for ``example3``
looks like this

.. code-block::

   from accelerator import JobWithFile

   options=dict(
       firstfile=JobWithFile,
       secondfile=JobWithFile
   )

The ``.withfile()`` function takes a filename argument, and in
addition two optional arguments: ``sliced`` and ``extras``. The
``extras`` argument is used to pass any kind of information that is
helpful when using the speciﬁed file, and ``sliced`` tells that the
file is stored in parallel slices.

The files are loaded usinf ``.load()``, like this

.. code-block::

   def analysis(sliceno):
       print(options.firstfile.load(sliceno=sliceno))

   def synthesis():
       print(options.secondfile.load())

The ``.load()`` function assumes that the file is in Python Pickle
format, and there is also an ``.json_load()`` function for
JSON-ﬁles. To get the full filename of the file, use ``.filename()``

.. code-block::

       print(options.firstfile.filename(sliceno=3))
       print(options.secondfile.filename())

There is also the wrapper around open(), so it is possible to use ``open()``

.. code-block::

       with(options.firstfile.open(), 'rb') as fh:
           data = fh.read()

and have full flexibility.



Typing Examples
---------------

.. code-block::

   from datetime import datetime, date, time, timedelta
   from accelerator import OptionString, OptionEnum, RequiredOption

   options = dict(
      # no type
      length=None         # accepts anything, default is None

      # scalar
      length=int          # requires intable or None, default is None
      length=3            # requires intable or None, default is 3

      # string
      name=str            # requires string or None, default is None
      name='foo'          # requires string or None, default is 'foo'
      name=OptionString   # requires non-empty string
      # same, but with a guiding example, NOT a default value
      name=OptionString('example')

      # enums
      foo=OptionEnum('a b c')                # requires 'a', 'b', or 'c'
      foo=OptionEnum(['a', 'b', 'c'])        # same
      foo=OptionEnum('a b c').a              # requires 'a', 'b', or 'c', default is 'a'
      foo=OptionEnum('a b c', none_ok=True)  # requires 'a', 'b', 'c' or None

      # lists and sets
      bar=[int]         # requires list of intables or None, defaults to []
      bar={int}         # same, but for set

      # dates, times, datetimes, and timedeltas
      ts=datetime             # a datetimeable object or None
      ts=datetime(1972, 1, 1) # with default value
      # date, time. timedelta are similar

      # types containing types
      baz={str: str}        # requires dict of string to string or None
      baz={str: {str: int}} # requires dicto of string to dict of string to int or None
      # Containers with types default to empty containers

      frob=RequiredOption(int)                 # requires an int
      frob=RequiredOption(int, none_ok=True)   # requires an int or None
   )



Option Typing Formal Rules
--------------------------

This section outlines all typing rules.  Consider the following
example:

.. code-block::

   options = dict(
                    # types to   input = 3  input = 3.3  input = '3'  input='3.3'
       a = 3,       #    int         3          3            3          ERROR
       b = int,     #    int         3        ERROR          3          ERROR
       c = 3.14,    #   float       3.0        3.3         ERROR         3.3
       d = ''       #    str        '3'       '3.3'         '3'         '3.3'


1. Typing may be specified using a class name (i.e. ``b = int``) or as a
   value belonging to the intended class (i.e.  ``a = 3``).

2. An input is required to be of the correct type. Values are accepted
   if they are valid input to the type's constructor.  For example
   ``int(3)``, ``int(3.3)``, and ``int('3')`` are okay, but
   ``int('3.3')`` is not.

3. Default values

     - If values are specified, like for ``a``, ``c``, and ``d``
       above, these values are default values and will be used if the
       option is omitted in the ``build()``-call.

     - If the type is specified as a class, like for ``b = int``
       above, the default value will be ``None``.

4.  ``None`` is always accepted, unless the type is
      - ``RequiredOptions(..., none_ok=False)``
      - ``OptionEnum(..., none_ok=False)``
      - ``OptionString()``

5. Inputs can be left unassigned, unless the type is
     - ``RequiredOption()``
     - ``OptionEnum()`` without a default value.
     - ``OptionString``

6. Containers.  ``{}`` specifies a ``dict`` etc.
