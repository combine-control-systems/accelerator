Advanced Script Features
========================

.. _depend-extra-ref:

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
objects or filenames relative to the job script's location.

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
  2. Add the following line to the updated job script’s source code

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

.. tip:: All the job parameters are also available via the *board*.



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



Limiting Concurrency
--------------------

By default, a job containing the analysis() function will be forked
into ``slices`` parallel processes, where ``slices``` is specified in
the Accelerator’s configuration file.  For a well written parallel
program, this can maximise the usage of the computers CPU resources.
On the other hand, there exists job scripts that use a large amount of
memory, perhaps scaling with the number of slices, so unless the
machine has plenty of RAM, these scripts may run out of memory.  One
example of such a script is the standard job script ``dataset_sort``,
which sorts datasets in parallel in all slices for maximum
performance.  Reducing the number of slices globally in the
configuration file to handle the worst case is not the optimal
solution.

Instead, Exax implements a ``concurrency`` parameter that can operate
on a single build call or job script.  It can be set either in the
build call, using the ``concurrency=`` parameter, or on the command
line as an option to the ``ax run`` command.  In both cases, the limit
could be set to all job scripts, or it could be set to a specific job
script only.  While the default behaviour is to fork all
``analysis()``-processes in parallel, the concurrency parameter will
limit the number of forks and dispatch a new ``analysis()``-process as
soon as a previous one is finished untill all slices are exhausted.

For example, if concurrency is set to a number, like this

.. code-block ::

   ax run --concurrency=3 mybuild

or

.. code-block ::

   urd.build('myscript', concurrency=3)

the number of parallel processes is limited to in this case three for
all job scripts . Alternatively, concurrency can be specified for a
single job script like this

.. code-block ::

   ax run --concurrency="dataset_sort=3" mybuild

and all scripts except the ``dataset_sort`` will run on all slices,
while ``dataset_sort`` will run on three slices.

.. note:: A job is not aware of, and does not store, the concurrency
          setting.  There is no way to tell afterwards if the job was
          created using full parallelisation or not.

.. _merge-auto-ref:

Automatic Slice-Data Merging: merge_auto
----------------------------------------

When all ``analysis()`` processes have finished, their results are
available to ``synthesis()`` using the ``analysis_res`` variable.
This variable is actually an iterator, presenting one ``analysis()``
result at a time.

Merging these results has to be done with caution, it is easy to get
it wrong.  In order to save development as well as debugging time, the
``analysis_res`` object has a member function ``merge_auto()``, which
merges the data from all slices into one object.  This section
descripes more in deptht how it works.

To start with, here is the basic setup

.. code-block ::

  def analysis(sliceno):
     data = function(sliceno, ...)
     return data

  def synthesis(analysis_res):
     total = analysis_res.merge_auto()

where ``total`` will contain the merged data from all slices.

The default operation of ``merge_auto()`` is as follows

  - lists are concatenated

    .. code-block ::

      ([1, 2, 3], [4, 5, 6]).merge_auto() == [1, 2, 3, 4, 5, 6]

  - integers are added

    .. code-block ::

      (1, 2, 3).merge_auto() == 6

    This could for example be parallel counting of lines in a log file.

  - types with an ``update()`` member will be updated

    .. code-block ::

      ({'lemon', 'apple'}, {'apple', 'pear'}).merge_auto() == {'lemon', 'apple', 'pear'}

    .. code-block ::

      ({'lemon': 3}, {'lemon': 4}) == {'lemon': 7}

  - each item in a tuple is merged independently

If two sets contain the same element this is considered by default to
be okay, the item is a member of at least one of the input sets, like
the lemon, apple, pear example above.

But for dictionaries, the same key may have different values in
different input sets, and the question is then what to do, like in
this example

  .. code-block ::

    ({'skywalker': 'luke'}, {'skywalker': 'anakin'}.merge_auto() == ?

To resolve the situation, ``merge_auto()`` takes an input argument
``allow_overwrite`` that can be either of ``True``, ``False``, or
``None``.

  - ``True`` means that the last merged value will be output.

  - ``False`` will raise an error if the same key exists in multiple
    slices.  This will also cause an exception when merging two sets
    or Counters that share at least one key.

  - ``None`` Is inbetween.  It will raise an exception if there are
    duplicate keys for dictionaries, but not for sets or Counters.
    *This is the default.*

Note that these rules applies to the *bottom* of the hierarcy only.
For multi-level dictionaries keys can always overlap on the higher
levels.  For example

  .. code-block ::
     (
       {'sold_items': {'books': {'Moby Dick', 'Don Quixote'}}},
       {'sold_items': {'books': {'Don Quixote', 'Lolita'}}}
     ).merge_auto()

This is okay, because the bottom level is a set and the default is
``None``, meaning that duplicate set members is okay.  The two levels
above, ``sold_items`` and ``books``, are not part of the duplicate
check.  The merge will produce sets of sold items while maintaining
the different category hierarcy.




Forced Builds
-------------

In very rare circumstances a forced build may be wanted.  A re-build
can be forced like this

.. code-block ::

   def main(urd):
       urd.build('jobscript', force_build=True)

