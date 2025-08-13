All About Files
===============

This chapter describes how to

 - use the return value to pass data
 - store and retrieve data using exax helper functions
 - register files, making exax aware of them
 - read project input data files



Writing and Reading data
------------------------

From a programmer's point of view, data is passed from job to job
using job objects.  The job object provides functions for both reading
and writing files.



Where should a file be stored?
..............................

The current work directory (CWD) is always pointing to the current job
directory, so creating files with relative paths will ensure that they
end up where they should - in the runnin job's directory.

Never store files elsewhere, that will break the association between
files and the source code (and input parameter set) that created them.
One of the benefits of the helper functions described in this chapter
is that they ensure that files are stored in the correct places.



Passing data using return value
...............................

The simplest way to store data created in a job is to use the return
function:

.. code-block::

  def synthesis():
      ...
      data = ...
      return data

This will store the data in Python's pickle format.  To access the
data later, use the ``load()`` function with no argument:

.. code-block::

  def main(urd):
      job = urd.build('example')
      data = job.load()

or

.. code-block::

  jobs = ('example',)

  def synthesis():
      data = jobs.example.load()



Passing data using named files
..............................

Files can be created by any means, for example by calling a shell
command or running ``ffmpeg`` in a subprocess, or just by calling
Python's ``open()`` function.

Exax provides three functions for creating files using different data
serialisations, see this example

.. code-block::

   # Store and load data using Python's pickle format
   job.save(data, 'filename')              # save in pickle format

   data = job.load('filename')             # load


   # Store and load data using JSON format
   job.json_save(data, 'filename')         # save in JSON format

   data = job.json_load('filename')        # load


   # Store and load data in any format
   with job.open('filename', 'wt') as fh:  # save in custom format
       fh.write(data)                      # (text-based in this example)

   with job.open('filename', 'rt') as fh:  # load
       data = fh.read()                    # 


All three save functions will *register* the file as well.  More about
this in the next section.

Exax uses references to jobs to pass data and parameters around in a
project, so while files can be created by any means, all files are
closely connected to the job that created them, and therefore it makes
sense to use only the three job-object based load functions above for
data reading.



Using ``JobWithFile()``
.......................

``JobWithFile`` is an input parameter type that can is used to
pinpoint a specific file in a specific job.

The basic functionality is as follow.  In a build script, a specific
file in a job is input to a ``build()`` call like this





Registering files
-----------------

For convenvience, knowledge about created files should be added to the
file creating job's meta information.  In exax notation, this is
called to *register* a file.



Manual registration
...................

All three calls in the example in the previous section will register
the created files automatically.  If files are created by other means,
they can be registered manually, either one by one, or using a glob
pattern, like this

.. code-block::

   job.register_file('filename')

   files = job.register_files('*.jpg')

``register_files()`` will by default register everything.  It will
return the names of the files that are registered.



Automatic registration
......................

There is also an automatic file registration running when the job
finishes.  It automatically registers all files created by the job,
while following these rules

  1. Files in subdirectories are never registered automatically.

  2. Automatic registration is *disabled* if any file has been
     manually registered (using for example ``job.save()`` or
     ``job.register_file()``).

The rationale is like this

  - If there is no manual registration, exax will go and find and
    created files and register them automatically.

  - If there is manual registration, it is assumed that it is an
    active decision, and *only* manually registered files are
    considered.

  - If there are sub-directories, they may contain large numbers of
    files, for example images, and auto registration might not be a
    good idea.  And they can easily be registered manually using
    ``job.register_files('dir/*.png)``.



Finding registered files
........................

Information about registered files is can be found using these
functions:

.. code-block::

   # return a list of all registered files in a job
   files = job.files()

   # glob filter
   files = job.files('dir/*.png')

   # get absolute path to file
   fn = job.filename('name_of_file')

While absolute paths should generally be avoided, ``job.filename()``
is useful when files are to be used outside of exax.  For example to
provide an absolute path to a file containing some useful
visualisation.




Sliced Files
------------

Exax supports parallel execution using the ``analysis()`` call in job
scripts.  A common case is to have all parallel slices performing
similar operations but on different sets of data.  This is where the
*sliced files* come in handy.  It might sound complicated, but really
it is not.  The ``save()`` call takes an argument ``sliceno=``, and
doing

.. code-block::

  job.save(data, 'filename', sliceno=3)

will store ``data in a file named ``filename.3``.  This file is read
back in a similar fashion

.. code-block::

  data = job.load('filename', sliceno=3)

Now, extending this example to the ``analysis()`` function, where we
have an input variable ``sliceno`` containing the number of the
current parallel slice

.. code-block::

   jobs = ('datajob')

   def analysis(sliceno, job):
       data_in = jobs.datajob.load('data_in', sliceno=sliceno)
       data_out = function(data_in)
       job.write('data_out', sliceno=sliceno)

In, say, slice number 3, where ``sliceno`` is equal to 3, the
``load()`` line will read the file ``data_in.3`` from the
``jobs.datajob`` job, process it, and write the result to a file
``data_out.3``.  All other slices will do similar things with
different ``sliceno``.

The benefit here is that a single filename is used to represent a
whole set of files, which simplifies programming complexity and
reduces risk of error.  In addition, it is still plain files on disk,
so there is no complicated "parallel storage layer" involved.



Temporary Files
---------------

Making a file temporary will case it to be deleted when the script
creating it finishes.  This could free up space in cases where a lot
of temporary data is generated that has no use outside of the job
generating (and consuming) it.

To make a file temporary, use the ``temp=`` argument to either
``job.save()``, ``job.json_save()``, or ``job.open()``, like in this
example

.. code-block::

  def prepare(job):
      data = ...
      job.save('data', temp=True)

Temporary files are affected by file registration.
If a temporary file is registered, it ceases to be temporary.
(Because registration implies that the file is of particular interest
outside the job.)

Starting the exax server with the ``--debug``-flag will override the
``temp=`` parameter and no files will be considered temporary.



Input Files
-----------

Ideally, absolute paths to input data files should not be stored in a
project's source code.  The source code would then need modification
if the project is moved to a computer with a different file hierarchy,
for example.

Exax solution is to use a configuration parameter called ``input
directory`` defined the ``accelerator.conf`` file.

Let's say data is stored in the ``/data`` directory

.. code-block:: text

  /data/
       |-> file1
       |-> dir/
              |-> file2

In the ``accelerator.conf``, this is reflected in the line

.. code-block:: text

  input directory: /data

The input filenames and data can then be accessed like this

.. code-block::

  path = job.input_directory()              # absolute path to input directory

  fn = job.input_filename('file1')          # abs path to file1
  fn = job.input_filename('dir', 'file2')   #             file2, or just
  fn = job.input_filename('dir/file2')


  with job.input('file1', 'rb') as fh:      # read contents of file1
      data = fh.read()

``job.input`` is basically a wrapper around Python's ``open()``
function that in addition to finding the correct file asserts that the
file is opened in read mode only.


