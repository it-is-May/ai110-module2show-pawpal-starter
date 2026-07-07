"""Demo script for the PawPal+ system.

Builds one owner with two pets and several tasks, then runs the real
scheduling pipeline (Scheduler.generate_plan) and prints the resulting
daily plan to the terminal.
"""

from pawpal_system import (
    Constraints,
    Frequency,
    Owner,
    Pet,
    Plan,
    Priority,
    Scheduler,
    Task,
)


def build_owner() -> Owner:
    """Create one owner with two pets, each carrying a couple of tasks."""
    # --- Pet 1: a dog with morning and evening care ---
    rex = Pet(name="Rex", species="dog")
    rex.add_task(
        Task("Morning walk", 30, Priority.HIGH, frequency=Frequency.DAILY)
    )
    rex.add_task(
        Task("Evening feeding", 15, Priority.HIGH, frequency=Frequency.DAILY)
    )

    # --- Pet 2: a cat with a daily chore and a weekly vet visit ---
    whiskers = Pet(name="Whiskers", species="cat")
    whiskers.add_task(
        Task("Litter box cleaning", 10, Priority.MEDIUM, frequency=Frequency.DAILY)
    )
    whiskers.add_task(
        Task(
            "Vet visit",
            45,
            Priority.HIGH,
            frequency=Frequency.WEEKLY,
            weekday="Tuesday",
        )
    )

    owner = Owner(name="May", preferences="mornings preferred")
    owner.add_pet(rex)
    owner.add_pet(whiskers)
    return owner


def print_plan(owner: Owner, plan: Plan, weekday: str) -> None:
    """Print a human-readable 'Today's Schedule' to the terminal."""
    print("=" * 40)
    print(f"{weekday}'s Schedule for {owner.name}")
    print("=" * 40)

    for scheduled in plan.scheduled_tasks:
        task = scheduled.task
        print(f"{scheduled.start_time} - {task.title} ({task.duration_minutes} min)")
        print(f"           why: {scheduled.reason}")

    total_minutes = sum(s.task.duration_minutes for s in plan.scheduled_tasks)
    print("-" * 40)
    print(f"{len(plan.scheduled_tasks)} tasks, {total_minutes} minutes total")


def main() -> None:
    owner = build_owner()

    # Plan for a Tuesday so the weekly vet visit is included.
    weekday = "Tuesday"
    constraints = Constraints(available_minutes=120, weekday=weekday)

    scheduler = Scheduler()
    plan = scheduler.generate_plan(owner, constraints)

    print_plan(owner, plan, weekday)


if __name__ == "__main__":
    main()
