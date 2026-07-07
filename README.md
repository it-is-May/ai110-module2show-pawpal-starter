# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## System Overview

The system lives in `pawpal_system.py` and splits **data** classes from the
**logic** class. The full class diagram is in [`diagrams/uml.mmd`](diagrams/uml.mmd).

| Class | Role |
|-------|------|
| `Owner` | The person planning care. Holds a name, preferences, and a list of pets. Methods: `add_pet`, `all_tasks` (flattens tasks across every pet). |
| `Pet` | An animal the tasks are for. Holds a name, species, and its own task list. Method: `add_task`. |
| `Task` | One care task: title, duration, `Priority`, an optional `due_time`, `Frequency`, an optional `weekday` (for weekly tasks), and a `completed` flag. Method: `mark_complete`. |
| `Scheduler` | The logic class. Takes an `Owner` plus `Constraints` and produces a `Plan` by filtering, sorting, placing, and explaining tasks across all pets. |
| `Constraints` | The limits for a day: available minutes, day window, and which `weekday` the plan is for. |
| `ScheduledTask` | A `Task` given a `start_time` and a per-task `reason`. |
| `Plan` | The finished result: an ordered list of `ScheduledTask`s plus an overall `reasoning` string. |
| `Priority` / `Frequency` | Enums for LOW/MEDIUM/HIGH and ONCE/DAILY/WEEKLY. |

The **algorithmic features** the `Scheduler` implements are documented in the
[Smarter Scheduling](#-smarter-scheduling) table below.


## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.

## 🖥️ Sample Output

Sample of the CLI output from running `python main.py`:

```
========================================
Tuesday's Schedule for May
========================================
08:00 - Evening feeding (15 min)
           why: HIGH priority, 15 min
08:15 - Morning walk (30 min)
           why: HIGH priority, 30 min
08:45 - Vet visit (45 min)
           why: HIGH priority, 45 min
09:30 - Litter box cleaning (10 min)
           why: MEDIUM priority, 10 min
----------------------------------------
4 tasks, 100 minutes total
```

`main.py` builds one owner (May) with two pets — Rex (dog) and Whiskers (cat) —
and four tasks, then runs the real scheduling pipeline (`Scheduler.generate_plan`)
for a Tuesday. The vet visit is a weekly-Tuesday task, so it appears here; on
other days it is filtered out.

## 🧪 Testing PawPal+

```bash
# Run the full test suite:
pytest

# Run with coverage:
pytest --cov
```

Sample test output:

```
============================= test session starts =============================
platform win32 -- Python 3.13.2, pytest-9.0.3, pluggy-1.6.0
configfile: pytest.ini
testpaths: tests
plugins: anyio-4.9.0
collected 8 items

tests/test_pawpal.py::test_mark_complete_changes_status PASSED           [ 12%]
tests/test_pawpal.py::test_adding_task_increases_pet_task_count PASSED   [ 25%]
tests/test_pawpal.py::test_filter_by_frequency_picks_the_right_tasks_for_the_day PASSED [ 37%]
tests/test_pawpal.py::test_sort_tasks_orders_by_priority_then_duration PASSED [ 50%]
tests/test_pawpal.py::test_filter_by_time_drops_tasks_that_do_not_fit PASSED [ 62%]
tests/test_pawpal.py::test_resolve_conflicts_pushes_overlaps_forward PASSED [ 75%]
tests/test_pawpal.py::test_detect_conflicts_reports_overlaps PASSED      [ 87%]
tests/test_pawpal.py::test_generate_plan_places_due_times_and_reports_clashes PASSED [100%]

============================== 8 passed in 0.12s ==============================
```

### Test coverage summary

The suite in `tests/test_pawpal.py` covers the most important behaviors:

| Test | What it verifies | Method under test |
|------|------------------|-------------------|
| `test_mark_complete_changes_status` | Completing a task flips its status | `Task.mark_complete` |
| `test_adding_task_increases_pet_task_count` | Adding a task grows the pet's list | `Pet.add_task` |
| `test_filter_by_frequency_picks_the_right_tasks_for_the_day` | Daily always shows, weekly only on its day, done-once drops | `Scheduler.filter_by_frequency` |
| `test_sort_tasks_orders_by_priority_then_duration` | Highest priority first; shorter wins ties | `Scheduler.sort_tasks` |
| `test_filter_by_time_drops_tasks_that_do_not_fit` | Tasks that overflow the time budget are skipped | `Scheduler.filter_by_time` |
| `test_resolve_conflicts_pushes_overlaps_forward` | Overlapping slots are pushed forward | `Scheduler.resolve_conflicts` |
| `test_detect_conflicts_reports_overlaps` | Overlaps are reported as warnings; clean plans report none | `Scheduler.detect_conflicts` |
| `test_generate_plan_places_due_times_and_reports_clashes` | Preferred times are honored; a clash is warned and pushed apart | `Scheduler.generate_plan` / `assign_slots` |

## 📐 Smarter Scheduling

The `Scheduler` implements these algorithmic features:

| Feature | Method(s) | Notes |
|---------|-----------|-------|
| Task sorting | `Scheduler.sort_tasks` | Highest priority first; shorter duration wins ties |
| Filtering | `Scheduler.filter_by_time` | Greedily keeps tasks that fit the time budget, skips ones that overflow |
| Time placement | `Scheduler.assign_slots` | Places a task at its preferred `due_time` when given, otherwise back to back |
| Conflict detection | `Scheduler.detect_conflicts` | Reports each overlapping slot as a warning (surfaced in the app), without changing the plan |
| Conflict handling | `Scheduler.resolve_conflicts` | Pushes any overlapping slot forward to start when the previous task ends |
| Recurring tasks | `Scheduler.filter_by_frequency` | Daily always; weekly only on the task's own weekday; once until completed |

## 📸 Demo Walkthrough

Run the Streamlit app with `streamlit run app.py`, then follow along:

1. **Enter the owner.** Type the owner's name at the top (e.g. "May"). It is stored once and persists as you navigate.
2. **Add pets.** Type a pet name, pick a species (or choose "other" and type a custom one like "rabbit"), and click **Add pet**. Duplicate names are rejected. Add as many pets as you like.
3. **Add tasks per pet.** Pick which pet the task is for, then enter a title, duration, priority, and frequency. For a **weekly** task, also choose the day it recurs (e.g. Vet visit → Tuesday). Click **Add task**; the task table updates with a row per task.
4. **Choose the day and time budget.** Under *Build Schedule*, set the available minutes and the weekday to plan for.
5. **Generate the schedule.** Click **Generate schedule**. The app runs `Scheduler.generate_plan` across all pets and shows each task with its start time and reason, plus an overall explanation. Weekly tasks appear only when their day matches the chosen weekday.

## Output & Formatting

The app uses Streamlit's built-in components for a readable layout (no `tabulate`
or ANSI library):

- **Structured task table** — the task list is rendered with `st.table`, expanded to columns for pet, title, duration, priority, due time, frequency, and day.
- **Color-coded status** — `st.warning` surfaces conflict messages and rejects invalid input; `st.info` marks empty states.
- **CLI schedule** — `main.py` prints an aligned schedule with `=`/`-` separators and a per-task reason line.
