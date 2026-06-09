from enum import Enum
from typing import List, Optional, Dict, Any
from datetime import datetime, time
from pydantic import BaseModel, Field

class ActivityType(str, Enum):
    FITNESS_ROUTINE = "FITNESS_ROUTINE"
    FOOD_CONSUMPTION = "FOOD_CONSUMPTION"
    MEDICATION_CONSUMPTION = "MEDICATION_CONSUMPTION"
    THERAPY = "THERAPY"
    CONSULTATION = "CONSULTATION"
    PREP = "PREP"
    SLEEP = "SLEEP"

class ResourceType(str, Enum):
    EQUIPMENT = "EQUIPMENT"
    SPECIALIST = "SPECIALIST"
    ALLIED_HEALTH = "ALLIED_HEALTH"

class AdherenceLevel(str, Enum):
    STRICT = "STRICT"
    FLEXIBLE = "FLEXIBLE"
    BREAK = "BREAK"

class ResourceRequirement(BaseModel):
    type: ResourceType
    subtype: str

class Resource(BaseModel):
    id: str
    name: str
    type: ResourceType
    subtype: str
    available_hours_utc: Dict[str, str]

class TravelPlan(BaseModel):
    start: str
    end: str
    adherence_level: AdherenceLevel
    destination_timezone: str

class AvailabilitySchedule(BaseModel):
    working_days: List[int] # 0=Mon, 6=Sun
    work_hours: Dict[str, str] # {"start": "09:00", "end": "17:00"}
    weekend_hours: Dict[str, str] # {"start": "07:00", "end": "22:00"}

class Preferences(BaseModel):
    day_start_hour: int
    day_end_hour: int
    min_gap_minutes: int

class ClientProfile(BaseModel):
    id: str
    base_timezone: str
    travel_plans: List[TravelPlan]
    availability: AvailabilitySchedule
    preferences: Preferences

class Activity(BaseModel):
    id: str
    name: str
    type: ActivityType
    duration_minutes: int
    frequency: str
    details: str
    facilitator_role: Optional[str]
    location: str
    remote_capable: bool
    prep_time_minutes: int
    backup_activities: List[str]
    adjustments_if_skipped: str
    metrics_to_collect: List[str]
    resource_requirements: List[ResourceRequirement]
    priority: int = 0
    time_slot: Optional[str] = None 
    meal_anchor: Optional[str] = None 
    transit_time_minutes: int = 0 

class ScheduledEvent(BaseModel):
    title: str
    start: str
    end: str
    type: ActivityType
    activity_id: str
    transit_minutes: int = 0
    resources: List[str]

class ScheduleResult(BaseModel):
    success: bool
    events: List[ScheduledEvent]
    errors: List[str]
