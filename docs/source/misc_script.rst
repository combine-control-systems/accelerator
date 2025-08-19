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

A change to a job script’s source code will cause a new job to be
built upon running .build(), but *sometimes it is desirable to modify
the source code without causing a re-build*.  This happens, for
example, when new comments are added to an existing job script, and
re-computation of all jobs is not an option for time reasons.  If the
functionality after a change is *known* to remain the same, existing
jobs strictly do not need to be re-built. For this special situation,
there is an equivalent_hashes dictionary that can be used to manually
specify which versions of the source code that are equivalent.  Exax
helps creating this dictionary, if needed.  Here is how it works.

  1. Find the hash <old_hash> of the existing job in that job’s setup.json.
  2. Add the following line to the updated method’s source code

     .. code-block::

        equivalent_hashes = {'whatever': (<old_hash>,)}

  3. Run the build script. The server will print something like

     .. code-block::

        ===========================================================
        WARNING: test_methods.a_test_rechain has equivalent_hashes,
        but missing verifier <current_hash>
        ===========================================================

  4. Copy ``<current_hash>`` into the ``equivalent_hashes``:

     .. code-block::

        equivalent_hashes = {<current_hash>: (<old_hash>,)}

This line now tells that current_hash is equivalent to old_hash, so if
a job with the old hash exists, the job script will not be built
again.  Note that the right part of the assignment is actually a list, so
there could be any number of equivalent versions of the source code.

From time to time, this has been used during development of Exax's
standard_methods, but for everyday work it should probably be avoided.



Accessing a Job's parameters
----------------------------

All job parameters are available in the ``Job.params`` dict.  It
contains a lot of information, including start and end timestamps,
exax version, python version, location of paths defined in the
configuration file, and more

.. code-block::

   job = urd.build('example')
   print(job.params)
   print(job.params.starttime)
   print(job.params.options)
   print(job.params.jobs)



Accessing a Job's post data
---------------------------

The post data is written when the job finishes.  It contains profiling
information (execution time) for ``prepare``, ``synthesis``, and all
``analysis`` slices, as well as any subjobs built or files created.

.. code-block::

   job = urd.build('example')
   print(job.post)


Creating Custom Status Messages
-------------------------------

Most built-in job scripts and functions, such as for example ``csvimport``
and ``json_load()``, provide their own status messages to be displayed
when pressing ``CTRL+T`` (see :ref:`job_scripts:Progress/status reporting`).
However, it is also possible to create custom status messages for your
scripts using the status context manager. Here's an example:

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
``CTRL+t`` is pressed.
