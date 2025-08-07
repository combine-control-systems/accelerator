Job Fundamentals
================


The concepts relating to exax jobs are fundamental, and this section
provides a shorter summary about the basic concepts.

1. Data and metadata relating to a job is stored in a job directory.

  The set of files stored in the job directory at dispatch is complete
  in the sense that all information required to run the job is
  included.  So the exax job dispatcher actually just creates
  processes and points them to the job directory to start execution.
  New processes have to go and figure out their purpose by themselves
  by looking in this directory.

  A running job has the process’ current working directory (CWD)
  pointing into the job directory, so any files created by the job
  (including return values) will by default be stored in the job’s
  directory.

  When a job completes, the meta data files are updated with profiling
  information, such as execution time spent in single and parallel
  processing modes.  Information about created datasets, files, and
  subjobs is also added.

  In addition, all code that is directly related to the job is also
  stored in the job directory in a compressed archive. This archive is
  typically limited to the script’s source, but any files that may
  have been added manually (using ``depend_extra``) are stored in the
  archive too.  This way, source code and results are always connected
  and conveniently stored in the same directory for future reference.

2. Job objects are wrappers around job directories, providing helper
   functions.

  Exax uses a class based programming model.  Access to data,
  functions, and parameters is done using a few *objects* that are
  populated by exax.

3. Jobs are referenced by simple strings, like "dev-42"

  Human readable references is a great benefit.

4. Both job scripts and build scripts create jobs.

5. Unique jobs are only executed once.

  Jobs are re-cycled, unless their pre-conditions have changed.  Among
  the meta information stored in the job directory is a hash digest of
  the script’s source code (including `depend_extra``s).  This hash,
  together with the input parameters, is used to figure out if a
  result could be re-used instead of re-computed.  This saves time and
  energy, and greatly improves transparency and reproducibility.

6. Jobs created from build scripts are always considered to be unique.

  So they will always be re-built.

5. Jobs may link to each other using job references.

  Meaning that jobs may share results and parameters with each other.

6. Jobs are stored in workdirs.

  So it is clear *exactly* where on the disk that all work is being
  saved.  This simplifies computer and storage administration.

7. There may be any number of workdirs.

  This adds a layer of “physical separation”. All jobs relating to
  importing a set of data may be stored in one workdir, perhaps named
  "import", and development work may be stored in a workdir named
  "dev", etc.

7. Job ids are created by appending a counter to the workdir name.

8. Jobs may dispatch other jobs.

  A job can dispatch any number of new jobs.  These jobs are then
  called *subjobs*.  A maximum allowed recursion depth is defined to
  avoid infinite recursion.
