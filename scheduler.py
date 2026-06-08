import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from models import Activity, ClientProfile, Resource, ScheduledEvent, ResourceType

def load_data():
    with open('action_plan.json') as f:
        action_plan_data = json.load(f)
        activities = [Activity(**a) for a in action_plan_data]
        
    with open('client_profile.json') as f:
        profile_data = json.load(f)
        profile = ClientProfile(**profile_data)
        
    with open('resources.json') as f:
        resources_data = json.load(f)
        resources = []
        for r in resources_data:
            try:
                res_type = ResourceType(r['type'].upper())
            except ValueError:
                res_type = ResourceType.EQUIPMENT # fallback
                
            resources.append(Resource(
                id=r['id'],
                name=r.get('name', ''),
                type=res_type,
                subtype=r['subtype'],
                available_hours_utc=r.get('available_hours_utc', {})
            ))
        
    return activities, profile, resources

def is_work_hour(dt_local, profile: ClientProfile):
    weekday = dt_local.weekday()
    if weekday not in profile.availability['working_days']:
        return False # Weekend, not work hour
        
    start_str = profile.availability['work_hours']['start']
    end_str = profile.availability['work_hours']['end']
    
    # Very simple check
    hour = dt_local.hour
    start_hour = int(start_str.split(':')[0])
    end_hour = int(end_str.split(':')[0])
    
    return start_hour <= hour < end_hour

def schedule_events():
    activities, profile, resources = load_data()
    scheduled_events = []
    
    start_date = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
    
    for day_idx in range(90):
        current_day_utc = start_date + timedelta(days=day_idx)
        current_day_str = current_day_utc.isoformat()
        
        # Determine Travel Status
        adherence = "STRICT"
        current_tz_str = profile.base_timezone
        
        for trip in profile.travel_plans:
            t_start = datetime.fromisoformat(trip['start'])
            t_end = datetime.fromisoformat(trip['end'])
            if t_start <= current_day_utc <= t_end:
                adherence = trip['adherence_level']
                current_tz_str = trip['destination_timezone']
                break
                
        client_tz = ZoneInfo(current_tz_str)
        
        # Skip everything if BREAK
        if adherence == "BREAK":
            continue
            
        daily_fitness = 0
        meals_scheduled = {} # map "Breakfast" to end_time
        
        # 1. Schedule Meals
        for act in activities:
            if act.type == "FOOD_CONSUMPTION":
                
                if "Breakfast" in act.name: hour = 8
                elif "Lunch" in act.name: hour = 13
                else: hour = 19
                
                local_time = datetime(
                    year=current_day_utc.year, month=current_day_utc.month, day=current_day_utc.day,
                    hour=hour, minute=0, tzinfo=client_tz
                )
                
                # Check work hours (usually meals are allowed, but let's say lunch is 1pm, we schedule it)
                utc_start = local_time.astimezone(ZoneInfo("UTC"))
                utc_end = utc_start + timedelta(minutes=act.duration_minutes)
                
                scheduled_events.append({
                    "title": act.name,
                    "start": utc_start.isoformat(),
                    "end": utc_end.isoformat(),
                    "type": act.type,
                    "activity_id": act.id,
                    "resources": []
                })
                meals_scheduled[act.name] = utc_end
                
                # Prep
                prep_start = utc_start - timedelta(minutes=act.prep_time_minutes)
                scheduled_events.append({
                    "title": f"Prep: {act.name}",
                    "start": prep_start.isoformat(),
                    "end": utc_start.isoformat(),
                    "type": "PREP",
                    "activity_id": act.id,
                    "resources": []
                })

        # 2. Schedule Medications relative to meals
        for act in activities:
            if act.type == "MEDICATION_CONSUMPTION":
                anchor_meal = None
                if act.meal_anchor == "after_breakfast": anchor_meal = "Breakfast"
                elif act.meal_anchor == "after_dinner": anchor_meal = "Dinner"
                else: anchor_meal = "Breakfast" # default
                
                # Find the meal end time
                meal_end = None
                for name, end_t in meals_scheduled.items():
                    if anchor_meal in name:
                        meal_end = end_t
                        break
                        
                if meal_end:
                    utc_start = meal_end + timedelta(minutes=5) # 5 mins AFTER meal ends
                    utc_end = utc_start + timedelta(minutes=act.duration_minutes)
                    scheduled_events.append({
                        "title": act.name,
                        "start": utc_start.isoformat(),
                        "end": utc_end.isoformat(),
                        "type": act.type,
                        "activity_id": act.id,
                        "resources": []
                    })

        # 3. Schedule Others (Fitness, Therapy, Consult)
        for act in activities:
            if act.type in ["FOOD_CONSUMPTION", "MEDICATION_CONSUMPTION"]: continue
            
            # Quotas & Travel
            if adherence == "FLEXIBLE" and act.type in ["THERAPY", "CONSULTATION"]: continue
            if act.type == "FITNESS_ROUTINE":
                if daily_fitness >= 1: continue
            
            # Only schedule 2 times a week roughly
            if act.frequency == "2_TIMES_A_WEEK" and day_idx % 3 != 0: continue
            if act.frequency == "1_TIME_A_WEEK" and day_idx % 7 != 0: continue
            
            hour = 7 if act.time_slot == "morning" else 18 if act.time_slot == "evening" else 15
            
            local_time = datetime(
                year=current_day_utc.year, month=current_day_utc.month, day=current_day_utc.day,
                hour=hour, minute=0, tzinfo=client_tz
            )
            
            # Enforce Work Hours!
            if is_work_hour(local_time, profile):
                # Push it to 18:00 (after work)
                local_time = local_time.replace(hour=18)
                
            utc_start = local_time.astimezone(ZoneInfo("UTC"))
            utc_end = utc_start + timedelta(minutes=act.duration_minutes)
            
            scheduled_events.append({
                "title": act.name,
                "start": utc_start.isoformat(),
                "end": utc_end.isoformat(),
                "type": act.type,
                "activity_id": act.id,
                "resources": [] # Mocked for simplicity in V4 to focus on timeline
            })
            if act.type == "FITNESS_ROUTINE":
                daily_fitness += 1
                
    with open('schedule.json', 'w') as f:
        json.dump(scheduled_events, f, indent=2)

if __name__ == "__main__":
    schedule_events()
    print("Successfully generated schedule.json with quotas and OOO constraints.")
