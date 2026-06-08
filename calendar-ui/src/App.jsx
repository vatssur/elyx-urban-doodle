import React, { useMemo, useState } from 'react';
import rawData from './data/schedule.json';

const HOUR_HEIGHT = 60; // 60px per hour
const START_HOUR = 0;   // Timeline starts at midnight
const END_HOUR = 24;    // Timeline ends at midnight next day
const TOTAL_HOURS = END_HOUR - START_HOUR;

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
  const [weekOffset, setWeekOffset] = useState(0);

  // Group events by day
  const allDays = useMemo(() => {
    const map = new Map();
    
    rawData.forEach(event => {
      const date = new Date(event.start);
      const dateKey = date.toLocaleDateString();
      
      if (!map.has(dateKey)) {
        map.set(dateKey, {
          dateStr: event.start,
          events: []
        });
      }
      
      const startHour = date.getHours();
      const startMin = date.getMinutes();
      const end = new Date(event.end);
      const durationMins = (end - date) / (1000 * 60);
      
      if (startHour < START_HOUR || startHour >= END_HOUR) return;
      
      const topOffset = (startHour - START_HOUR) * HOUR_HEIGHT + (startMin / 60) * HOUR_HEIGHT;
      // Strict min height so 1-min medicine blocks are visible
      const blockHeight = Math.max(durationMins * (HOUR_HEIGHT / 60), 8); 
      
      map.get(dateKey).events.push({
        ...event,
        top: topOffset,
        height: blockHeight
      });
    });

    return Array.from(map.values()).sort((a, b) => new Date(a.dateStr) - new Date(b.dateStr));
  }, []);

  const totalWeeks = Math.ceil(allDays.length / 7);
  const currentWeekDays = allDays.slice(weekOffset * 7, (weekOffset + 7) * 7);

  const getTypeLabel = (type) => {
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

  const timeMarkers = Array.from({ length: TOTAL_HOURS + 1 }).map((_, i) => START_HOUR + i);

  return (
    <div className="calendar-container">
      <header className="header">
        <h1>HealthSpan</h1>
        <p>Your AI-Optimized Longevity Schedule</p>
        
        <div className="pagination">
          <button 
            disabled={weekOffset === 0} 
            onClick={() => setWeekOffset(w => w - 1)}
          >
            &larr; Previous Week
          </button>
          <span>Week {weekOffset + 1} of {totalWeeks}</span>
          <button 
            disabled={weekOffset >= totalWeeks - 1} 
            onClick={() => setWeekOffset(w => w + 1)}
          >
            Next Week &rarr;
          </button>
        </div>
      </header>

      <div className="timeline-container">
        {/* Y-Axis Time Labels */}
        <div className="time-labels">
          <div className="time-header-spacer"></div>
          {timeMarkers.map(hour => (
            <div key={hour} className="time-label" style={{ height: HOUR_HEIGHT }}>
              {hour === 0 || hour === 24 ? '12 AM' : hour === 12 ? '12 PM' : hour > 12 ? `${hour - 12} PM` : `${hour} AM`}
            </div>
          ))}
        </div>

        {/* 7-Day Grid */}
        <div className="week-grid">
          {currentWeekDays.slice(0, 7).map((day, idx) => (
            <div key={idx} className="day-column glass">
              <div className="day-header">
                <h2>{getDayName(day.dateStr).substring(0, 3)}</h2>
                <span>{getShortDate(day.dateStr)}</span>
              </div>
              
              <div className="day-timeline" style={{ height: TOTAL_HOURS * HOUR_HEIGHT }}>
                {/* Horizontal grid lines */}
                {timeMarkers.slice(0, -1).map(hour => (
                  <div key={hour} className="grid-line" style={{ top: (hour - START_HOUR) * HOUR_HEIGHT }}></div>
                ))}
                
                {/* Events */}
                {day.events.map((evt, eIdx) => (
                  <div 
                    key={eIdx} 
                    className={`event-block ${evt.type}`}
                    style={{ top: evt.top, height: evt.height }}
                  >
                    {/* Only show title inside block if it's tall enough */}
                    {evt.height > 20 && <span className="block-title">{evt.title}</span>}
                    
                    {/* Hover Tooltip Popup */}
                    <div className="tooltip glass">
                      <div className="tooltip-header">
                        <h4>{evt.title}</h4>
                        <span className={`badge ${evt.type}`}>{getTypeLabel(evt.type)}</span>
                      </div>
                      <div className="tooltip-time">
                        {formatTime(evt.start)} - {formatTime(evt.end)}
                      </div>
                      {evt.resources && evt.resources.length > 0 && (
                        <div className="tooltip-resources">
                          <strong>Resources:</strong> {evt.resources.join(', ')}
                        </div>
                      )}
                    </div>
                  </div>
                ))}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Legend */}
      <div className="legend glass">
        <h3>Legend</h3>
        <div className="legend-items">
          <div className="legend-item"><span className="swatch FITNESS_ROUTINE"></span> Fitness</div>
          <div className="legend-item"><span className="swatch FOOD_CONSUMPTION"></span> Nutrition</div>
          <div className="legend-item"><span className="swatch MEDICATION_CONSUMPTION"></span> Medication</div>
          <div className="legend-item"><span className="swatch THERAPY"></span> Therapy</div>
          <div className="legend-item"><span className="swatch CONSULTATION"></span> Consultation</div>
          <div className="legend-item"><span className="swatch PREP"></span> Prep</div>
        </div>
      </div>
    </div>
  );
}

export default App;
