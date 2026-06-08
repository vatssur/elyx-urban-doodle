from enum import Enum
from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from datetime import datetime, time

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

@dataclass
class ResourceRequirement:
    type: ResourceType
    subtype: str

@dataclass
class Resource:
    id: str
    name: str
    type: ResourceType
    subtype: str
    available_hours_utc: Dict[str, str]

@dataclass
class TravelPlan:
    start: str
    end: str
    adherence_level: AdherenceLevel
    destination_timezone: str

@dataclass
class AvailabilitySchedule:
    working_days: List[int] # 0=Mon, 6=Sun
    work_hours: Dict[str, str] # {"start": "09:00", "end": "17:00"}
    weekend_hours: Dict[str, str] # {"start": "07:00", "end": "22:00"}

@dataclass
class ClientProfile:
    id: str
    base_timezone: str
    travel_plans: List[TravelPlan]
    availability: AvailabilitySchedule

@dataclass
class Activity:
    id: str
    name: str
    type: ActivityType
    duration_minutes: int
    frequency: str  # e.g., "DAILY", "3_TIMES_A_WEEK"
    details: str
    facilitator_role: Optional[str]
    location: str
    remote_capable: bool
    prep_time_minutes: int
    backup_activities: List[str] # List of Activity IDs
    adjustments_if_skipped: str
    metrics_to_collect: List[str]
    resource_requirements: List[ResourceRequirement]
    priority: int = 0
    time_slot: Optional[str] = None 
    meal_anchor: Optional[str] = None 
    transit_time_minutes: int = 0 

@dataclass
class ScheduledEvent:
    title: str
    start: str
    end: str
    type: ActivityType
    activity_id: str
    resources: List[str]
