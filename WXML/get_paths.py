import pandas as pd
import PTN_to_event_network




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


event_network = PTN_to_event_network.PTN_to_event_network(
    min_transfer, vehicle_paths, scedule, minimum_times)


def trim_paths(paths):
    """
    paths: set of all paths formable by the event activity matrix

    return: subset of paths that start with a departure and end with an arrival
    """

    valid_paths = set()
    
    # Removes paths that start as arrivals and end as departures
    for path in paths:
        if path[0][2] == -1 and path[-1][2] == 1:
            valid_paths.add(path)
    
    return(valid_paths)

def no_repeats(paths):
    """
    paths: set of paths (each path is a tuple/list of events),
           each event is (location, station, direction)

    return: set of trimmed paths where no (location, station, -direction) is repeated
    """
    
    trimmed_paths = set()


    for path in paths:
        seen = set()
        trimmed = []
        
        # Loops until the entire path is added or a path truncated at the loop is added
        for event in path:
            loc, station, direction = event
            reverse_event = (loc, station, -direction)
            if reverse_event in seen:
                break
            seen.add((loc, station, direction))
            trimmed.append(event)

        trimmed_paths.add(tuple(trimmed))

    return trimmed_paths


def get_paths(event_network, columns, rows):
    
    """
    event_network: Event Activity matrix populated with slack times for
    driving, waiting, and transfering

    columns: Vector of (vehicle, station) pairs

    return: Set of all possible paths within the event activity graph
            Set of waiting activities
            Set of changing activities
            Set of driving activities
    """
    #collums under this implementation are easy to calculate, though
    #not the most efficient as of now, might need to be optimized
    
    waits = set()
    changes = set()
    drives = set()

    # Repackages the EA Matrix as a pandas DataFrame
    M = pd.DataFrame(event_network, columns = columns)
    M.index = rows

    # Checks whether or not a slack exists
    for row in M.index:
        for col in M.columns:
            # Checks activity at and appends 1/-1 for arrival/departure
            if M.at[row, col] != -1: 
                if row[0] != col[0]:
                    changes.add((row + (1,), (col + (-1,))))
                elif row[1] != col[1]:
                    drives.add((col + (-1,), row + (1,)))                  
                else:
                    waits.add((row + (1,), (col + (-1,))))
    
    # Initializes set of paths
    arcs = changes.union(drives, waits)
    paths = set(tuple(arc) for arc in arcs)
    updated = True

    # Runs until no new paths are found
    while updated:
        updated = False
        new_paths = set()

        for path1 in paths:
            for path2 in paths:
                # If the end of path1 connects to the start of path2
                if path1[-1] == path2[0]:
                    # Ensure no node is repeated (except the connecting node)
                    if not any(node in path2[1:] for node in path1[:-1]):
                        # Splices path1 and path2 together
                        new_path = path1 + path2[1:]
                        if new_path not in paths:
                            new_paths.add(new_path)

        # Adds new_paths to paths
        if new_paths:
            paths.update(new_paths)
            updated = True

    # Extracts the feasible paths from the set of paths
    paths = trim_paths(paths)
    paths = no_repeats(paths)

    return(paths, waits, changes, drives)






    
