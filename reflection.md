# PawPal+ Project Reflection

## 1. System Design

User should be able to:
- enter basic owner & pet info
- add & edit care tasks (duration + priority)
- trigger plan generation & view the result (with reasoning)

**a. Initial design**

- Briefly describe your initial UML design.

    - My initial UML design had five classes: four data-holding classes (Owner, Pet, Task, and Plan) plus one logic class (Scheduler). I split data from logic so that what gets scheduled stays separate from how it gets decided, keeping each class focused on one responsibility. The classes connect as: Owner has Pet, Pet has Tasks, the Scheduler takes Tasks and produces a Plan, and the Plan orders Tasks (all shown as associations in the diagram).

- What classes did you include, and what responsibilities did you assign to each?

    - **Owner** — holds the owner's basic info (name) and preferences. Responsible for storing who is planning the care.
    - **Pet** — holds the pet's info (name, species). Responsible for representing the animal the tasks are for.
    - **Task** — holds a single care task's data (title, duration in minutes, priority). Responsible for describing one thing that needs to happen.
    - **Scheduler** — the logic class. Takes a list of tasks plus constraints (time available, priority) and produces a Plan. Responsible for sorting tasks by priority, dropping tasks when time runs out, assigning time slots, and building the reasoning.
    - **Plan** — holds the final ordered list of scheduled tasks and the explanation. Responsible for representing the finished daily schedule that gets displayed.
    
**b. Design changes**

- Did your design change during implementation?

    - Yes. Reviewing the skeleton against the README showed the initial four data classes were not enough, so the design grew to satisfy the requirements more fully.

- If yes, describe at least one change and why you made it.

    - **Added a ScheduledTask class.** A plain Task had no start time, so it could not produce output like "08:00 — Morning walk." ScheduledTask wraps a Task with a `start_time` and a per-task `reason`.
    - **Introduced Priority and Frequency enums.** Priority was a plain string (typo-prone and not sortable) and there was no way to express recurring tasks. Enums lock the values and make priority sortable, and Frequency covers daily/weekly tasks from the README.
    - **Grouped constraints into a Constraints class.** The scheduler originally took only `available_minutes`, which ignored the day window and owner preferences the README calls for.
    - **Gave Owner an `all_tasks()` method and changed `generate_plan` to take the Owner.** Tasks live two levels deep (Owner → Pet → Task), so the Owner now flattens them and the Scheduler retrieves across pets instead of being handed a raw list.
    - **Added a `completed` flag to Task and split `generate_plan` into helper methods** (`filter_by_frequency`, `sort_tasks`, `filter_by_time`, `assign_slots`, `resolve_conflicts`, `build_reasoning`) so each scheduling behavior is small and testable, matching the README's "Smarter Scheduling" table.

    - **Refined the relationship arrow types.** I changed the plain associations to more specific UML relationships with multiplicity to reflect real-world life-cycles: composition for Pet→Task and Plan→ScheduledTask (the part dies with the whole), aggregation for Owner→Pet and ScheduledTask→Task (the part can outlive the whole — a pet can change owners, a Task exists independently of any one schedule), and dependency for Scheduler→Owner/Constraints/Plan (used in a method, not stored). The connections also changed: `Plan` now contains `ScheduledTask` (which wraps `Task`), and `Scheduler` reads tasks from the Owner rather than the Plan ordering Tasks directly.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?

    - The `Constraints` class carries several fields, but the scheduler currently acts on three of them: the total time available (`available_minutes`), the day the plan is for (`weekday`), and when the day begins (`day_start`). Two more fields — `day_end` and owner `preferences` — are carried for future use but not yet read by the scheduler. Each task also carries a `Priority` (LOW/MEDIUM/HIGH), used to *order* tasks; a `Frequency` (once/daily/weekly) with an optional `weekday`, used to *filter* which tasks are due on the planned day; and an optional `due_time`, used to *place* the task at a preferred clock time.

- How did you decide which constraints mattered most?

    - Time is treated as a hard limit and priority as the ranker. The scheduler sorts tasks by priority first, then drops lower-priority tasks once the time budget runs out (`filter_by_time`). I chose this because the scenario is a busy owner: fitting the day is non-negotiable, so time gates *whether* a task happens, while priority decides *which* tasks survive when everything cannot fit.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

    - When the day is full, the scheduler drops whole tasks rather than shortening them or squeezing everything in. It also fills strictly by priority order, so a long low-priority task can be dropped even if a shorter one would have fit in the leftover time.

- Why is that tradeoff reasonable for this scenario?

    - For a busy pet owner, a realistic plan that fits the day beats an overloaded one that cannot actually be followed. Dropping by priority keeps the most important care (meds, feeding) guaranteed, and favoring simple priority order over optimal time-packing keeps the plan easy to explain — which matters because the README asks the app to justify why it chose the plan.

**c. Where my design differs from the suggested approach (and why)**

The project instructions suggested a few specific implementations. I deliberately built some of them differently because the alternatives fit a stateless, single-day planner better. Each choice was a judgment call, not an oversight:

- **Recurrence — day-matching filter instead of "spawn the next instance."** The suggestion was that completing a daily/weekly task should auto-create a new instance for the next date using `timedelta`. That assumes a persistent calendar and stored dates across sessions, which this app does not have (there is no database — state lives only in the current Streamlit session). Instead, each weekly task stores the weekday it fires on, and `filter_by_frequency` asks a simpler, stateless question: "is this task due on the day I'm planning for?" It directly answers what the scheduler needs, avoids inventing a date store, and still lets the user control exactly which day each weekly task recurs (weekly-Tuesday vs weekly-Thursday).

