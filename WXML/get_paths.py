import pandas as pd

def get_paths(event_network, columns):
    
    """
    event_network: Event Activity matrix populated with slack times for
    driving, waiting, and transfering

    columns: Vector of (vehicle, station) pairs

    return: Set of all possible paths within the event activity graph   
    """

    arcs = set()

    # Repackages the EA Matrix as a pandas DataFrame
    M = pd.DataFrame(event_network, columns = columns)
    M.index = columns

    # Checks whether or not a slack exists
    for row in M.index:
        for col in M.columns:
            # Checks activity at and appends 1/-1 for arrival/departure
            if M.at[row, col] != -1: 
                if row[0] != col[0]:
                    arcs.add((row + (1,), (col + (-1,))))
                elif row[1] != col[1]:
                    arcs.add((col + (-1,), row + (1,)))                 
                else:
                    arcs.add((row + (1,), (col + (-1,))))
    
    # Initializes set of paths
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
    
    valid_paths = set()
    
    # Removes paths that start as arrivals and end as departures
    for path in paths:
        if path[0][2] != 1 and path[-1][2] != -1:
            valid_paths.add(path)

    return(paths)