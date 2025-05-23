def get_events(columns, rows):
    """
    nodes: Vector of (Vehicle, Station) pairs

    return: Set of all events from corresponding nodes
    """

    column_events = set()
    row_events = set()

    for columns in columns:
        column_events.add(column + (-1,))

    for row in rows:
        row_evenvts.add(row + (1,))

    events = column_events.union(row_events)
    
    return column_events, row_events, events

print(get_events([(0, 0), (0, 1), (1, 3), (1, 1)]))
