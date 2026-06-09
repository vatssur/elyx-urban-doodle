from datetime import datetime, timezone, timedelta
from scheduler import check_overlap

def test_check_overlap_basic():
    start = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1)
    
    events = [{
        "title": "Gym",
        "start": "2026-01-01T11:30:00+00:00",
        "end": "2026-01-01T12:30:00+00:00",
        "transit_minutes": 0
    }]
    
    assert check_overlap(start, end, act_transit=0, min_gap=0, scheduled_events=events) == False
    assert check_overlap(start, end + timedelta(hours=1), act_transit=0, min_gap=0, scheduled_events=events) == True

def test_check_overlap_transit_buffers():
    start = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1) # 10:00 - 11:00
    
    # Event starts at 11:30 with 15m transit -> Blocks 11:15 to 12:45
    events = [{
        "title": "Therapy",
        "start": "2026-01-01T11:30:00+00:00",
        "end": "2026-01-01T12:30:00+00:00",
        "transit_minutes": 15
    }]
    
    # Candidate ends at 11:00. Adding 15m transit -> ends at 11:15.
    # 11:15 does not overlap with 11:15.
    assert check_overlap(start, end, act_transit=15, min_gap=0, scheduled_events=events) == False
    
    # Candidate ends at 11:05. Adding 15m transit -> ends at 11:20.
    # 11:20 > 11:15 -> Overlap!
    end2 = start + timedelta(hours=1, minutes=5)
    assert check_overlap(start, end2, act_transit=15, min_gap=0, scheduled_events=events) == True

def test_check_overlap_min_gap():
    start = datetime(2026, 1, 1, 10, 0, tzinfo=timezone.utc)
    end = start + timedelta(hours=1) # 10:00 - 11:00
    
    events = [{
        "title": "Gym",
        "start": "2026-01-01T11:00:00+00:00",
        "end": "2026-01-01T12:00:00+00:00",
        "transit_minutes": 0
    }]
    
    # Back-to-back is fine if min_gap is 0
    assert check_overlap(start, end, act_transit=0, min_gap=0, scheduled_events=events) == False
    
    # With min_gap = 15, the candidate extends to 11:15, overlapping with 11:00
    assert check_overlap(start, end, act_transit=0, min_gap=15, scheduled_events=events) == True
