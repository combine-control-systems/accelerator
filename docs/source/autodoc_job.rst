Autodoc Job Classes
===================

A Job is a directory on disk containing input, source code, and output
of a script execution.  Objects of the Job class are used to
represent jobs, providing helper functions to access the stored data.

There are two kinds of job classes, the Job class for finished jobs,
and the CurrentJob for jobs that are currently executing.  The latter
has additional functionality that makes sense while executing, for
example for creating new files.

|
|
|
|

.. autoclass:: accelerator.Job
   :members:
   :undoc-members:
   :exclude-members: version
   :member-order: alphabetical

.. note:: This list is not complete, see source code for details.

|
|
|
|

.. autoclass:: accelerator.job.CurrentJob
   :members:
   :undoc-members:
   :exclude-members:
   :member-order: alphabetical

