import json
import uuid
import random

def load_templates():
    with open('templates.json', 'r') as f:
        return json.load(f)

def generate_activities(templates, total_count=150):
    activities = []
    
    # 1. Generate the base activities
    for i in range(total_count):
        tpl = random.choice(templates)
        
        # Create a unique instance
        act = {
            "id": f"act_{uuid.uuid4().hex[:8]}",
            "name": tpl['name'],
            "type": tpl['type'],
            "duration_minutes": tpl['duration_minutes'],
            "frequency": tpl['frequency'],
            "details": tpl['details'],
            "facilitator_role": tpl['facilitator_role'],
            "location": tpl['location'],
            "remote_capable": tpl['remote_capable'],
            "prep_time_minutes": tpl['prep_time_minutes'],
            "backup_activities": [], # Will populate in step 2
            "adjustments_if_skipped": tpl['adjustments_if_skipped'],
            "metrics_to_collect": tpl['metrics_to_collect'],
            "resource_requirements": tpl['resource_requirements'],
            "time_slot": tpl.get('time_slot'),
            "meal_anchor": tpl.get('meal_anchor'),
            "priority": random.randint(1, 10) # Lower is more important
        }
        activities.append(act)
        
    # 2. Self-join Backup Activities
    # For every fitness activity, assign 1-2 other fitness activities as backup
    fitness_ids = [a['id'] for a in activities if a['type'] == 'FITNESS_ROUTINE']
    for act in activities:
        if act['type'] == 'FITNESS_ROUTINE' and len(fitness_ids) > 1:
            backups = random.sample([x for x in fitness_ids if x != act['id']], min(2, len(fitness_ids)-1))
            act['backup_activities'] = backups
            
    return activities

def extract_action_plan(activities, target_count=25):
    # We must guarantee 1 breakfast, 1 lunch, 1 dinner, and 1 med for each
    plan = []
    
    # Extract meals
    breakfasts = [a for a in activities if "Breakfast" in a['name']]
    lunches = [a for a in activities if "Lunch" in a['name']]
    dinners = [a for a in activities if "Dinner" in a['name']]
    
    if breakfasts: plan.append(breakfasts[0])
    if lunches: plan.append(lunches[0])
    if dinners: plan.append(dinners[0])
    
    # Extract specific meds to anchor to meals
    meds = [a for a in activities if a['type'] == 'MEDICATION_CONSUMPTION']
    for m in meds[:2]:
        if m['id'] not in [p['id'] for p in plan]:
            plan.append(m)
            
    # Fill the rest randomly from fitness, therapy, consultation
    remaining = [
        a for a in activities 
        if a['id'] not in [p['id'] for p in plan] 
        and a['type'] not in ['FOOD_CONSUMPTION', 'MEDICATION_CONSUMPTION']
    ]
    random.shuffle(remaining)
    
    needed = target_count - len(plan)
    plan.extend(remaining[:needed])
    
    # Sort by priority (1 is highest)
    plan.sort(key=lambda x: x['priority'])
    
    return plan

def generate_client_profile():
    profile = {
        "id": "client_1",
        "base_timezone": "America/New_York",
        "travel_plans": [
            {
                "id": "trip_1",
                "start": "2026-06-18T00:00:00+00:00",
                "end": "2026-06-23T00:00:00+00:00",
                "adherence_level": "FLEXIBLE",
                "destination_timezone": "Europe/London"
            },
            {
                "id": "trip_2",
                "start": "2026-07-10T00:00:00+00:00",
                "end": "2026-07-15T00:00:00+00:00",
                "adherence_level": "BREAK",
                "destination_timezone": "America/Los_Angeles"
            }
        ],
        "availability": {
            "working_days": [0, 1, 2, 3, 4], # Mon-Fri
            "work_hours": {"start": "09:00", "end": "17:00"},
            "weekend_hours": {"start": "07:00", "end": "22:00"}
        }
    }
    return profile

if __name__ == "__main__":
    templates = load_templates()
    
    # 1. Generate 150 Global Database Activities
    activities = generate_activities(templates, 150)
    with open('activities.json', 'w') as f:
        json.dump(activities, f, indent=2)
        
    # 2. Extract 25-item Action Plan
    action_plan = extract_action_plan(activities, 25)
    with open('action_plan.json', 'w') as f:
        json.dump(action_plan, f, indent=2)
        
    # 3. Generate Client Profile
    profile = generate_client_profile()
    with open('client_profile.json', 'w') as f:
        json.dump(profile, f, indent=2)
        
    print(f"Generated {len(activities)} activities in activities.json")
    print(f"Generated {len(action_plan)} action plan items in action_plan.json")
    print(f"Generated client_profile.json with 2 travel plans")
