def get_events(nodes):
    """
    nodes: Vector of (Vehicle, Station) pairs

    return: Set of all events from corresponding nodes
    """

    events = set()

    for node in nodes:
        events.add(node + (-1,))
        events.add(node + (1,))
    
    return events

print(get_events([(0, 0), (0, 1), (1, 3), (1, 1)]))
