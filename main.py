"""Temporary testing ground for the PawPal+ system.

Verifies that the data classes in pawpal_system.py behave as expected by
building a small owner/pet/task setup and printing a schedule to the terminal.

This script builds the schedule directly from ScheduledTask objects with
hand-picked times. To exercise the real scheduling pipeline instead, call
Scheduler().generate_plan(owner, constraints).
"""

from pawpal_system import (
    Frequency,
    Owner,
    Pet,
    Priority,
    ScheduledTask,
    Task,
)


def build_owner() -> Owner:
    """Create one owner with two pets, each carrying a couple of tasks."""
    # --- Pet 1: a dog with morning and evening care ---
    rex = Pet(name="Rex", species="dog")
    rex.tasks.append(
        Task(
            title="Morning walk",
            duration_minutes=30,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
        )
    )
    rex.tasks.append(
        Task(
            title="Evening feeding",
            duration_minutes=15,
            priority=Priority.HIGH,
            frequency=Frequency.DAILY,
        )
    )

    # --- Pet 2: a cat with a midday task ---
    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.tasks.append(
        Task(
            title="Litter box cleaning",
            duration_minutes=10,
            priority=Priority.MEDIUM,
            frequency=Frequency.DAILY,
        )
    )

    return Owner(name="May", preferences="mornings preferred", pets=[rex, whiskers])


def build_schedule(owner: Owner) -> list[ScheduledTask]:
    """Assign a start time to each pet's tasks (different times per task)."""
    # Map each task to a time that matches when it should happen, so a
    # "Morning" task lands in the morning and an "Evening" task in the evening.
    # (Real time assignment will live in Scheduler.assign_slots once wired in.)
    start_times = {
        "Morning walk": "08:00",
        "Litter box cleaning": "12:30",
        "Evening feeding": "18:00",
    }

    schedule: list[ScheduledTask] = []
    for pet in owner.pets:
        for task in pet.tasks:
            start = start_times.get(task.title, "08:00")
            schedule.append(
                ScheduledTask(
                    task=task,
                    start_time=start,
                    reason=f"{task.priority.name} priority task for {pet.name}",
                )
            )

    # Sort by start time so the schedule reads top-to-bottom by clock.
    schedule.sort(key=lambda scheduled: scheduled.start_time)
    return schedule


def print_schedule(owner: Owner, schedule: list[ScheduledTask]) -> None:
    """Print a human-readable 'Today's Schedule' to the terminal."""
    print("=" * 40)
    print(f"Today's Schedule for {owner.name}")
    print("=" * 40)

    for scheduled in schedule:
        task = scheduled.task
        print(f"{scheduled.start_time} - {task.title} ({task.duration_minutes} min)")
        print(f"           why: {scheduled.reason}")

    total_minutes = sum(s.task.duration_minutes for s in schedule)
    print("-" * 40)
    print(f"{len(schedule)} tasks, {total_minutes} minutes total")


def main() -> None:
    owner = build_owner()
    schedule = build_schedule(owner)
    print_schedule(owner, schedule)


if __name__ == "__main__":
    main()
