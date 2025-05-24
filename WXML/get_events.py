def get_events(columns, rows):
    """
    nodes: Vector of (Vehicle, Station) pairs

    return: Set of all events from corresponding nodes
    """

    column_events = set()
    row_events = set()
    events = []

    for columns in columns:
        column_events.add(columns + (-1,))

    for row in rows:
        row_events.add(row + (1,))

    for event in column_events:
        events.append(event)
    for event in row_events:
        events.append(event)
  
    return column_events, row_events, events
