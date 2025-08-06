Script Miscellaneous
====================

Depend on extra files
---------------------

A job script may import and execute code located in other files. Such
files can be included in the build check hash calculation as well.
This will ensure that a change to an imported file will indeed force a
re-execution of the job script when a build is requested.  Specify
additional files using the ``depend_extra`` list early in the job
script, as in this example

.. code-block::
   from . import my_python_module

   depend_extra = (my_python_module, 'my_other_file',)

As seen above, it is possible to specify either imported Python module
objects or filenames relative to the method's location.

If Exax suspects that a ``depend_extra``-statement is missing, it will
suggest adding it by printing a message in the output log like this

.. code-block:: text

   ====================================================================
   WARNING: dev.a_test should probably depend_extra on my_python_module
   ====================================================================

.. note:: ``depend_extra`` will add the external source code to the
          current job directory and include them in the hash computation.

          To keep operation fast and limit disk occupied by file
          copies, do not depend_extra on more than is actually needed.


Equivalent Hashes
-----------------


Accessing a Job's parameters
----------------------------


Accessing a Job's post data
---------------------------


jobWithFile





Status and Progress Reporting
-----------------------------

Ideally, jobs should complete fast.  When they do not, it is easy to
check the progress using the built in status functionality.  Status is
invoked by pressing ``C-t`` in the server or build terminals.

.. tip ::  Press C-t (That is CTRL + t) at any time to see status.

It is also possible to issue the ``ax status`` command.

.. tip :: The shell command ``ax status`` provides status information
   *as well as the last error that has occured*.

.. tip :: The status is also available in exax Board.

Status messages are used by most built-in job scripts and functions,
such as for example ``csvimport`` and ``json_load()``, and it is
straightforward to design new ones.


Creating Status Messages
........................

It is possible to create status messages using the status context
manager.  Here's an example

.. code-block ::
   :caption: Example of status context manager with static content.

   from accelerator import status
   ...
   def synthesis():
       with status('reading huge file') as s:
           jobs.source.load('bigfile')

And here's another example that updates the status message to reflect
the progress of the program

.. code-block ::
   :caption: Example of status context manager with dynamic content.

   from accelerator import status
   ...
   def analysis(sliceno):
       msg = "reached line %d already!"
       with status(msg % (0,) as update:
           for ix, data in enumerate(datasets.source.iterate(sliceno, 'data')):
           if ix % 1000000 == 0:
               update(msg % (ix,))

The last created status message will be printed to ``stdout`` when
``C-t`` is pressed.
