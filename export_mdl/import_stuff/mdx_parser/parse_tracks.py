def parse_tracks(r):
    """Event object key times (KEVT). Returns (times in ms, global sequence id or -1)."""
    tracks_count = r.getf('<I')[0]
    global_sequence_id = r.getf('<i')[0]
    times = []

    for _ in range(tracks_count):
        times.append(r.getf('<I')[0])
    return times, global_sequence_id
