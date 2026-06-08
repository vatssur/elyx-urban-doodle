import React from 'react';
import type { DayData, AdherenceLevel } from '../types';

interface DayCardProps {
  day: DayData;
  travelStatus: AdherenceLevel | null;
}

const formatTime = (isoString: string) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const getDayName = (dateObj: Date) => {
  return dateObj.toLocaleDateString([], { weekday: 'long', month: 'long', day: 'numeric' });
};

const getTypeLabel = (type: string) => {
  switch (type) {
    case 'FITNESS_ROUTINE': return 'Fitness';
    case 'FOOD_CONSUMPTION': return 'Nutrition';
    case 'MEDICATION_CONSUMPTION': return 'Medication';
    case 'THERAPY': return 'Therapy';
    case 'CONSULTATION': return 'Consultation';
    case 'PREP': return 'Prep';
    default: return 'Activity';
  }
};

export const DayCard: React.FC<DayCardProps> = ({ day, travelStatus }) => {
  return (
    <div className="day-card glass">
      <div className="day-card-header">
        <h2>{getDayName(day.dateObj)}</h2>
      </div>
      
      {/* Out of Office Banner */}
      {travelStatus && (
        <div className={`ooo-banner ${travelStatus}`}>
          <span className="ooo-icon">&#9992;</span>
          <div>
            <strong>Out of Office: Travel</strong>
            <p>Adherence Level: {travelStatus}. The schedule has been adjusted accordingly.</p>
          </div>
        </div>
      )}
      
      <div className="day-events-list">
        {day.events.length === 0 ? (
          <p className="no-events">No activities scheduled for this day.</p>
        ) : (
          day.events.map((evt, eIdx) => (
            <div key={eIdx} className={`list-item ${evt.type}`}>
              <div className="li-time">
                {formatTime(evt.start)}
                <span className="li-duration">
                  {Math.round((new Date(evt.end).getTime() - new Date(evt.start).getTime()) / 60000)} min
                </span>
              </div>
              <div className="li-details">
                <span className="li-title">{evt.title}</span>
                <span className={`badge ${evt.type}`}>{getTypeLabel(evt.type)}</span>
              </div>
            </div>
          ))
        )}
      </div>
    </div>
  );
};
