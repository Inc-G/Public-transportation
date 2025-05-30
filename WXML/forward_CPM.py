import numpy as np
from PTN_to_event_network import PTN_to_event_network
from tdm_b import tdm_b
min_transfer = [0,1,0,0]
#assuming paths are fed in so that there are no loops(ok if whole path is a loop)
#each list is for each vehicle sequentially, and the tuples are edges in the path.
vehicle_paths = [
        [(0,1),(1,0)],
        [(2,1),(1,2)],
        [(3,1),(1,3)]
]
#assuming sceudels (and minimum times) are in-order with the paths
scedule = [
    [0,5,10,15],
    [0,7,8,10],
    [0,4,6,10]
]

minimum_times = [
    [4,1,3],
    [3,1,2],
    [3,1,4]
]

M =PTN_to_event_network(min_transfer, vehicle_paths, scedule, minimum_times)
e_del = [0,0,0,2,5,3,0,2,0,2,2,0]
weights = [0,1,2,3,4,5,0,1,2,3,4]
paths = tdm_b(M[0],M[1],M[2], e_del, weights)


#can't test until I have critical connections
# not having critical connections also affects how I update edge_to, 
# might not neet event_network for these methods in the future
def keep_critcal_connections(paths, edge_to):
    connetions = edge_to.get(-1)
    for change in connetions:
        is_critical = False
        for path in paths:
            for i in range(len(path)-1):
                if (path[i][0] == change[0][0] and path[i+1][0] == change[1][0]):
                    is_critical = True
        if (not is_critical):
            outgoing = edge_to.get(change[0][1])
            outgoing.remove(next(edge for edge in outgoing if edge[0] == change[1][1]))
            edge_to.update({change[0]:outgoing})
    return edge_to

def get_kth_element(k):
    for i in range(len(scedule)):
        n = len(scedule[i])
        if k < n:
            return i,k
        k -= n
    
#we'd assume we're working with a critical connection matrix, otherwise we make one and pass it in
# assuming were working with a nice delays and scedule set based on the vertices. can refactor how 
# data is sent in, just need structure for traversal with event_network
def forward_CPM(scedule, e_del, edge_to,paths):
    #might need to go back to old code and have an ordered numbering of the vertices,
    # or some kind of more direct connection
    #also if we have knowelde that we're going to use this info later, it just makes more sense
    #to pick up the info in event_network
    edge_to = keep_critcal_connections(paths, edge_to)
    distance_to = [[] for i in range(len(scedule))]
    
    counter = 0
    for i in range(len(scedule)):
        for j in range(len(scedule[i])):
            distance_to[i].append(scedule[i][j]+e_del[counter])
            counter += 1
    counter = 0
    
    perimeter = []
    for i in range(len(scedule)):
        
        visited = set()
        perimeter.append(counter)
        while(not perimeter == []):
            current = perimeter.pop()
            if (not current in visited):
                for value in edge_to.setdefault(current,[]):
                    perimeter.append(value[0])
                    indexing_current = get_kth_element(current)
                    indexing_value = get_kth_element(value[0])
                    distance_to_current = distance_to[indexing_current[0]][indexing_current[1]]
                    distance_to_value = distance_to[indexing_value[0]][indexing_value[1]]  
                    if ( distance_to_current + value[1] > distance_to_value):
                        distance_to[indexing_value[0]][indexing_value[1]
                        ]= distance_to_current + value[1]
                visited.add(current)
        counter += len(scedule[i])
    return distance_to
print(forward_CPM(scedule, e_del, M[3], paths))

