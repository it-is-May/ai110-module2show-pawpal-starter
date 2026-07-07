"""Quick tests for the most important PawPal+ behaviors."""

from pawpal_system import (
    Constraints,
    Frequency,
    Owner,
    Pet,
    Priority,
    ScheduledTask,
    Scheduler,
    Task,
)


def test_mark_complete_changes_status():
    """Task Completion: mark_complete() flips completed False -> True."""
    task = Task(title="Morning walk", duration_minutes=30, priority=Priority.HIGH)
    assert task.completed is False

    task.mark_complete()

    assert task.completed is True


def test_adding_task_increases_pet_task_count():
    """Task Addition: adding a task to a Pet grows its task list by one."""
    pet = Pet(name="Rex", species="dog")
    assert len(pet.tasks) == 0

    pet.add_task(Task(title="Feeding", duration_minutes=15, priority=Priority.HIGH))

    assert len(pet.tasks) == 1


def test_filter_by_frequency_picks_the_right_tasks_for_the_day():
    """Recurrence: daily always shows, weekly only on its day, done-once drops."""
    daily = Task("Walk", 30, Priority.HIGH, frequency=Frequency.DAILY)
    weekly_tue = Task(
        "Vet", 45, Priority.HIGH, frequency=Frequency.WEEKLY, weekday="Tuesday"
    )
    once_done = Task("Nails", 10, Priority.LOW, frequency=Frequency.ONCE)
    once_done.mark_complete()

    tasks = [daily, weekly_tue, once_done]
    scheduler = Scheduler()

    # On Tuesday: daily + the weekly-Tuesday task; the completed once-task is gone.
    assert scheduler.filter_by_frequency(tasks, "Tuesday") == [daily, weekly_tue]

    # On Monday: only the daily task; weekly-Tuesday is not due today.
    assert scheduler.filter_by_frequency(tasks, "Monday") == [daily]


def test_sort_tasks_orders_by_priority_then_duration():
    """Sorting: highest priority first; for a tie, the shorter task wins."""
    low = Task("Brush", 10, Priority.LOW)
    high_long = Task("Walk", 45, Priority.HIGH)
    high_short = Task("Feed", 15, Priority.HIGH)

    ordered = Scheduler().sort_tasks([low, high_long, high_short])

    # Both HIGH tasks come before the LOW one; shorter HIGH task leads.
    assert ordered == [high_short, high_long, low]


def test_filter_by_time_drops_tasks_that_do_not_fit():
    """Filtering: keep tasks while budget lasts, skip ones that overflow."""
    a = Task("A", 30, Priority.HIGH)
    b = Task("B", 45, Priority.HIGH)  # would overflow the 60-min budget
    c = Task("C", 20, Priority.HIGH)  # still fits after A (30 + 20 <= 60)

    kept = Scheduler().filter_by_time([a, b, c], available_minutes=60)

    assert kept == [a, c]


def test_resolve_conflicts_pushes_overlaps_forward():
    """Conflict handling: an overlapping slot starts when the previous one ends."""
    first = ScheduledTask(task=Task("Walk", 30, Priority.HIGH), start_time="08:00")
    # Starts at 08:15 but the first task runs until 08:30 -> must be pushed.
    second = ScheduledTask(task=Task("Feed", 15, Priority.HIGH), start_time="08:15")

    fixed = Scheduler().resolve_conflicts([first, second])

    assert fixed[0].start_time == "08:00"
    assert fixed[1].start_time == "08:30"


def test_detect_conflicts_reports_overlaps():
    """Conflict detection: overlapping slots produce a warning, clean ones don't."""
    scheduler = Scheduler()
    walk = ScheduledTask(task=Task("Walk", 30, Priority.HIGH), start_time="08:00")
    # Starts at 08:15 but Walk runs until 08:30 -> overlap.
    feed = ScheduledTask(task=Task("Feed", 15, Priority.HIGH), start_time="08:15")

    warnings = scheduler.detect_conflicts([walk, feed])
    assert len(warnings) == 1
    assert "Feed" in warnings[0] and "Walk" in warnings[0]

    # Non-overlapping slots produce no warnings.
    later = ScheduledTask(task=Task("Feed", 15, Priority.HIGH), start_time="09:00")
    assert scheduler.detect_conflicts([walk, later]) == []


def test_generate_plan_places_due_times_and_reports_clashes():
    """due_time placement: preferred times are honored, and an overlap is
    reported as a warning and then pushed apart in the final plan."""
    owner = Owner(name="May")
    pet = Pet(name="Rex")
    owner.add_pet(pet)
    # Both want 08:00-ish; Walk (30 min) and Feed (10 min) collide.
    pet.add_task(Task("Walk", 30, Priority.HIGH, due_time="08:00"))
    pet.add_task(Task("Feed", 10, Priority.HIGH, due_time="08:10"))

    plan = Scheduler().generate_plan(
        owner, Constraints(available_minutes=120, weekday="Monday")
    )

    # The clash is reported...
    assert len(plan.warnings) == 1
    assert "Feed" in plan.warnings[0]
    # ...and the final plan has no overlap: Feed is pushed to when Walk ends.
    starts = {s.task.title: s.start_time for s in plan.scheduled_tasks}
    assert starts["Walk"] == "08:00"
    assert starts["Feed"] == "08:30"
