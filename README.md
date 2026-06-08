# HealthSpan Scheduler

HealthSpan Scheduler is a sophisticated, highly-dynamic scheduling engine designed to intelligently plan health, fitness, medical, and lifestyle activities around a user's biological constraints and travel schedules.

## Core Architecture

The architecture is split into two primary segments: the **Python Data Pipeline** and the **React/TypeScript Frontend**.

### 1. Python Data Pipeline (The Brain)
*   **`models.py`**: Defines strict datatypes (using `dataclass` and `Enum`) for `Activity`, `ScheduledEvent`, `ClientProfile`, etc. This ensures absolute type safety when generating and parsing data.
*   **`templates.json`**: A master list of highly diverse activities (e.g., VO2 Max Tests, Bouldering, Sleep Blocks). Activities hold constraints like `remote_capable`, `transit_time_minutes`, and `duration_minutes`.
*   **`data_generator.py`**: Reads `templates.json` and extrapolates a global pool of 150 activities. From there, it filters down to a perfectly deduplicated 25-item **Action Plan**. It guarantees core elements (Breakfast, Lunch, Dinner, Medications) exist.
*   **`scheduler.py`**: The dynamic scheduling engine. It reads the action plan and outputs the final `schedule.json`.

### 2. React + Vite Frontend (The UI)
*   Located in `calendar-ui/`, built with Vite, React, and TypeScript.
*   The UI relies heavily on modularized components (`App.tsx`, `Sidebar.tsx`, `Agenda.tsx`, `DayCard.tsx`) to render the calendar.
*   It visualizes explicit transit buffers, out-of-office travel banners, and strict sleep blocks.

---

## How the Scheduler Works

The `scheduler.py` engine is not a simple "place X at Y hour" script. It acts as an advanced, conflict-resolving allocator.

1.  **Sleep & Meals First**: The scheduler explicitly blocks out 8 hours of `SLEEP` every night (22:00 to 06:00). Then, it anchors Meals and Medications to fixed times so they are guaranteed to happen, even during "Break" adherence periods.
2.  **Priority-Based Sorting**: All remaining activities are sorted by their **Priority Level** (1 being highest, 10 being lowest).
3.  **Dynamic Slot Allocation**: The engine processes the highest priority items first. For each item, it searches the user's available window (06:00 - 22:00) for the first free slot that does **not** overlap with any existing scheduled items (including work hours).
4.  **Transit Buffers**: When checking for overlaps, the scheduler actively subtracts/adds the activity's `transit_time_minutes`. This guarantees the user has enough time to travel to/from the location without overlapping their next appointment.
5.  **Frequency Shifting**: If an activity requires 3 sessions a week (e.g., Monday, Wednesday, Friday), but Wednesday is entirely booked by higher-priority events, the scheduler will dynamically "flow" the activity into Thursday.
6.  **Remote Travel Constraints**: During travel periods, the engine checks the `remote_capable` flag. If an activity requires local physical equipment, it is cleanly skipped while the user is out of town.
