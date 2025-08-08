All About Files
===============

This chapter describes how to

 - use the return value to pass data
 - store and retrieve data using exax helper functions
 - register files, making exax aware of them
 - read project input data files



Writing and Reading data
------------------------



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
   job.save('filename', data)              # save in pickle format

   data = job.load('filename')             # load


   # Store and load data using JSON format
   job.json_save('filename', data)         # save in JSON format

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


Input Files
-----------


Sliced Files
------------


Temporary Files
---------------




