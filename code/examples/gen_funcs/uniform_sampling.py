from __future__ import division
from __future__ import absolute_import

import numpy as np

def uniform_random_sample_with_different_nodes_and_ranks(g_in,gen_out,params,info):
    ub = params['ub']
    lb = params['lb']
    n = len(lb)

    if len(g_in) == 0: 
        b = params['initial_batch_size']

        O = np.zeros(b, dtype=gen_out)
        for i in range(0,b):
            x = np.random.uniform(lb,ub,(1,n))
            O['x'][i] = x
            O['num_nodes'][i] = 1
            O['ranks_per_node'][i] = 16
            O['priority'] = 1
        
    else:
        O = np.zeros(1, dtype=gen_out)
        O['x'] = len(g_in)*np.ones(n)
        O['num_nodes'] = np.random.choice([1,2,3,4]) 
        O['ranks_per_node'] = np.random.randint(1,17)
        O['priority'] = 10*O['num_nodes']

    return O


def uniform_random_sample_with_priorities(g_in,gen_out,params,info):
    ub = params['ub']
    lb = params['lb']

    n = len(lb)
    b = params['gen_batch_size']

    O = np.zeros(b, dtype=gen_out)
    for i in range(0,b):
        x = np.random.uniform(lb,ub,(1,n))

        O['x'][i] = x
        O['priority'][i] = np.random.uniform(0,1)

    return O

def uniform_random_sample(g_in,gen_out,params,info):
    ub = params['ub']
    lb = params['lb']

    n = len(lb)
    b = params['gen_batch_size']

    O = np.zeros(b, dtype=gen_out)
    for i in range(0,b):
        x = np.random.uniform(lb,ub,(1,n))

        O['x'][i] = x

    return O