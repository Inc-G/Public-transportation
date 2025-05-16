import numpy as np
import PTN_to_event_network
min_transfer = [2,1,3,3,3]

vehicle_paths = [
        [(0,1),(1,0)],
        [(2,1),(1,2)],
]
scedule = [
    [0,5,7,10],
    [0,4,6,10]
]

minimum_times = [
    [4,1,3],
    [3,1,4]
]
M =PTN_to_event_network.PTN_to_event_network(min_transfer, vehicle_paths, scedule, minimum_times)


#can't test until I have critical connections
critical_connections = []
def keep_critcal_connections(event_network,critical_connections,vehicle_paths):
    blocks = []
    current_start = 0
    slack_list =[]
    for (a,b) in critical_connections:
        slack_list.append(event_network[a][b])
    for path in vehicle_paths:
        blocks.append((current_start,current_start+len(path)))  
    for i in range(len(event_network)):
        for j in range(len(event_network)):
            in_block = False
            for (s, e) in blocks:
                if s <= i < e and s <= j < e:
                    in_block = True
                    break  
            if in_block == False:
                event_network[i][j] = -1
    for (a,b) in critical_connections:
        event_network[a][b] = slack_list.pop(0)
    return event_network

    
#we'd assume we're working with a critical connection matrix, otherwise we make one and pass it in
# assuming were working with a nice delays and scedule set based on the vertices. can refactor how 
# data is sent in, just need structure for traversal with event_network
def forward_CPM(event_network, scedule, delays):
    distance_to = []
    counter = 0
    for i in range(len(scedule)):
        for j in range(len(scedule[i])):
            distance_to.append(scedule[i][j]+delays[counter])
            counter += 1
    counter = 0
    visited = set()
    perimeter = []
    for i in range(len(scedule)):
        perimeter.append(counter)
        while(not perimeter == []):
            current = perimeter.pop()
            if (not current in visited):
                break
        counter += len(scedule[i])
    return 0