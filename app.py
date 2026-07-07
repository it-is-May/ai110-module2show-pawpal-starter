import streamlit as st

from pawpal_system import (Owner, Pet, Task, Priority, Frequency, Constraints, Scheduler)

WEEKDAYS = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to **PawPal+**, a pet care planning assistant.

Enter an owner and their pets, add care tasks (with duration, priority, and how often they
recur), then generate a daily schedule. The plan is built by the `Scheduler` in
`pawpal_system.py`, which sorts and filters tasks across all pets and explains its choices.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")

# Create the Owner once with an empty name; the user fills it in on the app.
if "owner" not in st.session_state:
    st.session_state.owner = Owner(name="")

owner = st.session_state.owner

# Sync the owner name each rerun so editing the box actually renames the owner.
owner_name = st.text_input("Owner name", value=owner.name, placeholder="Type your name")
owner.name = owner_name

st.markdown("### Pets")
col_p1, col_p2 = st.columns(2)
with col_p1:
    pet_name = st.text_input("Pet name", placeholder="Type a pet name")
with col_p2:
    species_choice = st.selectbox("Species", ["dog", "cat", "other"])
# When the pet is neither dog nor cat, let the user type the species.
if species_choice == "other":
    species = st.text_input("Which species?", placeholder="e.g. rabbit, bird").strip()
else:
    species = species_choice

if st.button("Add pet"):
    clean_name = pet_name.strip()
    existing = {p.name.lower() for p in owner.pets}
    if not clean_name:
        st.warning("Enter a pet name first.")
    elif clean_name.lower() in existing:
        st.warning(f"A pet named '{clean_name}' already exists.")
    elif species_choice == "other" and not species:
        st.warning("Enter the species first.")
    else:
        owner.add_pet(Pet(name=clean_name, species=species))

if not owner.pets:
    st.info("No pets yet. Add one above to start adding tasks.")
    st.stop()

st.write("Current pets: " + ", ".join(f"{p.name} ({p.species})" for p in owner.pets))

st.markdown("### Tasks")
st.caption("Add tasks for each pet. They feed into the scheduler when you generate a plan below.")

# Select by index and look the pet up in the live list, so we mutate the
# real pet in session_state (Streamlit hands back a *copy* of an object option).
pet_index = st.selectbox(
    "Add task to which pet?",
    range(len(owner.pets)),
    format_func=lambda i: owner.pets[i].name,
)
pet = owner.pets[pet_index]

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", placeholder="Type a task")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

col4, col5, col6 = st.columns(3)
with col4:
    frequency = st.selectbox("Frequency", ["once", "daily", "weekly"], index=1)
with col5:
    # Only a weekly task needs a specific day; disabled otherwise.
    task_weekday = st.selectbox(
        "On which day?", WEEKDAYS, disabled=(frequency != "weekly")
    )
with col6:
    due_time = st.text_input("Preferred time (optional)", placeholder="e.g. 08:00")

if st.button("Add task"):
    clean_due = due_time.strip()
    if not task_title.strip():
        st.warning("Enter a task title first.")
    elif clean_due and not Scheduler._is_hhmm(clean_due):
        st.warning("Preferred time must look like 08:00 (24-hour HH:MM), or leave it blank.")
    else:
        pet.add_task(
            Task(
                title=task_title.strip(),
                duration_minutes=int(duration),
                priority=Priority[priority.upper()],
                due_time=clean_due,
                frequency=Frequency(frequency),
                weekday=task_weekday if frequency == "weekly" else "",
            )
        )

tasks = owner.all_tasks()
if tasks:
    st.write("Current tasks:")
    st.table(
        [
            {
                "pet": p.name,
                "title": t.title,
                "duration_minutes": t.duration_minutes,
                "priority": t.priority.name.lower(),
                "due_time": t.due_time,
                "frequency": t.frequency.value,
                "day": t.weekday,
            }
            for p in owner.pets
            for t in p.tasks
        ]
    )
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Runs the scheduler across all pets and shows the plan with its reasoning.")

col_s1, col_s2 = st.columns(2)
with col_s1:
    available_minutes = st.number_input(
        "Available minutes today", min_value=1, max_value=1440, value=120
    )
with col_s2:
    plan_weekday = st.selectbox("Plan for which day?", WEEKDAYS)

if st.button("Generate schedule"):
    constraints = Constraints(
        available_minutes=int(available_minutes), weekday=plan_weekday
    )
    plan = Scheduler().generate_plan(owner, constraints)

    if plan.scheduled_tasks:
        # Surface any preferred-time clashes the scheduler had to shuffle.
        for warning in plan.warnings:
            st.warning(warning)
        st.write("### Your plan")
        for slot in plan.scheduled_tasks:
            st.write(f"**{slot.start_time}** — {slot.task.title} ({slot.reason})")
        st.markdown("**Why this plan:**")
        st.text(plan.reasoning)
    else:
        st.info("No tasks fit the available time.")
