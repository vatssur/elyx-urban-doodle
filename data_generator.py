import json
import uuid
import random
from typing import Any
from models import ActivityType

def load_templates() -> list[dict[str, Any]]:
    """Load templates from templates.json."""
    with open('templates.json', 'r') as f:
        data: list[dict[str, Any]] = json.load(f)
        return data

def generate_activities(templates: list[dict[str, Any]], total_count: int = 150) -> list[dict[str, Any]]:
    """
    Generate a global pool of unique activity instances from templates.
    """
    activities = []
    
    # Create instances to fill up to total_count, but guarantee all templates are used at least once
    pool = list(templates) + [random.choice(templates) for _ in range(total_count - len(templates))]
    
    # 1. Generate the base activities
    for tpl in pool:
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
            "transit_time_minutes": tpl.get('transit_time_minutes', 0),
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
    fitness_ids = [a['id'] for a in activities if a['type'] == ActivityType.FITNESS_ROUTINE]
    for act in activities:
        if act['type'] == ActivityType.FITNESS_ROUTINE and len(fitness_ids) > 1:
            backups = random.sample([x for x in fitness_ids if x != act['id']], min(2, len(fitness_ids)-1))
            act['backup_activities'] = backups
            
    return activities

def extract_action_plan(activities: list[dict[str, Any]], target_count: int = 25) -> list[dict[str, Any]]:
    """
    Extract a unique 25-item Action Plan from the global pool, guaranteeing meals.
    """
    plan = []
    seen_names = set()
    
    # Extract meals
    breakfasts = [a for a in activities if "Breakfast" in a['name']]
    lunches = [a for a in activities if "Lunch" in a['name']]
    dinners = [a for a in activities if "Dinner" in a['name']]
    
    if breakfasts: 
        plan.append(breakfasts[0])
        seen_names.add(breakfasts[0]['name'])
    if lunches: 
        plan.append(lunches[0])
        seen_names.add(lunches[0]['name'])
    if dinners: 
        plan.append(dinners[0])
        seen_names.add(dinners[0]['name'])
    
    # Extract specific meds to anchor to meals
    meds = [a for a in activities if a['type'] == ActivityType.MEDICATION_CONSUMPTION]
    for m in meds[:2]:
        if m['name'] not in seen_names:
            plan.append(m)
            seen_names.add(m['name'])
            
    # Fill the rest randomly from fitness, therapy, consultation
    # Ensuring NO duplicate template names are added!
    remaining = [
        a for a in activities 
        if a['name'] not in seen_names 
        and a['type'] not in [ActivityType.FOOD_CONSUMPTION, ActivityType.MEDICATION_CONSUMPTION]
    ]
    random.shuffle(remaining)
    
    needed = target_count - len(plan)
    for a in remaining:
        if len(plan) >= target_count:
            break
        if a['name'] not in seen_names:
            plan.append(a)
            seen_names.add(a['name'])
    
    # Sort by priority (1 is highest)
    plan.sort(key=lambda x: x['priority'])
    
    return plan

def generate_client_profile() -> dict[str, Any]:
    """Generate a client profile with travel plans and work hours."""
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
            "weekend_hours": {
                "start": "07:00",
                "end": "22:00"
            }
        },
        "preferences": {
            "day_start_hour": 6,
            "day_end_hour": 22,
            "min_gap_minutes": 15
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
    print(f"Generated {len(action_plan)} unique action plan items in action_plan.json")
    print(f"Generated client_profile.json with 2 travel plans")
