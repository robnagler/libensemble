# """
# Runs libEnsemble to test communications
# Scale up array_size and number of workers as required
#
# Execute via the following command:
#    mpiexec -np 4 python3 {FILENAME}.py
# The number of concurrent evaluations of the objective function will be N-1.
# """

# Do not change these lines - they are parsed by run-tests.sh
# TESTSUITE_COMMS: mpi local tcp
# TESTSUITE_NPROCS: 2 4

import sys
import numpy as np

# Import libEnsemble items for this test
from libensemble.libE import libE
from libensemble.sim_funcs.comms_testing import float_x1000 as sim_f
from libensemble.gen_funcs.uniform_sampling import uniform_random_sample as gen_f
from libensemble.tests.regression_tests.common import parse_args, save_libE_output, per_worker_stream
from libensemble.mpi_controller import MPIJobController  # Only used to get workerID in float_x1000
jobctrl = MPIJobController(auto_resources=False)

nworkers, is_master, libE_specs, _ = parse_args()

array_size = int(1e6)  # Size of large array in sim_specs
rounds = 2  # Number of work units for each worker
sim_max = nworkers * rounds

sim_specs = {'sim_f': sim_f,
             'in': ['x'],
             'out': [('arr_vals', float, array_size), ('scal_val', float)]}

gen_specs = {'gen_f': gen_f,
             'in': ['sim_id'],
             'out': [('x', float, (2,))],
             'lb': np.array([-3, -2]),
             'ub': np.array([3, 2]),
             'gen_batch_size': sim_max,
             'batch_mode': True,
             'num_active_gens': 1,
             'save_every_k': 300}

persis_info = per_worker_stream({}, nworkers + 1)

exit_criteria = {'sim_max': sim_max, 'elapsed_wallclock_time': 300}

# Perform the run
H, persis_info, flag = libE(sim_specs, gen_specs, exit_criteria, persis_info,
                            libE_specs=libE_specs)

if is_master:
    assert flag == 0
    for i in range(sim_max):
        x1 = H['x'][i][0]*1000.0
        x2 = H['x'][i][1]
        assert np.all(H['arr_vals'][i] == x1), "Array values do not all match"
        assert H['scal_val'][i] == x2 + x2/1e7, "Scalar values do not all match"

    save_libE_output(H, persis_info, __file__, nworkers)
