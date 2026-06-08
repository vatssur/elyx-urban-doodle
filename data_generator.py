import json
import random
import uuid
from datetime import datetime, timedelta, timezone

START_DATE = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
END_DATE = START_DATE + timedelta(days=90)

def generate_activities(num_activities=100):
    activities = []
    
    # --- CONSTRAINTS: Exactly 1 of each core meal ---
    meals = [
        {"name": "High-protein Breakfast", "meal_type": "Breakfast", "prep_time": 15, "duration": 30},
        {"name": "Light Salad Lunch", "meal_type": "Lunch", "prep_time": 20, "duration": 45},
        {"name": "Steak Dinner", "meal_type": "Dinner", "prep_time": 45, "duration": 60}
    ]
    for meal in meals:
        activities.append({
            "id": f"act_{uuid.uuid4().hex[:8]}",
            "priority": 10,
            "type": "FOOD_CONSUMPTION",
            "name": meal["name"],
            "frequency": "Daily",
            "duration_minutes": meal["duration"],
            "prep_time_minutes": meal["prep_time"],
            "meal_type": meal["meal_type"],
            "remote_capable": False,
            "resource_requirements": []
        })

    # Templates for the remaining random activities
    FITNESS = [
        {"name": "Morning Run", "subtype": "Running", "time_slot": "morning"},
        {"name": "Yoga Session", "subtype": "Yoga", "time_slot": "morning"},
        {"name": "Weight Training", "subtype": "Weights", "time_slot": "evening"},
        {"name": "Eye Exercises", "subtype": "Eye Care", "time_slot": "afternoon"},
        {"name": "Cycling", "subtype": "Cardio", "time_slot": "afternoon"}
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

    for i in range(num_activities - len(meals)):
        activity_type = random.choices(
            ["FITNESS_ROUTINE", "MEDICATION_CONSUMPTION", "THERAPY", "CONSULTATION"],
            weights=[40, 30, 15, 15]
        )[0]
        
        act = {
            "id": f"act_{uuid.uuid4().hex[:8]}",
            "priority": random.randint(1, 9),
            "type": activity_type,
            "remote_capable": False,
            "prep_time_minutes": 0,
            "resource_requirements": []
        }
        
        if activity_type == "FITNESS_ROUTINE":
            template = random.choice(FITNESS)
            act["name"] = template["name"]
            act["frequency"] = f"{random.randint(2, 5)} times a week"
            act["duration_minutes"] = random.choice([30, 45, 60, 120]) # Added 2 hour exercise
            act["time_slot"] = template["time_slot"]
            if template["subtype"] in ["Weights", "Cardio"]:
                act["resource_requirements"].append({"type": "Equipment", "subtype": template["subtype"]})
            if random.random() > 0.5:
                act["resource_requirements"].append({"type": "Specialist", "subtype": "Personal Trainer"})
                act["remote_capable"] = random.choice([True, False])
                
        elif activity_type == "MEDICATION_CONSUMPTION":
            template = random.choice(MEDICATION)
            act["name"] = template["name"]
            act["frequency"] = "Daily"
            act["duration_minutes"] = 1 # Ensuring 1 minute blocks
            act["timing"] = template["timing"]
            
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
        
    activities.sort(key=lambda x: x["priority"], reverse=True)
    return activities

def generate_resources():
    resources = []
    subtypes = {
        "Equipment": ["Weights", "Cardio", "Ice Bath", "Sauna"],
        "Specialist": ["Personal Trainer", "Dietitian", "Psychologist"],
        "Allied Health": ["Massage Therapist", "Physiotherapist"]
    }
    for r_type, s_types in subtypes.items():
        for s_type in s_types:
            for i in range(random.randint(2, 5)):
                res = {
                    "id": f"res_{uuid.uuid4().hex[:8]}",
                    "name": f"{s_type} {i+1}",
                    "type": r_type,
                    "subtype": s_type,
                    "availability": []
                }
                res["available_hours_utc"] = {"start": "08:00", "end": "20:00"}
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
    return {
        "id": "client_1",
        "name": "Jane Doe",
        "timezone": "America/New_York",
        "base_availability_local": {
            "start": "08:00", 
            "end": "22:00"    
        },
        "travel_plans": [
            {
                "id": "trip_1",
                "start": (START_DATE + timedelta(days=10)).isoformat(),
                "end": (START_DATE + timedelta(days=15)).isoformat(),
                "adherence_level": "FLEXIBLE",
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
