import React, { useMemo } from 'react';
import rawData from './data/schedule.json';

const formatTime = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' });
};

const getDayName = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleDateString([], { weekday: 'long' });
};

const getShortDate = (isoString) => {
  const date = new Date(isoString);
  return date.toLocaleDateString([], { month: 'short', day: 'numeric' });
};

function App() {
  // Group events by day
  const daysMap = useMemo(() => {
    const map = new Map();
    
    rawData.forEach(event => {
      // Create a key based on the local date string so we group by local days
      const dateKey = new Date(event.start).toLocaleDateString();
      
      if (!map.has(dateKey)) {
        map.set(dateKey, {
          dateStr: event.start,
          events: []
        });
      }
      map.get(dateKey).events.push(event);
    });

    // Sort days chronologically
    const sortedDays = Array.from(map.values()).sort((a, b) => new Date(a.dateStr) - new Date(b.dateStr));
    
    // Sort events within each day chronologically
    sortedDays.forEach(day => {
      day.events.sort((a, b) => new Date(a.start) - new Date(b.start));
    });

    return sortedDays;
  }, []);

  const getTypeLabel = (type) => {
    switch (type) {
      case 'FITNESS_ROUTINE': return 'Fitness';
      case 'FOOD_CONSUMPTION': return 'Nutrition';
      case 'MEDICATION_CONSUMPTION': return 'Medication';
      case 'THERAPY': return 'Therapy';
      case 'CONSULTATION': return 'Consultation';
      case 'PREP': return 'Preparation';
      default: return 'Activity';
    }
  };

  return (
    <div className="calendar-container">
      <header className="header">
        <h1>HealthSpan</h1>
        <p>Your AI-Optimized Longevity Schedule</p>
      </header>

      <div className="week-grid">
        {daysMap.map((day, idx) => (
          <div key={idx} className="day-column glass">
            <div className="day-header">
              <h2>{getDayName(day.dateStr)}</h2>
              <span>{getShortDate(day.dateStr)}</span>
            </div>
            
            <div className="events-list">
              {day.events.map((evt, eIdx) => (
                <div key={eIdx} className={`event-card glass ${evt.type}`}>
                  <div className="event-time">
                    <svg width="14" height="14" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round">
                      <circle cx="12" cy="12" r="10"></circle>
                      <polyline points="12 6 12 12 16 14"></polyline>
                    </svg>
                    {formatTime(evt.start)} - {formatTime(evt.end)}
                  </div>
                  <h3 className="event-title">{evt.title}</h3>
                  <span className="event-type">{getTypeLabel(evt.type)}</span>
                </div>
              ))}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
}

export default App;
