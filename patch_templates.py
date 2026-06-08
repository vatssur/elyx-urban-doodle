import json

with open('templates.json', 'r') as f:
    templates = json.load(f)

for t in templates:
    loc = t.get('location', '')
    if loc and 'Home' in loc:
        t['transit_time_minutes'] = 0
    elif t.get('remote_capable'):
        t['transit_time_minutes'] = 0
    else:
        t['transit_time_minutes'] = 15 # default 15 min

with open('templates.json', 'w') as f:
    json.dump(templates, f, indent=2)

print(f"Patched {len(templates)} templates with transit times.")
