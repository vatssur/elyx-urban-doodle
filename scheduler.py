import json
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from typing import Any
from models import Activity, ClientProfile, Resource, ScheduledEvent, ActivityType, AdherenceLevel, ScheduleResult

def load_data() -> tuple[list[Activity], ClientProfile, list[Resource]]:
    """
    Load activities, client profile, and resources from JSON files.
    
    Returns:
        A tuple containing the list of Activities, the ClientProfile, and an empty list of resources.
    """
    with open('action_plan.json') as f:
        action_plan_data = json.load(f)
        activities = [Activity(**a) for a in action_plan_data]
        
    with open('client_profile.json') as f:
        profile_data = json.load(f)
        profile = ClientProfile(**profile_data)
            
    return activities, profile, []

def is_work_hour(dt_local: datetime, profile: ClientProfile) -> bool:
    """
    Check if a given local datetime falls within the user's working hours.
    
    Args:
        dt_local: The local datetime to check.
        profile: The ClientProfile containing work hour constraints.
        
    Returns:
        True if the time is within work hours, False otherwise.
    """
    weekday = dt_local.weekday()
    if weekday not in profile.availability.working_days:
        return False
        
    start_str = profile.availability.work_hours['start']
    end_str = profile.availability.work_hours['end']
    
    hour = dt_local.hour
    start_hour = int(start_str.split(':')[0])
    end_hour = int(end_str.split(':')[0])
    
    return start_hour <= hour < end_hour

def get_travel_status(dt_utc: datetime, profile: ClientProfile) -> tuple[str, str]:
    """
    Determine the adherence level and timezone based on travel plans.
    
    Args:
        dt_utc: The current UTC datetime.
        profile: The ClientProfile containing travel plans.
        
    Returns:
        A tuple of (adherence_level, timezone_string).
    """
    for trip in profile.travel_plans:
        t_start = datetime.fromisoformat(trip.start)
        t_end = datetime.fromisoformat(trip.end)
        if t_start <= dt_utc <= t_end:
            return trip.adherence_level, trip.destination_timezone
    return "STRICT", profile.base_timezone

def check_overlap(start_utc: datetime, end_utc: datetime, act_transit: int, min_gap: int, scheduled_events: list[dict[str, Any]]) -> bool:
    """
    Check if a proposed time slot (including transit padding and min gap) overlaps with existing events.
    
    Args:
        start_utc: The start time of the activity.
        end_utc: The end time of the activity.
        act_transit: The transit time in minutes to pad.
        min_gap: The minimum gap in minutes required between activities.
        scheduled_events: A list of already scheduled event dictionaries.
        
    Returns:
        True if there is an overlap, False if the slot is clear.
    """
    new_start = start_utc - timedelta(minutes=act_transit + min_gap)
    new_end = end_utc + timedelta(minutes=act_transit + min_gap)
    for e in scheduled_events:
        e_transit = e.get('transit_minutes', 0)
        e_start = datetime.fromisoformat(e['start']) - timedelta(minutes=e_transit)
        e_end = datetime.fromisoformat(e['end']) + timedelta(minutes=e_transit)
        if max(new_start, e_start) < min(new_end, e_end):
            return True
    return False

