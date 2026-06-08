import json
import random
import uuid
from datetime import datetime, timedelta, timezone

# We need to generate schedules starting from today, for 3 months.
START_DATE = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
END_DATE = START_DATE + timedelta(days=90)

def generate_activities(num_activities=100):
    activities = []
    
    # Templates for activities
    FITNESS = [
        {"name": "Morning Run", "subtype": "Running", "time_slot": "morning"},
        {"name": "Yoga Session", "subtype": "Yoga", "time_slot": "morning"},
        {"name": "Weight Training", "subtype": "Weights", "time_slot": "evening"},
        {"name": "Eye Exercises", "subtype": "Eye Care", "time_slot": "afternoon"},
        {"name": "Cycling", "subtype": "Cardio", "time_slot": "afternoon"}
    ]
    
    FOOD = [
        {"name": "High-protein Breakfast", "subtype": "Breakfast", "prep_time": 15},
        {"name": "Light Salad Lunch", "subtype": "Lunch", "prep_time": 20},
        {"name": "Steak Dinner", "subtype": "Dinner", "prep_time": 45},
        {"name": "Protein Shake", "subtype": "Snack", "prep_time": 5}
    ]
    
    MEDICATION = [
        {"name": "Vitamin D", "timing": "after Breakfast"},
        {"name": "Omega 3", "timing": "after Dinner"},
        {"name": "Probiotic", "timing": "before Breakfast"},
        {"name": "Multivitamin", "timing": "after Lunch"}
    ]
    
    THERAPY = [
        {"name": "Ice Bath", "subtype": "Cold Exposure"},
        {"name": "Sauna", "subtype": "Heat Exposure"},
        {"name": "Massage", "subtype": "Physical Therapy"}
    ]
    
    CONSULTATION = [
        {"name": "Dietitian Check-in", "subtype": "Dietitian"},
        {"name": "Therapy Session", "subtype": "Psychologist"},
        {"name": "Physio Check", "subtype": "Physiotherapist"}
    ]

    for i in range(num_activities):
        activity_type = random.choices(
            ["FITNESS_ROUTINE", "FOOD_CONSUMPTION", "MEDICATION_CONSUMPTION", "THERAPY", "CONSULTATION"],
            weights=[30, 30, 20, 10, 10]
        )[0]
        
        act = {
            "id": f"act_{uuid.uuid4().hex[:8]}",
            "priority": random.randint(1, 10),
            "type": activity_type,
            "remote_capable": False,
            "prep_time_minutes": 0,
            "resource_requirements": []
        }
        
        if activity_type == "FITNESS_ROUTINE":
            template = random.choice(FITNESS)
            act["name"] = template["name"]
            act["frequency"] = f"{random.randint(2, 5)} times a week"
            act["duration_minutes"] = random.choice([30, 45, 60])
            act["time_slot"] = template["time_slot"]
            if template["subtype"] in ["Weights", "Cardio"]:
                act["resource_requirements"].append({"type": "Equipment", "subtype": template["subtype"]})
            if random.random() > 0.5:
                act["resource_requirements"].append({"type": "Specialist", "subtype": "Personal Trainer"})
                act["remote_capable"] = random.choice([True, False])
                
        elif activity_type == "FOOD_CONSUMPTION":
            template = random.choice(FOOD)
            act["name"] = template["name"]
            act["frequency"] = "Daily"
            act["duration_minutes"] = 30
            act["prep_time_minutes"] = template["prep_time"]
            act["meal_type"] = template["subtype"]
            
        elif activity_type == "MEDICATION_CONSUMPTION":
            template = random.choice(MEDICATION)
            act["name"] = template["name"]
            act["frequency"] = "Daily"
            act["duration_minutes"] = 1
            act["timing"] = template["timing"] # e.g. "after Breakfast"
            
        elif activity_type == "THERAPY":
            template = random.choice(THERAPY)
            act["name"] = template["name"]
            act["frequency"] = f"{random.randint(1, 3)} times a week"
            act["duration_minutes"] = random.choice([15, 30, 60])
            if template["subtype"] == "Physical Therapy":
                act["resource_requirements"].append({"type": "Allied Health", "subtype": "Massage Therapist"})
            else:
                act["resource_requirements"].append({"type": "Equipment", "subtype": template["name"]})
                
        elif activity_type == "CONSULTATION":
            template = random.choice(CONSULTATION)
            act["name"] = template["name"]
            act["frequency"] = "Once a month"
            act["duration_minutes"] = random.choice([30, 60])
            act["resource_requirements"].append({"type": "Specialist", "subtype": template["subtype"]})
            act["remote_capable"] = True
            
        activities.append(act)
        
    # Sort by priority
    activities.sort(key=lambda x: x["priority"], reverse=True)
    return activities

def generate_resources():
    resources = []
    
    subtypes = {
        "Equipment": ["Weights", "Cardio", "Ice Bath", "Sauna"],
        "Specialist": ["Personal Trainer", "Dietitian", "Psychologist"],
        "Allied Health": ["Massage Therapist", "Physiotherapist"]
    }
    
    # Create a few instances of each
    for r_type, s_types in subtypes.items():
        for s_type in s_types:
            for i in range(random.randint(2, 5)): # 2-5 resources per subtype
                res = {
                    "id": f"res_{uuid.uuid4().hex[:8]}",
                    "name": f"{s_type} {i+1}",
                    "type": r_type,
                    "subtype": s_type,
                    "availability": [] # Instead of listing every minute of 3 months, let's list their available hours
                }
                
                # Standard availability: e.g. 8 AM to 8 PM UTC
                res["available_hours_utc"] = {
                    "start": "08:00",
                    "end": "20:00"
                }
                
                # Add some random unavailabilities (e.g. booked slots) for the next 90 days
                booked_slots = []
                for _ in range(20):
                    day_offset = random.randint(0, 89)
                    hour = random.randint(8, 18)
                    date_val = START_DATE + timedelta(days=day_offset, hours=hour)
                    booked_slots.append({
                        "start": date_val.isoformat(),
                        "end": (date_val + timedelta(hours=1)).isoformat()
                    })
                
                res["booked_slots"] = booked_slots
                resources.append(res)
                
    return resources

def generate_client_profile():
    # Example client profile
    return {
        "id": "client_1",
        "name": "Jane Doe",
        "timezone": "America/New_York",
        "base_availability_utc": {
            "start": "12:00", # 8 AM EST
            "end": "02:00"    # 10 PM EST next day UTC
        },
        "travel_plans": [
            {
                "id": "trip_1",
                "start": (START_DATE + timedelta(days=10)).isoformat(),
                "end": (START_DATE + timedelta(days=15)).isoformat(),
                "adherence_level": "FLEXIBLE", # or BREAK, MAINTAIN
                "destination_timezone": "Europe/London"
            }
        ]
    }

if __name__ == "__main__":
    activities = generate_activities(100)
    resources = generate_resources()
    client_profile = generate_client_profile()
    
    with open("activities.json", "w") as f:
        json.dump(activities, f, indent=2)
        
    with open("resources.json", "w") as f:
        json.dump(resources, f, indent=2)
        
    with open("client_profile.json", "w") as f:
        json.dump(client_profile, f, indent=2)
        
    print("Generated data successfully.")
