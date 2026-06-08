import React, { useMemo, useState } from 'react';
import rawData from './data/schedule.json';
import actionPlanData from './data/action_plan.json';
import clientProfileData from './data/client_profile.json';

import type { ScheduledEvent, Activity, ClientProfile, DayData } from './types';
import { Sidebar } from './components/Sidebar';
import { Agenda } from './components/Agenda';

// Cast JSON to TS Types
const scheduleList = rawData as ScheduledEvent[];
const actionPlan = actionPlanData as unknown as Activity[];
const clientProfile = clientProfileData as unknown as ClientProfile;

function App() {
  const [sidebarOpen, setSidebarOpen] = useState(false);
  const [dayOffset, setDayOffset] = useState(0);

  // Group events by day
  const allDays = useMemo(() => {
    const map = new Map<string, DayData>();
    
    scheduleList.forEach(event => {
      const date = new Date(event.start);
      const dateKey = `${date.getFullYear()}-${date.getMonth()+1}-${date.getDate()}`;
      
      if (!map.has(dateKey)) {
        map.set(dateKey, {
          dateObj: date,
          dateStr: dateKey,
          events: []
        });
      }
      map.get(dateKey)!.events.push(event);
    });

    Array.from(map.values()).forEach(day => {
      day.events.sort((a, b) => new Date(a.start).getTime() - new Date(b.start).getTime());
    });

    return Array.from(map.values()).sort((a, b) => a.dateObj.getTime() - b.dateObj.getTime());
  }, []);

  const totalDays = allDays.length;
  const currentDays = allDays.slice(dayOffset, dayOffset + 3);

  return (
    <div className="app-container">
      <Sidebar 
        isOpen={sidebarOpen} 
        onClose={() => setSidebarOpen(false)} 
        actionPlan={actionPlan} 
      />

      <div className="main-content">
        <header className="header">
          <div className="header-top">
            <button className="toggle-btn" onClick={() => setSidebarOpen(true)}>
              &#9776; View Action Plan
            </button>
          </div>
          <h1>HealthSpan Agenda</h1>
          <p>Your AI-Optimized Longevity Schedule</p>
          
          <div className="pagination">
            <button 
              disabled={dayOffset === 0} 
              onClick={() => setDayOffset(d => Math.max(0, d - 3))}
            >
              &larr; Previous
            </button>
            <span>Viewing Days {dayOffset + 1}-{Math.min(dayOffset + 3, totalDays)} of {totalDays}</span>
            <button 
              disabled={dayOffset >= totalDays - 3} 
              onClick={() => setDayOffset(d => Math.min(totalDays - 3, d + 3))}
            >
              Next &rarr;
            </button>
          </div>
        </header>

        <Agenda 
          currentDays={currentDays} 
          clientProfile={clientProfile} 
        />
      </div>
    </div>
  );
}

export default App;
