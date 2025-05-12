import numpy as np
import pandas as pd

def tdm_b(events, paths, drives, changes, waits):
    """
    events: set of all events in the EA network

    paths: set of all paths in the EA network

    drives: set of all driving activities in the EA network
    
    changes: set of all waiting activities in the EA network

    waits: set of all waiting activites in the EA network

    returns:
        A: matrix for LP

        b: upper bounds for each constraint

        integerality: vector that denotes whether variables should be integers or continuous
    """
    M = 10

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
        b = np.vstack([b, "change"]) # Need to extract s_a from EA network
    
    # Adds -Mz_p + y_i(p) - q_p <= 0 constraint
    counter = 0

    for path in paths:
        i = events_dict[path[0]]

        new_row = np.zeros(num_variables)
        new_row[i + y_start] = 1
        new_row[counter] = -M 
        new_row[counter + q_start] = -1

        A = np.vstack([A, new_row])
        b = np.vstack([b, 0])

        counter += 1
    




