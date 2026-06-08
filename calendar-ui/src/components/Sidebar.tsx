import React from 'react';
import type { Activity } from '../types';

interface SidebarProps {
  isOpen: boolean;
  onClose: () => void;
  actionPlan: Activity[];
}

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

export const Sidebar: React.FC<SidebarProps> = ({ isOpen, onClose, actionPlan }) => {
  return (
    <div className={`sidebar glass ${isOpen ? 'open' : ''}`}>
      <div className="sidebar-header">
        <h2>Client Action Plan</h2>
        <button onClick={onClose}>&times;</button>
      </div>
      <div className="sidebar-content">
        <p className="sidebar-subtitle">Priority Ordered Activities ({actionPlan.length})</p>
        {actionPlan.map((act) => (
          <div key={act.id} className={`action-card ${act.type}`}>
            <div className="ac-header">
              <span className={`badge ${act.type}`}>{getTypeLabel(act.type)}</span>
              <span className="ac-priority">Pri: {act.priority}</span>
            </div>
            <h4>{act.name}</h4>
            <p className="ac-freq">{act.frequency} &bull; {act.duration_minutes} min</p>
            {act.backup_activities && act.backup_activities.length > 0 && (
              <p className="ac-backup">Has {act.backup_activities.length} backups</p>
            )}
          </div>
        ))}
      </div>
    </div>
  );
};
