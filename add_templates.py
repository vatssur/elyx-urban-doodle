import json
import random

# Load existing
with open('templates.json', 'r') as f:
    templates = json.load(f)

new_templates = [
    ("Pilates Reformer", "FITNESS_ROUTINE", 45, "2_TIMES_A_WEEK", "Focus on core and flexibility.", "Pilates Instructor", "Studio", False, 10, "morning"),
    ("Cycling - Steady State", "FITNESS_ROUTINE", 60, "2_TIMES_A_WEEK", "Zone 2 cycling.", None, "Outdoors or Stationary", True, 10, "morning"),
    ("Swimming Laps", "FITNESS_ROUTINE", 45, "1_TIME_A_WEEK", "Moderate intensity freestyle.", None, "Local Pool", False, 15, "morning"),
    ("Deep Tissue Massage", "THERAPY", 60, "1_TIME_A_WEEK", "Focus on legs and back.", "Massage Therapist", "Clinic", False, 0, "afternoon"),
    ("Theragun Recovery", "THERAPY", 15, "DAILY", "Percussive therapy post-workout.", None, "Home", True, 0, "evening"),
    ("Red Light Therapy", "THERAPY", 15, "3_TIMES_A_WEEK", "Whole body PBM.", None, "Clinic", False, 5, "afternoon"),
    ("Hyperbaric Oxygen Therapy", "THERAPY", 60, "1_TIME_A_WEEK", "mHBOT at 1.3 ATA.", "Technician", "Clinic", False, 10, "morning"),
    ("Sleep Consultation", "CONSULTATION", 45, "1_TIME_A_MONTH", "Review sleep hygiene and CPAP data.", "Sleep Specialist", "Clinic", True, 10, "afternoon"),
    ("Blood Work - Comprehensive", "CONSULTATION", 30, "1_TIME_A_MONTH", "Lipid panel, hormones, metabolic.", "Phlebotomist", "Lab", False, 15, "morning"),
    ("VO2 Max Test", "CONSULTATION", 60, "1_TIME_A_MONTH", "Treadmill or bike protocol.", "Exercise Physiologist", "Lab", False, 10, "morning"),
    ("DEXA Scan", "CONSULTATION", 30, "1_TIME_A_MONTH", "Body composition tracking.", "Technician", "Lab", False, 10, "afternoon"),
    ("Psychotherapy Session", "CONSULTATION", 60, "1_TIME_A_WEEK", "CBT focus.", "Therapist", "Clinic", True, 5, "evening"),
    ("Stretching Routine", "FITNESS_ROUTINE", 15, "DAILY", "Full body mobility.", None, "Home", True, 0, "morning"),
    ("Foam Rolling", "THERAPY", 15, "DAILY", "Myofascial release.", None, "Home", True, 0, "evening"),
    ("Meditation", "THERAPY", 20, "DAILY", "Mindfulness and breathing.", None, "Home", True, 0, "morning"),
    ("Journaling", "PREP", 15, "DAILY", "Gratitude and daily planning.", None, "Home", True, 0, "evening"),
    ("Meal Prep (Weekly)", "PREP", 120, "1_TIME_A_WEEK", "Batch cook proteins and grains.", None, "Home", True, 0, "afternoon"),
    ("Grocery Shopping", "PREP", 60, "1_TIME_A_WEEK", "Buy whole foods.", None, "Store", False, 10, "morning"),
    ("Protein Shake", "FOOD_CONSUMPTION", 5, "DAILY", "Whey isolate with water.", None, "Home", True, 2, "afternoon"),
    ("Pre-Workout Snack", "FOOD_CONSUMPTION", 10, "DAILY", "Banana and almond butter.", None, "Home", True, 2, "morning"),
    ("Magnesium Supplement", "MEDICATION_CONSUMPTION", 1, "DAILY", "400mg Magnesium Glycinate.", None, "Home", True, 0, "evening"),
    ("Creatine Monohydrate", "MEDICATION_CONSUMPTION", 1, "DAILY", "5g with water.", None, "Home", True, 0, "morning"),
    ("Ashwagandha", "MEDICATION_CONSUMPTION", 1, "DAILY", "600mg KSM-66.", None, "Home", True, 0, "morning"),
    ("Multivitamin", "MEDICATION_CONSUMPTION", 1, "DAILY", "Take with food.", None, "Home", True, 0, "afternoon"),
    ("Chiropractic Adjustment", "THERAPY", 30, "1_TIME_A_WEEK", "Spinal alignment.", "Chiropractor", "Clinic", False, 5, "afternoon"),
    ("Acupuncture", "THERAPY", 60, "1_TIME_A_WEEK", "Traditional Chinese Medicine.", "Acupuncturist", "Clinic", False, 5, "morning"),
    ("Cryotherapy", "THERAPY", 10, "1_TIME_A_WEEK", "Whole body cryo chamber.", "Technician", "Clinic", False, 5, "afternoon"),
    ("Float Tank", "THERAPY", 90, "1_TIME_A_MONTH", "Sensory deprivation.", None, "Spa", False, 10, "evening"),
    ("Endurance Hike", "FITNESS_ROUTINE", 180, "1_TIME_A_MONTH", "Trail hiking with elevation.", None, "Outdoors", False, 30, "morning"),
    ("Rowing Machine Intervals", "FITNESS_ROUTINE", 30, "2_TIMES_A_WEEK", "2km repeats.", None, "Gym", False, 5, "morning"),
    ("Bouldering", "FITNESS_ROUTINE", 90, "1_TIME_A_WEEK", "Indoor rock climbing.", None, "Climbing Gym", False, 15, "evening"),
    ("Tennis Match", "FITNESS_ROUTINE", 120, "1_TIME_A_WEEK", "Singles match.", "Partner", "Tennis Court", False, 15, "afternoon"),
    ("Functional Movement Screen", "CONSULTATION", 45, "1_TIME_A_MONTH", "Assess mobility asymmetries.", "Physiotherapist", "Clinic", False, 5, "morning"),
    ("Continuous Glucose Monitor Setup", "CONSULTATION", 30, "1_TIME_A_MONTH", "Apply new CGM sensor.", "Nurse", "Clinic", False, 5, "morning"),
    ("Cardiologist Checkup", "CONSULTATION", 60, "1_TIME_A_MONTH", "ECG and BP review.", "Cardiologist", "Clinic", False, 10, "afternoon"),
    ("Optometrist Visit", "CONSULTATION", 45, "1_TIME_A_MONTH", "Eye health screening.", "Optometrist", "Clinic", False, 5, "morning"),
    ("Dentist Cleaning", "CONSULTATION", 60, "1_TIME_A_MONTH", "Routine prophylaxis.", "Hygienist", "Clinic", False, 5, "afternoon"),
    ("Personal Reflection", "PREP", 30, "1_TIME_A_WEEK", "Review weekly goals.", None, "Home", True, 0, "evening"),
    ("Supplement Organization", "PREP", 15, "1_TIME_A_WEEK", "Fill pill organizers.", None, "Home", True, 0, "afternoon"),
    ("Hydration Protocol", "PREP", 5, "DAILY", "Prepare 3L of water with electrolytes.", None, "Home", True, 2, "morning")
]

idx = len(templates) + 1
for t in new_templates:
    name, t_type, duration, freq, details, role, loc, remote, prep, slot = t
    templates.append({
        "template_id": f"TPL_NEW_{idx:03d}",
        "name": name,
        "type": t_type,
        "duration_minutes": duration,
        "frequency": freq,
        "details": details,
        "facilitator_role": role,
        "location": loc,
        "remote_capable": remote,
        "prep_time_minutes": prep,
        "adjustments_if_skipped": "None",
        "metrics_to_collect": ["Completion"],
        "resource_requirements": [{"type": "SPECIALIST", "subtype": role}] if role else [],
        "time_slot": slot,
        "meal_anchor": None
    })
    idx += 1

with open('templates.json', 'w') as f:
    json.dump(templates, f, indent=2)

print(f"Added 40 templates. Total is now {len(templates)}")
