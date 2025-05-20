def get_events(columns):
    """
    columns: Vector of (Vehicle, Station) pairs

    return: Set of all events from the event activity network 
    """

    events = set()

    for column in columns:
        events.add(column + (-1,))
        events.add(column + (1,))
    
    return events

print(get_events([(0, 0), (0, 1), (1, 3), (1, 1)]))