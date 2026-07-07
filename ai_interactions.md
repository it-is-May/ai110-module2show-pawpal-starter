# AI Interactions Log

> **Stretch features only.** Only fill in the sections that apply to stretch features you attempted. If you did not attempt a stretch feature, leave its section blank or delete it. This file is not required for the core project.

---

## Agent Workflow (SF7)

> Document your experience using an AI agent (e.g., Cursor Agent, Claude, Copilot) to make multi-step changes autonomously.

**What task did you give the agent?**

I used an AI agent (Claude Code) for several multi-step tasks: debug an import error in `app.py`; connect the Streamlit UI to the backend classes (owner, pet, and task creation, plus schedule generation); add recurring-task scheduling, conflict detection, and preferred-time (`due_time`) placement to the `Scheduler`; expand the pytest suite; and keep the README, reflection, and UML diagram in sync with the code.

**What did the agent do?**

- **`pawpal_system.py`** — added `filter_by_frequency` (recurrence), `detect_conflicts`, `due_time`-aware `assign_slots`, `Owner.add_pet`, and `Plan.warnings`.
- **`app.py`** — wired the whole UI to `Owner`/`Pet`/`Task`/`Scheduler`, added multi-pet support, a custom-species field, `due_time` input, and conflict warnings.
- **`main.py`** — rewrote the demo to run the real `generate_plan` pipeline across two pets.
- **`tests/test_pawpal.py`** — added six tests (recurrence, sorting, time-filtering, conflict detect/resolve, due-time), bringing the suite to eight.
- **`README.md`, `reflection.md`, `diagrams/uml.mmd`** — updated to match the code.
- It verified behavior by running `pytest` and by driving the Streamlit app headlessly with Streamlit's `AppTest` harness, which surfaced a real bug: `st.selectbox` returns a *copy* of an object option, so adding a task mutated a throwaway pet and nothing saved.

**What did you have to verify or fix manually?**

I reviewed each change before accepting it. I corrected a wrong assumption where I'd set `st.session_state.tasks = Task()` when it should stay a list; I flagged a Streamlit table layout issue with the raw `Task` objects; I rejected an awkward "(Already added since the first draft)" note the agent put in the reflection; and I made the agent re-check the actual `git log` before drafting commit messages, because its first drafts added multi-line bodies and a co-author trailer that didn't match my terse, single-line history. I also decided to keep my weekday-filter recurrence design rather than the suggested date-spawning approach, after weighing it against the app's stateless, single-day scope.

---

## Prompt Comparison (SF11)

> Compare two different prompts (or two different models) on the same task.

| | Option A | Option B |
|-|----------|----------|
| **Model / tool used** | | |
| **Prompt** | | |
| **Response summary** | | |
| **What was useful** | | |
| **Problems noticed** | | |
| **Decision** | | |

**Which approach did you use in your final implementation and why?**

<!-- Your conclusion -->
