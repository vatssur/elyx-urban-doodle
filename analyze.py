import json
from collections import defaultdict
from datetime import datetime

with open('activities.json') as f:
    activities = json.load(f)

with open('schedule.json') as f:
    schedule = json.load(f)

print(f"Total Activities: {len(activities)}")
meals = [a for a in activities if a['type'] == 'FOOD_CONSUMPTION']
print(f"Total Meals generated: {len(meals)}")
for m in meals:
    print(f" - {m['name']} (ID: {m['id']})")

# Analyze Day 1 schedule
print("\n--- Day 1 Analysis ---")
day1_events = []
for event in schedule:
    dt = datetime.fromisoformat(event['start'])
    # Look at the first generated day (e.g., today's date)
    # Let's group by date string
    date_str = dt.date().isoformat()
    day1_events.append((date_str, event))

# Group by date
events_by_date = defaultdict(list)
for date_str, evt in day1_events:
    events_by_date[date_str].append(evt)

first_date = sorted(events_by_date.keys())[0]
first_day_events = sorted(events_by_date[first_date], key=lambda x: x['start'])

dinner_count = 0
for evt in first_day_events:
    print(f"[{evt['start']}] {evt['title']} ({evt['type']})")
    if 'Dinner' in evt['title']:
        dinner_count += 1

print(f"\nDinners on Day 1: {dinner_count}")
