import React from 'react';
import type { DayData, ClientProfile, AdherenceLevel } from '../types';
import { DayCard } from './DayCard';

interface AgendaProps {
  currentDays: DayData[];
  clientProfile: ClientProfile;
}

export const Agenda: React.FC<AgendaProps> = ({ currentDays, clientProfile }) => {
  
  const getTravelStatus = (dateObj: Date): AdherenceLevel | null => {
    for (const trip of clientProfile.travel_plans) {
      const start = new Date(trip.start);
      const end = new Date(trip.end);
      if (dateObj >= start && dateObj <= end) {
        return trip.adherence_level;
      }
    }
    return null;
  };

  return (
    <div className="agenda-list">
      {currentDays.map((day, idx) => (
        <DayCard 
          key={idx} 
          day={day} 
          travelStatus={getTravelStatus(day.dateObj)} 
        />
      ))}
    </div>
  );
};