def schedule_events() -> ScheduleResult:
    """
    Execute the dynamic scheduling engine.
    
    Loads activities, sorts by priority, and iteratively finds non-overlapping
    time slots for each activity while enforcing sleep blocks and transit buffers.
    Writes the final schedule to 'schedule.json'.
    """
    try:
        activities, profile, resources = load_data()
    except Exception as e:
        return ScheduleResult(success=False, events=[], errors=[f"Data loading failed: {str(e)}"])
        
    scheduled_events: list[dict[str, Any]] = []
    
    start_date = datetime.now(ZoneInfo("UTC")).replace(hour=0, minute=0, second=0, microsecond=0)
    
    # Pre-sort activities by priority (1 is highest)
    activities.sort(key=lambda x: x.priority)
    
    # Process 12 weeks
    for week_idx in range(12):
        week_start_utc = start_date + timedelta(days=week_idx*7)
        
        # 0. SCHEDULE SLEEP BLOCKS EVERY DAY (22:00 to 06:00)
        for day_offset in range(7):
            current_day_utc = week_start_utc + timedelta(days=day_offset)
            adherence, tz_str = get_travel_status(current_day_utc, profile)
            client_tz = ZoneInfo(tz_str)
            
            local_sleep_start = datetime(
                year=current_day_utc.year, month=current_day_utc.month, day=current_day_utc.day,
                hour=22, minute=0, tzinfo=client_tz
            )
            local_sleep_end = local_sleep_start + timedelta(hours=8)
            
            utc_start = local_sleep_start.astimezone(ZoneInfo("UTC"))
            utc_end = local_sleep_end.astimezone(ZoneInfo("UTC"))
            
            scheduled_events.append({
                "title": "Sleep",
                "start": utc_start.isoformat(),
                "end": utc_end.isoformat(),
                "type": ActivityType.SLEEP,
                "activity_id": "sleep_block",
                "transit_minutes": 0,
                "resources": []
            })
        
        meals_scheduled = {} # map "DayOffset_Breakfast" to end_time
        
        # 1. HARDCODE MEALS FIRST to block out time
        for act in activities:
            if act.type == ActivityType.FOOD_CONSUMPTION:
                for day_offset in range(7):
                    current_day_utc = week_start_utc + timedelta(days=day_offset)
                    adherence, tz_str = get_travel_status(current_day_utc, profile)
                    client_tz = ZoneInfo(tz_str)
                    
                    # Meals get scheduled even on BREAK
                    if "Breakfast" in act.name: hour = 8
                    elif "Lunch" in act.name: hour = 13
                    else: hour = 19
                    
                    local_time = datetime(
                        year=current_day_utc.year, month=current_day_utc.month, day=current_day_utc.day,
                        hour=hour, minute=0, tzinfo=client_tz
                    )
                    utc_start = local_time.astimezone(ZoneInfo("UTC"))
                    utc_end = utc_start + timedelta(minutes=act.duration_minutes)
                    
                    scheduled_events.append({
                        "title": act.name,
                        "start": utc_start.isoformat(),
                        "end": utc_end.isoformat(),
                        "type": act.type,
                        "activity_id": act.id,
                        "transit_minutes": act.transit_time_minutes,
                        "resources": []
                    })
                    meals_scheduled[f"{day_offset}_{act.name}"] = utc_end

        # 2. SCHEDULE MEDICATIONS 
        for act in activities:
            if act.type == ActivityType.MEDICATION_CONSUMPTION:
                for day_offset in range(7):
                    anchor_meal = "Breakfast"
                    if act.meal_anchor == "after_dinner": anchor_meal = "Dinner"
                    
                    # Find meal end time
                    meal_key = None
                    for key in meals_scheduled.keys():
                        if key.startswith(f"{day_offset}_") and anchor_meal in key:
                            meal_key = key
                            break
                            
                    if meal_key:
                        meal_end = meals_scheduled[meal_key]
                        utc_start = meal_end + timedelta(minutes=5)
                        utc_end = utc_start + timedelta(minutes=act.duration_minutes)
                        
                        scheduled_events.append({
                            "title": act.name,
                            "start": utc_start.isoformat(),
                            "end": utc_end.isoformat(),
                            "type": act.type,
                            "activity_id": act.id,
                            "transit_minutes": 0,
                            "resources": []
                        })

        # 3. DYNAMIC PRIORITY SLOT ALLOCATION
        other_acts = [a for a in activities if a.type not in [ActivityType.FOOD_CONSUMPTION, ActivityType.MEDICATION_CONSUMPTION]]
        
        freq_map = {"DAILY": 7, "3_TIMES_A_WEEK": 3, "2_TIMES_A_WEEK": 2, "1_TIME_A_WEEK": 1, "1_TIME_A_MONTH": 1}
        
        for act in other_acts:
            # Skip if 1 time a month and not the right week
            if act.frequency == "1_TIME_A_MONTH" and week_idx % 4 != 0:
                continue
                
            times_to_schedule = freq_map.get(act.frequency, 1)
            times_scheduled = 0
            
            for day_offset in range(7):
                if times_scheduled >= times_to_schedule:
                    break
                    
                current_day_utc = week_start_utc + timedelta(days=day_offset)
                adherence, tz_str = get_travel_status(current_day_utc, profile)
                client_tz = ZoneInfo(tz_str)
                
                # Constraint: BREAK skips everything else
                if adherence == AdherenceLevel.BREAK:
                    continue
                    
                # Constraint: TRAVEL + NOT REMOTE CAPABLE -> Skip
                is_traveling = adherence in [AdherenceLevel.FLEXIBLE, AdherenceLevel.STRICT] and current_day_utc >= datetime.fromisoformat(profile.travel_plans[0].start)
                if is_traveling and not act.remote_capable:
                    continue
                    
                # Find available slot dynamically
                # Search from 06:00 to 22:00
                preferred_start = profile.preferences.day_start_hour
                preferred_end = profile.preferences.day_end_hour
                if act.time_slot == "morning": preferred_end = 12
                if act.time_slot == "afternoon": preferred_start = 12; preferred_end = 17
                if act.time_slot == "evening": preferred_start = 17; preferred_end = profile.preferences.day_end_hour
                
                for hour in range(preferred_start, preferred_end):
                    local_time = datetime(
                        year=current_day_utc.year, month=current_day_utc.month, day=current_day_utc.day,
                        hour=hour, minute=0, tzinfo=client_tz
                    )
                    
                    if is_work_hour(local_time, profile):
                        continue
                        
                    utc_start = local_time.astimezone(ZoneInfo("UTC"))
                    utc_end = utc_start + timedelta(minutes=act.duration_minutes)
                    
                    # Check overlap WITH transit times and min gap
                    if not check_overlap(utc_start, utc_end, act.transit_time_minutes, profile.preferences.min_gap_minutes, scheduled_events):
                        scheduled_events.append({
                            "title": act.name,
                            "start": utc_start.isoformat(),
                            "end": utc_end.isoformat(),
                            "type": act.type,
                            "activity_id": act.id,
                            "transit_minutes": act.transit_time_minutes,
                            "resources": []
                        })
                        times_scheduled += 1
                        break # Move to next day

    try:
        with open('schedule.json', 'w') as f:
            json.dump(scheduled_events, f, indent=2)
    except Exception as e:
        return ScheduleResult(success=False, events=[], errors=[f"Failed to write schedule.json: {str(e)}"])
        
    # Convert dicts to ScheduledEvent objects
    final_events = [ScheduledEvent(**e) for e in scheduled_events]
    return ScheduleResult(success=True, events=final_events, errors=[])

if __name__ == "__main__":
    result = schedule_events()
    if result.success:
        print("Successfully generated V8 Dynamic Schedule with Pydantic Models.")
    else:
        print("Failed to generate schedule:")
        for err in result.errors:
            print(f" - {err}")
