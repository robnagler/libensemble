Known Issues
============

The following selection describes known bugs, errors, or other difficulties that
may occur when using libEnsemble.

* When using the executor: OpenMPI does not work with direct MPI task
  submissions in mpi4py comms mode, since OpenMPI does not support nested MPI
  executions. Use either local mode or the Balsam executor instead.
* Local comms mode (multiprocessing) may fail if MPI is initialized before
  forking processors. This is thought to be responsible for issues combining
  multiprocessing with PETSc on some platforms.
* Remote detection of logical cores via LSB_HOSTS (e.g., Summit) returns the
  number of physical cores as SMT info not available.
* TCP mode does not support
  (1) more than one libEnsemble call in a given script or
  (2) the auto-resources option to the executor.
* libEnsemble may hang on systems with matching probes not enabled on the
  native fabric, like on Intel's Truescale (TMI) fabric for instance. See the
  :doc:`FAQ<FAQ>` for more information.
* We currently recommended running in Central mode on Bridges as distributed
  runs are experiencing hangs.
