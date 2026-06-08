import json
from datetime import datetime, timedelta, timezone

# Load data
with open("activities.json", "r") as f:
    activities = json.load(f)

with open("resources.json", "r") as f:
    resources = json.load(f)

with open("client_profile.json", "r") as f:
    client_profile = json.load(f)

# Initialize schedule
START_DATE = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
NUM_DAYS = 7 # Just schedule 1 week for the POC

scheduled_events = []

def parse_frequency(freq_str):
    if freq_str == "Daily":
        return 7
    if "times a week" in freq_str:
        return int(freq_str.split()[0])
    if freq_str == "Once a month":
        return 1
    return 1

# Group by type
food_activities = [a for a in activities if a['type'] == 'FOOD_CONSUMPTION']
med_activities = [a for a in activities if a['type'] == 'MEDICATION_CONSUMPTION']
other_activities = [a for a in activities if a['type'] not in ['FOOD_CONSUMPTION', 'MEDICATION_CONSUMPTION']]

# We need to track activity occurrences for the week
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
    # Find matching resources
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

def find_available_slot(day_date, duration_mins, time_slot_pref=None):
    if time_slot_pref == 'morning':
        start_hour = 8
    elif time_slot_pref == 'afternoon':
        start_hour = 13
    elif time_slot_pref == 'evening':
        start_hour = 17
    else:
        start_hour = 10 # default
        
    start_time = day_date + timedelta(hours=start_hour)
    return start_time

for day_idx in range(NUM_DAYS):
    current_day = START_DATE + timedelta(days=day_idx)
    adherence = get_travel_adherence(current_day)
    
    # 1. Schedule Meals
    daily_meals = {}
    for meal in food_activities:
        if activity_counts[meal['id']] >= activity_targets[meal['id']]:
            continue
            
        hour = 8 if meal['meal_type'] == 'Breakfast' else 13 if meal['meal_type'] == 'Lunch' else 19 if meal['meal_type'] == 'Dinner' else 16
        start_time = current_day + timedelta(hours=hour)
        end_time = start_time + timedelta(minutes=meal['duration_minutes'])
        
        # Schedule Prep
        if meal['prep_time_minutes'] > 0:
            prep_start = start_time - timedelta(minutes=meal['prep_time_minutes'])
            scheduled_events.append({
                "title": f"Prep: {meal['name']}",
                "start": prep_start.isoformat(),
                "end": start_time.isoformat(),
                "type": "PREP"
            })
            
        scheduled_events.append({
            "title": meal['name'],
            "start": start_time.isoformat(),
            "end": end_time.isoformat(),
            "type": "FOOD_CONSUMPTION",
            "activity_id": meal['id']
        })
        daily_meals[meal['meal_type']] = start_time
        # Since meals are "Daily", we just increment but don't stop scheduling if we're generating day-by-day
        # Actually, "Daily" means target is 7. We increment it here.
        activity_counts[meal['id']] += 1
        
    # 2. Schedule Medications
    for med in med_activities:
        if activity_counts[med['id']] >= activity_targets[med['id']]:
            continue
            
        timing_parts = med['timing'].split()
        if len(timing_parts) == 2:
            rel = timing_parts[0]
            meal_type = timing_parts[1]
            
            if meal_type in daily_meals:
                meal_time = daily_meals[meal_type]
                if rel == 'before':
                    start_time = meal_time - timedelta(minutes=5)
                else:
                    start_time = meal_time + timedelta(minutes=30)
                    
                end_time = start_time + timedelta(minutes=med['duration_minutes'])
                scheduled_events.append({
                    "title": med['name'],
                    "start": start_time.isoformat(),
                    "end": end_time.isoformat(),
                    "type": "MEDICATION_CONSUMPTION",
                    "activity_id": med['id']
                })
                activity_counts[med['id']] += 1

    # 3. Schedule Others
    if adherence == "BREAK":
        continue
        
    for act in other_activities:
        # If we need this activity X times a week, distribute it
        # Simple approach: schedule it if we haven't hit the target yet for the week
        # But we should stagger them over days. For now, schedule it and increment.
        if activity_counts[act['id']] >= activity_targets[act['id']]:
            continue
            
        start_time = find_available_slot(current_day, act['duration_minutes'], act.get('time_slot'))
        # If it's the same time as something else, offset it (simplification)
        # Check if another fitness activity is at this exact time
        offset_mins = activity_counts[act['id']] * 60
        start_time = start_time + timedelta(minutes=offset_mins)
        
        end_time = start_time + timedelta(minutes=act['duration_minutes'])
        
        assigned_resources = []
        can_schedule = True
        for req in act['resource_requirements']:
            res_id = check_resource_availability(req['type'], req['subtype'], start_time, end_time)
            if res_id:
                assigned_resources.append(res_id)
            else:
                can_schedule = False
                break
                
        if can_schedule:
            scheduled_events.append({
                "title": act['name'],
                "start": start_time.isoformat(),
                "end": end_time.isoformat(),
                "type": act['type'],
                "activity_id": act['id'],
                "resources": assigned_resources
            })
            # Increment only when successfully scheduled
            activity_counts[act['id']] += 1

with open("schedule.json", "w") as f:
    json.dump(scheduled_events, f, indent=2)

print(f"Successfully generated schedule with {len(scheduled_events)} events.")
