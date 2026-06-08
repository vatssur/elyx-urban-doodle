# Guidelines for AI Coding Agents

When editing or extending this codebase, adhere strictly to the following architectural decisions and coding standards:

## 1. Strict Type Safety (Python & TypeScript)
*   **Python**: All core data structures must be defined in `models.py` using `@dataclass`. 
*   **Enums**: Always use `str`-based Enums for categorical data (`class ActivityType(str, Enum)`). Never perform raw string comparisons (e.g., `if type == "FOOD":`). Instead, use the Enum: `if type == ActivityType.FOOD_CONSUMPTION:`.
*   **TypeScript**: The frontend must exclusively use `.tsx`/`.ts` files. The `types.ts` file in the React app must perfectly mirror the Python models. Always use `import type { ... }` when importing interfaces in Vite.

## 2. Reusable UI Components
*   **No Monoliths**: Do not dump code into a massive `App.tsx`. 
*   **Component Modularity**: Break down complex UIs into highly focused, reusable components (e.g., `Sidebar.tsx`, `DayCard.tsx`). Pass props explicitly.

## 3. The Scheduler Philosophy
*   **Dynamic, Not Rigid**: The `scheduler.py` engine must remain a dynamic allocator. Do not hardcode specific times for low-priority activities. Allow the priority-based `check_overlap` logic to dynamically find open slots.
*   **Human Constraints**: Respect the human element. The scheduler must enforce transit buffers, explicit sleep blocks, and work hours. Do not schedule events back-to-back if they have different physical locations without padding the transit time.

## 4. Source of Truth
*   `templates.json` is the sole source of truth for raw activity definitions.
*   Do not hardcode new activity logic directly into `scheduler.py`. If a new behavior is needed, add a constraint flag (like `remote_capable` or `energy_cost`) to the Python dataclass and `templates.json`, and program the scheduler to react to that flag.
