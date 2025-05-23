import numpy as np
import pandas as pd
from scipy.optimize import milp, LinearConstraint, Bounds
from get_paths import get_paths
from get_events import get_events
from PTN_to_event_network import PTN_to_event_network
def tdm_b(event_network, columns, rows, e_del, weights):
    """
    event_network: Event Activity matrix populated with slack times for
    driving, waiting, and transfering

    columns: Vector of (vehicle, station) pairs

    e_del: list of source delays indexed by node

    weights: list of weights indexed by path

    returns: list of all maintained paths determined by linear optimization
    """

    M = 15
    T= 15

    # Extracts basic event-activity data
    paths, waits, changes, drives = get_paths(event_network, columns, rows) 

    column_events, row_events, events = get_events(columns, rows)

    events = column_events.union(row_events)

    # Sets the number of columns in A
    num_variables = len(events) + len(paths) + len(paths)
    q_start = len(events) + len(paths)
    y_start = len(paths)

    # Initializes A and b matrices
    A = np.empty((0, num_variables))
    b = np.empty((0,1))

    # Rewrites events as a dictionary for future indexing 
    events_dict = {event: idx for idx, event  in enumerate(events)}

    # Adds z_p in {0,1} constraint
    for i in range(len(paths)):
        new_row = np.zeros(num_variables)
        new_row[i] = 1

        A = np.vstack([A, new_row])
        b = np.vstack([b, 1])


        new_row[i] = -1
        A = np.vstack([A, new_row])
        b = np.vstack([b, 0])
    
    # Adds q_p >= 0 constraint
    for i in range(len(paths)):
        new_row = np.zeros(num_variables)
        new_row[i + q_start] = -1

        A= np.vstack([A, new_row])
        b = np.vstack([b, 0])
    
    # Adds y_i - y_j <= s_a constraint
    for activity in (waits | drives):
        i = events_dict[activity[0]]
        j = events_dict[activity[1]]

        new_row = np.zeros(num_variables)
        new_row[i + y_start] = 1
        new_row[j + y_start] = -1

        A = np.vstack([A, new_row])
        # Extract s_a from EA network
        i_sliced = activity[0][:-1]
        j_sliced = activity[1][:-1]

        i_index = columns.index(i_sliced)
        j_index = rows.index(j_sliced)

        b = np.vstack([b, event_network[i_index][j_index]])

    
    # Adds y_i >= d_i constraint
    for i in range(len(e_del)):
        if e_del[i] != 0:
            new_row = np.zeros(num_variables)
            new_row[i + y_start] = -1

            A = np.vstack([A, new_row])
            b = np.vstack([b, -e_del[i]])
        
    paths_dict = {paths: idx for idx, paths  in enumerate(paths)}

    # Adds -Mz_p + y_i(p) - q_p <= 0 constraint
    for path in paths:
        i = events_dict[path[-1]]
        p = paths_dict[path]
        
        new_row = np.zeros(num_variables)
        new_row[i + y_start] = 1
        new_row[p] = -M 
        new_row[p + q_start] = -1

        A = np.vstack([A, new_row])
        b = np.vstack([b, 0])

        
    # Adds -Mz_p + y_i - y_j <= s_a constraint
    for change in changes:
        i = change[0]
        j = change[1]


        for path in paths:
            for k in range(len(path) - 1):
                if path[k] == i and path[k+1] == j:
                    new_row = np.zeros(num_variables)

                    p = paths_dict[path]
                    i_index = events_dict[i]
                    j_index = events_dict[j]

                    new_row[p] = -M
                    new_row[i_index + y_start] = 1
                    new_row[j_index + y_start] = -1 

                    A = np.vstack([A, new_row])

                    i_sliced = i[:-1]
                    j_sliced = j[:-1]

                    i_index = columns.index(i_sliced)
                    j_index = rows.index(j_sliced)
                    
                    b = np.vstack([b, event_network[i_index][j_index]])
        
    # Sets y_p variables as continuous with all else being integer
    integrality = np.ones(num_variables, dtype = int)
    integrality[y_start:q_start] = 0

    c = np.zeros(num_variables)
    for path in paths:
        p = paths_dict[path]
        
        c[p + q_start] = weights[p]
        c[p] = T * weights[p]
    
    lower_bounds = np.full(num_variables, -1e6)
    upper_bounds = np.full(num_variables, 1e6)

    linear_constraint = LinearConstraint(A, lb = -np.inf, ub = b.flatten())
    bounds = Bounds(lower_bounds, upper_bounds)

    result = milp(c = c, constraints = [linear_constraint], bounds = bounds, integrality = integrality)

    paths = list(paths)
    maintained_paths = list()

    return(result.x[y_start:q_start])

    # Gets connection data from the solution vector x
    # connections = result.x[:y_start]

    """
    for connection in range(len(connections)):
        if connections[connection] == 0:
            maintained_paths.append(paths[connection])

    return(maintained_paths)
    """
    

min_transfer = [0,0,0,0,0]
#assuming paths are fed in so that there are no loops(ok if whole path is a loop)
#each list is for each vehicle sequentially, and the tuples are edges in the path.
vehicle_paths = [
        [(0,1),(1,0)],
        [(2,1),(1,3)],
]
#assuming sceudels (and minimum times) are in-order with the paths
scedule = [
    [0,5,7,10],
    [0,4,6,10]
]

minimum_times = [
    [4,1,3],
    [3,1,4]
]
edge_to = dict()


event_network = PTN_to_event_network(
    min_transfer, vehicle_paths, scedule, minimum_times)
e_del = [0,0,0,2,5,3,0,2]
weights = [0,1,2,3,4,5]
for path in tdm_b(event_network[0],event_network[1],event_network[2], e_del, weights):
    print(path)