- **Conflicts — resolve and detect, instead of only warn.** The suggestion was a lightweight check that returns a warning rather than crashing. I kept a detection method (`detect_conflicts`, which returns warnings and never mutates) but also added `resolve_conflicts`, which repairs overlaps by pushing a task to start when the previous one ends. For a busy owner, a plan that fixes itself is more useful than one that only complains, and offering both means a caller can choose to report or repair. This is a superset of the suggestion, not a departure from it.

- **Sorting — by priority, not by clock time.** The suggestion was to sort tasks by a time attribute. The user enters a task's *duration* (how long it takes) and may give an optional preferred `due_time`, but most tasks have no fixed start time — the scheduler assigns those itself in `assign_slots` (placing a task at its `due_time` when given, otherwise back to back from the start of the day). So there is generally no clock time to sort by: a task without a preferred time only gets an "08:00" after scheduling, not before. The meaningful decision is *which* tasks win when the day is tight, so `sort_tasks` ranks by priority and uses duration only as a tiebreaker (equal priority → shorter task first). Clock-time ordering is an output of scheduling, not an input to it.

The common thread: the scenario is a one-day planner with no persistent backend, so I preferred stateless, explainable logic over machinery (stored dates, future instances) that only pays off with a real calendar behind it.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?

    - I used AI across the whole design and brainstorming phase: checking my requirements against the README (it caught that I was missing "display the plan and reasoning" as a core action), brainstorming which objects/classes to include and why, and explaining concepts I was unfamiliar with (enums, the Scheduler's role, Python dataclasses, `field()`, and the different UML arrow types). I then had it turn my UML into Python class stubs, review that skeleton against the README to find gaps (missing start time, relationships, completion status, conflict handling), and apply the fixes one at a time. I also used it to keep my UML diagram and reflection in sync with the code and to debug a Mermaid parse error.

- What kinds of prompts or questions were most helpful?

    - The most useful prompts asked the AI to "verify against the README" instead of trusting its own guess, to "explain a concept before applying it", to make changes "one at a time" so I could follow each, and to "show me the code in chat before writing it to a file". Checklists ("does the system satisfy these four classes?") were also helpful because they forced a clear yes/no per item instead of a vague summary.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

    - When I asked for the UML diagram, the AI generated it and wrote it straight to the `uml.mmd` file. I did not accept that — I had it undo the change and show me the code in the chat first so I could read and understand it before it touched my files. Reviewing it first let me confirm the classes and relationships matched what I actually intended.

- How did you evaluate or verify what the AI suggested?

    - I evaluated suggestions by reading them before applying, by asking the AI to justify them against the README rather than take its word, and by using checklists to confirm each requirement was met. When something looked too strong or off (for example the arrow types), I reasoned about the real-world scenario myself and chose the option that fit rather than accepting the first suggestion.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?

    - I wrote eight pytest tests in `tests/test_pawpal.py`, one per key behavior:
      - `mark_complete` flips a task's `completed` flag.
      - `add_task` grows a pet's task list by one.
      - `filter_by_frequency` includes daily tasks every day, weekly tasks only on their own weekday, and drops once-tasks that are already completed.
      - `sort_tasks` orders by priority first and uses shorter duration as the tiebreaker.
      - `filter_by_time` keeps tasks while the time budget lasts and skips ones that would overflow.
      - `resolve_conflicts` pushes an overlapping slot forward so it starts when the previous task ends.
      - `detect_conflicts` reports overlapping slots as warnings and reports none for a clean plan.
      - `generate_plan` honors a task's preferred `due_time`, and when two preferred times clash it reports a warning and pushes the later task apart.

- Why were these tests important?

    - These are the actual algorithmic decisions the scheduler makes (the parts most likely to break silently if I refactor). Sorting, time-filtering, recurrence, and conflict handling are exactly the "Smarter Scheduling" features, so locking them with tests means a future change can't quietly change the plan without a test going red.

**b. Confidence**

- How confident are you that your scheduler works correctly?

    - Fairly confident for the core logic: the eight tests pass, and running `python main.py` produces a sensible Tuesday plan across two pets (including the weekly vet visit, which correctly disappears on other days). I also verified the Streamlit UI end-to-end using Streamlit's `AppTest` harness, which caught a real bug: `st.selectbox` returns a copy of an object option, so adding a task mutated a throwaway pet and nothing was saved. I fixed it by selecting the pet by index and looking it up in the live list, then re-ran the harness to confirm the task persisted.

- What edge cases would you test next if you had more time?

    - An empty plan (no tasks, or none fit the time budget), tasks with equal priority and equal duration, a weekly task whose day never matches, and the day-window (`day_start`/`day_end`) actually bounding the schedule — right now `assign_slots` can run past `day_end`.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

    - Splitting data from logic and breaking `generate_plan` into small, single-purpose helpers. That made each scheduling behavior easy to test in isolation and easy to explain, and it made the recurring-task feature a clean one-method addition (`filter_by_frequency`) instead of a rewrite.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

    - **Plan the whole week at once.** Right now each run plans a single chosen weekday, so weekly-Tuesday and weekly-Thursday tasks only show when you generate their day. I would add a "plan the week" view that loops `generate_plan` over Monday–Sunday and shows all seven days together, so the user sees the full week without regenerating for each day.
    - **Smarter placement around due times.** `assign_slots` now honors a task's preferred `due_time`, but when two clash it simply pushes the later one to the end of the earlier one. I would explore shifting the *lower-priority* task instead of always the later one, and warning when a preferred time falls outside the `day_start`–`day_end` window.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

    - Verifying behavior beats trusting that code "looks right." The selectbox bug looked correct on the page and raised no error, but driving the app with a test harness proved the data never persisted. Asking the AI to reproduce the bug end-to-end instead of guessing at it is what actually found the root cause.
