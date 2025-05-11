import numpy as np
import math
import scipy as sp


#only really use the size of this, might be able to get rid of it
#through inferring it from other data
PTN = [
        [0, 1, 0],
        [1, 0, 1],
        [0, 1, 0],
    ]
#assuming paths are fed in so that there are no loops(ok if whole path is a loop)
#each list is for each vehicle sequentially, and the tuples are edges in the path.
vehicle_paths = [
        [(0,1),(1,0)],
        [(1,2),(2,1)],
]
#assuming sceudels (and minimum times) are in-order with the paths
scedule_delay = [
    [(0,0),(5,1),(10,1),(15,2)],
    [(0,0),(7,1),(12,3),(20,2)]
]

minimum_times = [
    [4,4,4]
    [5,4,6]
]



def PTN_to_event_network(PTN,vehicle_paths,scedule_delay,minimum_times):
    """
    PTN: matrix of shape (#stations) * #(stations) whose entry (i,j) is 1 is there is a path 
    from i to j and 0 otherwise

    vehicle_paths: list of length #vehicles, whose k-th entry is the path for vehicle k.: 
    a list of 2-ples, where the 2-ple (i,j) is the path from station i to station j

    schedule_delay: list of length #vehicles, whose k-th entry is a list of 
    length 2*(#edges in path of vehicle k), and each entry is a tuple (scheduled_time, delay) 
    for vehicle k to perform the corresponding acticity.

    minimum_times: list of length #vehicles whose k-th entry is a list of length 
    2*length(#edges in path of vehicle k) - 1, and each entry is
    the minimum time for vehicle k to perform the corresponding acticity.

    Returns: event_network. A matrix M of size #events/2, where the entry M[a,b] 
    at row a and column b, where a is [train_1, station_1] and b is [train_2, station_2], 
    is the slack for the activity (train_1 arrives at station_1) —> 
    (train_2 departs at station_2) if such an activity is possible and -1 otherwise.

    
    The basic idea for part 1 is this: for each path we localize the problem to a 
    len(path) x len(path) matrix submatrix, and then starting with 
    a_{21}(with respect to the submatrix) we will move right and down for each edge
    with the ability to wrap around to the top. For example, a 4x4 submatrix that is a 
    loop will look like this (s_n processed in order of computation):
    
    -1 -1 -1 s_7 
    s_1 s_2 -1 -1
    -1 s_3 s_4 -1
    -1 -1 s_5 s_6
    """
    
    
    
    #total number of edges traversed by all vehicles
    edge_count = sum(len(path) for path in vehicle_paths)
    #matrix of size edge_count x edge_count of -1
    event_network = np.ones((edge_count,edge_count))*-1
    transfers = [[] for _ in range(len(PTN))]
    #scedule_counter is used to iterate over scedule_delay and minimum_times
    #and calculate slack at each step
    scedule_counter = 0
    minimum_counter = 0
    #counter is used to track which submatrix we are in, while subcounter is used
    #to track where we are within that submatrix
    counter = 0
    subcounter = 0
    
    for i, path in enumerate(vehicle_paths):
        for j, (start, end) in enumerate(path):
            #the first edge of the event network is a driving path, and 
            #we use the driving path to record a start and end time to 
            #each edge
            depart_time = scedule_delay[i][scedule_counter][0]
            #here, counter anchors us to one submatrix, while subcounter 
            #has modulus len(path) so that we can wrap around
            #we use the formula later time - earliest time - minimum time=slack
            event_network[counter+((subcounter+1)% len(path))][
                counter+subcounter] = scedule_delay[i][
                    scedule_counter+1][0]-scedule_delay[i][scedule_counter][0]
            -minimum_times[i][minimum_counter]
            scedule_counter += 1
            minimum_counter += 1
            arrive_time = scedule_delay[i][scedule_counter][0]
            #here, we're checking if we reached the end of the path. Note that
            #this also gaurantees our graph is acyclic
            if minimum_counter != len(scedule_delay[i]):
                event_network[counter+((subcounter+1)% len(path))][
                    counter+((subcounter+1)% len(path))] = scedule_delay[i][scedule_counter+1][0]
                -scedule_delay[i][scedule_counter][0]-minimum_times[i][minimum_counter]
                scedule_counter += 1
                minimum_counter += 1
            else:
                scedule_counter = 0
                minimum_counter = 0
            subcounter += 1
            #old code that might be useful if more problems arise here
            """
            event_network[sum(len(path) for path in vehicle_paths[:i])+j]
            [sum(len(path) for path in vehicle_paths[:i]) + ((j+1)% len(path))] = scedule_delay[scedule_counter+1]
            -scedule_delay[scedule_counter]-minimum_times[minimum_counter]
            scedule_counter += 1
            if j == len(path)-1:
                scedule_counter += 1
            minimum_counter += 1
            """
            #update the transfer matrix with the vehicle, the edge, the start/end status
            #and the time of arrival/leaving
            transfers[start].append((i, -1,(start,end),depart_time))
            transfers[end].append((i, 1,(start,end),arrive_time))
        counter += len(path)
        subcounter = 0

        
    #not sure how minimums of transfers work here, as the scedule_delay and minimum_times
    # were able to be local to each path
    for i, station in transfers:
       # might get this to work with counter/subcounter code but not enough time
       # right now
       #going through every combination of entries in each station
       for (a,b,c,d) in station:
           for (e,f,g,h) in station:
               #condition checks 
               if a != e & b == 1 & f == -1 & d <= h:
                   #taking sum(len(path) was also another way I tried to 
                   # keep track of submatrices)       
                   event_network[sum(len(path) for path in vehicle_paths[:a])
                                     + vehicle_paths[a].index(c)][
                                         sum(len(path) for path in vehicle_paths[:e])
                                     + vehicle_paths[e].index(g)] = h-g
    return event_network   
#build collums for get_paths later
