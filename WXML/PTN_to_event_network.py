import numpy as np


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
edge_to = dict() # Dictionary to store connections between events and minimum transfer times
    #total number of edges in all paths


def PTN_to_event_network(min_transfer,vehicle_paths,scedule,minimum_times):
    """
    Generates an event network matrix representing the slack between connected events
    in a public transport network (PTN).

    Args:
        min_transfer (list): Minimum transfer times at each station.
        vehicle_paths (list): List of paths for each vehicle, where each path is a
                              list of (start_station, end_station) tuples.
        schedule (list): List of schedules for each vehicle, where each schedule is a
                         list of arrival and departure times at each station along the path.
        minimum_times (list): List of minimum travel times for each edge in each
                              vehicle's path.

    Returns:
        numpy.ndarray: A matrix where entry [i, j] represents the slack between
                       event j (arrival at a station) and event i (departure from a station).
                       A value of -1 indicates no direct connection.
    
    OLDER DESCRIPTION BELOW
    ----
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

    Returns: event_network. A matrix M of size #sum of edges for all paths, where the entry M[a,b] 
    at row a and column b, where a is [train_2, station_2] and b is [train_1, station_1], 
    is the slack for the activity (train_1 arrives at station_1) —> 
    (train_2 departs at station_2) if such an activity is possible and -1 otherwise.
    This implementation is slightly different from the previous one. The columns and 
    rows are based off of deparing and arriving points for an edge in the event_network,
    rather than vertiecies like it was previously. This reduces the size of the matrix
    since every path that's not a loop has less edges than verticies. For an example,
    (1) from the notes on monday would give us (method just gives the matrix)
    
          (A,1)(A,2)(B,4)(B,2)
    (A,2)[[ 1.  1. -1.  2.]
    (A,3)[-1.  0. -1. -1.]
    (B,2)[-1.  0.  1.  1.]
    (B,5)[-1. -1. -1.  0.]]
    (not exactly like this, zero-based indexing changes some stuff)
    With the version that closes the loop giving us the same matrix. 
    """    
    
    edge_count = sum([len(path) for path in vehicle_paths])
    columns = []
    rows = []
    for i, path in enumerate(vehicle_paths):
        for (start, end) in path:
            columns.append((i,start))
            rows.append((i,end))
    #matrix of size edge_count x edge_count of -1
    event_network = np.ones((edge_count,edge_count))*-1
    transfers = [[] for _ in range(len(min_transfer))]
    #scedule_counter is used to iterate over scedule and minimum_times
    #and calculate slack at each step
    scedule_counter = 0
    minimum_counter = 0
    #counter is used to track which submatrix we are in, while subcounter is used
    #to track where we are within that submatrix
    counter = 0
    subcounter = 0
    slack = 0
    
    vertex_counter = 0
    for i, path in enumerate(vehicle_paths):
        for (start, end) in (path):
            #keep track of depart and arrival times for transfers
            depart_time = scedule[i][scedule_counter]
            transfers[start].append((i, -1,(start,end),depart_time,vertex_counter))
            #adds along the diagonal
            slack = scedule[i][scedule_counter+1]-scedule[i][
                scedule_counter] - minimum_times[i][minimum_counter]
            event_network[counter+subcounter][counter + subcounter] = slack
            edge_to.update({vertex_counter: [[vertex_counter+1,minimum_times[i][minimum_counter]]]})
            scedule_counter += 1
            minimum_counter += 1
            arrive_time = scedule[i][scedule_counter]
            
            
            vertex_counter += 1
            transfers[end].append((i, 1,(start,end),arrive_time,vertex_counter))
            #checks if we run into a loop
            if minimum_counter < len(minimum_times[i]):
                slack = scedule[i][scedule_counter+1] - scedule[i][
                    scedule_counter]-minimum_times[i][minimum_counter]
                event_network[counter+subcounter][counter+ subcounter + 1] = slack
                edge_to.update({vertex_counter: [[vertex_counter+1,minimum_times[i][minimum_counter]]]})
                vertex_counter += 1
                scedule_counter += 1
                minimum_counter += 1
            else:
                scedule_counter = 0
                minimum_counter = 0
            subcounter += 1

            #update transfers with vehicle, start and exit, arrival and departure times
            # and the edge itself
            
        vertex_counter += 1    
        counter += len(path)
        subcounter = 0


    
    for i, station in enumerate(transfers):
       for (a,b,c,d,v1) in station:
           for (e,f,g,h,v2) in station:
               #feasibility check here, might be different with delays
               if a != e and b == 1 and f == -1 and d + min_transfer[i] <= h:     
                   slack = h-d-min_transfer[i]
                   row = sum(len(path) for path in vehicle_paths[:e]
                             )+ vehicle_paths[e].index(g)-1
                   column = sum(len(path) for path in vehicle_paths[:a]
                                )+ vehicle_paths[a].index(c)+1
                   if column >= sum(len(path) for path in vehicle_paths[:a])+ len(vehicle_paths[a]):
                       event_network = np.insert(event_network, column,-1, axis = 1)
                       np.insert(columns, (e,i))
                   event_network[row][column] = slack
                   current_outgoing = edge_to.setdefault(v1,[])
                   current_outgoing.append([v2,min_transfer[i]])
                   edge_to.update({v1: current_outgoing})
    return event_network,columns,rows

  
