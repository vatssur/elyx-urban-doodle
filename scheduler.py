import json
from datetime import datetime, timedelta, timezone, time
import zoneinfo

# Load data
with open("activities.json", "r") as f:
    activities = json.load(f)
with open("resources.json", "r") as f:
    resources = json.load(f)
with open("client_profile.json", "r") as f:
    client_profile = json.load(f)

client_tz = zoneinfo.ZoneInfo(client_profile['timezone'])

START_DATE = datetime.now(client_tz).replace(hour=0, minute=0, second=0, microsecond=0)
NUM_DAYS = 90 # 3 months

scheduled_events = []

def parse_frequency(freq_str):
    if freq_str == "Daily": return 90
    if "times a week" in freq_str: return int(freq_str.split()[0]) * 13 # ~13 weeks in 90 days
    if freq_str == "Once a month": return 3
    return 1

food_activities = [a for a in activities if a['type'] == 'FOOD_CONSUMPTION']
med_activities = [a for a in activities if a['type'] == 'MEDICATION_CONSUMPTION']
other_activities = [a for a in activities if a['type'] not in ['FOOD_CONSUMPTION', 'MEDICATION_CONSUMPTION']]

activity_counts = {act['id']: 0 for act in activities}
activity_targets = {act['id']: parse_frequency(act['frequency']) for act in activities}

def get_travel_adherence(date):
    for tp in client_profile['travel_plans']:
        start = datetime.fromisoformat(tp['start'])
        end = datetime.fromisoformat(tp['end'])
        if start <= date <= end:
            return tp['adherence_level']
    return "HOME"

def check_resource_availability(req_type, req_subtype, check_start, check_end):
    candidates = [r for r in resources if r['type'] == req_type and r['subtype'] == req_subtype]
    for cand in candidates:
        conflict = False
        for slot in cand.get('booked_slots', []):
            b_start = datetime.fromisoformat(slot['start'])
            b_end = datetime.fromisoformat(slot['end'])
            if max(check_start, b_start) < min(check_end, b_end):
                conflict = True
                break
        if not conflict:
            return cand['id']
    return None

def find_available_slot(local_date, duration_mins, time_slot_pref=None):
    if time_slot_pref == 'morning': start_hour = 10
    elif time_slot_pref == 'afternoon': start_hour = 14
    elif time_slot_pref == 'evening': start_hour = 18
    else: start_hour = 11
    
    # Create local datetime
    local_time = datetime.combine(local_date, time(start_hour, 0), tzinfo=client_tz)
    return local_time.astimezone(timezone.utc)

for day_idx in range(NUM_DAYS):
    current_day = START_DATE + timedelta(days=day_idx)
    adherence = get_travel_adherence(current_day)
    
    # 1. Schedule Meals
    daily_meals = {}
    for meal in food_activities:
        hour = 8 if meal['meal_type'] == 'Breakfast' else 13 if meal['meal_type'] == 'Lunch' else 19
        
        # TIMEZONE FIX: Construct in local time (e.g. 8:00 AM NY time) then convert to UTC
        local_start = datetime.combine(current_day.date(), time(hour, 0), tzinfo=client_tz)
        utc_start_time = local_start.astimezone(timezone.utc)
        utc_end_time = utc_start_time + timedelta(minutes=meal['duration_minutes'])
        
        if meal['prep_time_minutes'] > 0:
            prep_start = utc_start_time - timedelta(minutes=meal['prep_time_minutes'])
            scheduled_events.append({
                "title": f"Prep: {meal['name']}",
                "start": prep_start.isoformat(),
                "end": utc_start_time.isoformat(),
                "type": "PREP"
            })
            
        scheduled_events.append({
            "title": meal['name'],
            "start": utc_start_time.isoformat(),
            "end": utc_end_time.isoformat(),
            "type": "FOOD_CONSUMPTION",
            "activity_id": meal['id']
        })
        daily_meals[meal['meal_type']] = utc_start_time
        activity_counts[meal['id']] += 1
        
    # 2. Schedule Medications
    for med in med_activities:
        # We schedule meds daily
        timing_parts = med['timing'].split()
        if len(timing_parts) == 2:
            rel = timing_parts[0]
            meal_type = timing_parts[1]
            
            if meal_type in daily_meals:
                meal_time = daily_meals[meal_type] # This is UTC
                if rel == 'before':
                    start_time = meal_time - timedelta(minutes=5)
                else:
                    start_time = meal_time + timedelta(minutes=30)
                    
                end_time = start_time + timedelta(minutes=med['duration_minutes']) # 1 minute duration
                scheduled_events.append({
                    "title": med['name'],
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "type": "MEDICATION_CONSUMPTION",
                    "activity_id": med['id']
                })

    # 3. Schedule Others (distribute across weeks)
    if adherence == "BREAK":
        continue
        
    daily_fitness_count = 0
    
    for act in other_activities:
        if activity_counts[act['id']] >= activity_targets[act['id']]:
            continue
            
        if adherence == "FLEXIBLE":
            # Skip low priority entirely on flexible travel days
            if act['type'] in ["THERAPY", "CONSULTATION"]:
                continue
            # Limit fitness to max 1 per day
            if act['type'] == "FITNESS_ROUTINE":
                if daily_fitness_count >= 1:
                    continue
                daily_fitness_count += 1
            
        # VERY basic distribution: Only allow scheduling if (current_count / target) < (day_idx / 90)
        # This spreads the N activities across the 90 days.
        expected_count = (day_idx / 90.0) * activity_targets[act['id']]
        if activity_counts[act['id']] > expected_count + 1:
            continue

        utc_start_time = find_available_slot(current_day.date(), act['duration_minutes'], act.get('time_slot'))
        # Offset to prevent exact overlap
        offset_mins = (activity_counts[act['id']] % 4) * 30 
        utc_start_time += timedelta(minutes=offset_mins)
        utc_end_time = utc_start_time + timedelta(minutes=act['duration_minutes'])
        
        assigned_resources = []
        can_schedule = True
        for req in act['resource_requirements']:
            res_id = check_resource_availability(req['type'], req['subtype'], utc_start_time, utc_end_time)
            if res_id:
                assigned_resources.append(res_id)
            else:
                can_schedule = False
                break
                
        if can_schedule:
            scheduled_events.append({
                "title": act['name'],
                "start": utc_start_time.isoformat(),
                "end": utc_end_time.isoformat(),
                "type": act['type'],
                "activity_id": act['id'],
                "resources": assigned_resources
            })
            activity_counts[act['id']] += 1

with open("schedule.json", "w") as f:
    json.dump(scheduled_events, f, indent=2)

print(f"Successfully generated 90-day schedule with {len(scheduled_events)} events.")
