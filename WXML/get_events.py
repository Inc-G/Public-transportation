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
