export type ActivityType = 
  | "FITNESS_ROUTINE"
  | "FOOD_CONSUMPTION"
  | "MEDICATION_CONSUMPTION"
  | "THERAPY"
  | "CONSULTATION"
  | "PREP"
  | "SLEEP";

export type AdherenceLevel = "STRICT" | "FLEXIBLE" | "BREAK";

export interface Activity {
  id: string;
  name: string;
  type: ActivityType;
  duration_minutes: number;
  frequency: string;
  details: string;
  facilitator_role: string | null;
  location: string;
  remote_capable: boolean;
  prep_time_minutes: number;
  transit_time_minutes: number;
  backup_activities: string[];
  adjustments_if_skipped: string;
  metrics_to_collect: string[];
  priority: number;
}

export interface TravelPlan {
  id: string;
  start: string;
  end: string;
  adherence_level: AdherenceLevel;
  destination_timezone: string;
}

export interface ClientProfile {
  id: string;
  base_timezone: string;
  travel_plans: TravelPlan[];
}

export interface ScheduledEvent {
  title: string;
  start: string;
  end: string;
  type: string;
  activity_id: string;
  transit_minutes: number;
}

export interface DayData {
  dateObj: Date;
  dateStr: string;
  events: ScheduledEvent[];
}
