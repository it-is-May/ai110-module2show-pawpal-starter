"""PawPal+ system: domain classes and the Scheduler that builds a daily Plan.

"""

from dataclasses import dataclass, field
from enum import Enum


class Priority(Enum):
    """Fixed set of task priorities. Numeric values allow sorting."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


class Frequency(Enum):
    """How often a task repeats."""

    ONCE = "once"
    DAILY = "daily"
    WEEKLY = "weekly"


@dataclass
class Task:
    """Describes one care task that needs to happen."""

    title: str
    duration_minutes: int
    priority: Priority
    frequency: Frequency = Frequency.DAILY
    completed: bool = False

    def mark_complete(self) -> None:
        """Mark this task as done."""
        self.completed = True


@dataclass
class Pet:
    """Represents the animal the tasks are for."""

    name: str
    species: str = ""
    tasks: list[Task] = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Attach a task to this pet."""
        self.tasks.append(task)


@dataclass
class Owner:
    """Holds the owner's basic info and preferences."""

    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)

    def all_tasks(self) -> list[Task]:
        """Flatten and return the tasks from every pet."""
        tasks: list[Task] = []
        for pet in self.pets:
            tasks.extend(pet.tasks)
        return tasks


@dataclass
class ScheduledTask:
    """A Task assigned a start time in the plan, plus why it was chosen."""

    task: Task
    start_time: str  # "HH:MM", enables the "08:00 - Morning walk" output
    reason: str = ""  # per-task explanation


@dataclass
class Constraints:
    """The limits the scheduler must respect for a given day."""

    available_minutes: int
    day_start: str = "08:00"  # when the day begins
    day_end: str = "20:00"  # when the day ends
    preferences: str = ""  # owner preferences feed the scheduler


@dataclass
class Plan:
    """Holds the final ordered scheduled tasks and the overall explanation."""

    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)
    reasoning: str = ""


class Scheduler:
    """Logic class: takes tasks plus constraints and produces a Plan."""

    def generate_plan(self, owner: Owner, constraints: Constraints) -> Plan:
        """Retrieve owner's tasks, then sort, filter, place, resolve, explain."""
        tasks = owner.all_tasks()
        tasks = self.sort_tasks(tasks)
        tasks = self.filter_by_time(tasks, constraints.available_minutes)
        scheduled = self.assign_slots(tasks, constraints.day_start)
        scheduled = self.resolve_conflicts(scheduled)
        reasoning = self.build_reasoning(scheduled)
        return Plan(scheduled_tasks=scheduled, reasoning=reasoning)

    def sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (and duration as a tiebreaker).

        Highest priority first; for equal priority, shorter tasks first.
        """
        return sorted(
            tasks,
            key=lambda task: (-task.priority.value, task.duration_minutes),
        )

    def filter_by_time(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Drop tasks that do not fit in the remaining time budget.

        Walks the (priority-sorted) tasks and greedily keeps each one that
        still fits, skipping any that would overflow. A too-big high-priority
        task is skipped rather than blocking the smaller tasks behind it, so
        the day fills with high-impact work first but still packs in easy
        wins without exceeding the time limit.
        """
        kept: list[Task] = []
        remaining = available_minutes
        for task in tasks:
            if task.duration_minutes <= remaining:
                kept.append(task)
                remaining -= task.duration_minutes
        return kept

    def assign_slots(
        self, tasks: list[Task], day_start: str
    ) -> list[ScheduledTask]:
        """Give each kept task a start time, back to back from day_start.

        Starts the clock at day_start ("HH:MM") and places each task right
        after the previous one, advancing the clock by that task's duration.
        """
        scheduled: list[ScheduledTask] = []
        current = self._to_minutes(day_start)
        for task in tasks:
            scheduled.append(
                ScheduledTask(
                    task=task,
                    start_time=self._to_hhmm(current),
                    reason=f"{task.priority.name} priority, {task.duration_minutes} min",
                )
            )
            current += task.duration_minutes
        return scheduled

    @staticmethod
    def _to_minutes(hhmm: str) -> int:
        """Convert 'HH:MM' into minutes since midnight."""
        hours, minutes = hhmm.split(":")
        return int(hours) * 60 + int(minutes)

    @staticmethod
    def _to_hhmm(total_minutes: int) -> str:
        """Convert minutes since midnight back into 'HH:MM'."""
        return f"{total_minutes // 60:02d}:{total_minutes % 60:02d}"

    def resolve_conflicts(
        self, scheduled: list[ScheduledTask]
    ) -> list[ScheduledTask]:
        """Detect and fix overlapping time slots.

        Walks the slots in order; if a task would start before the previous
        one ends, it is pushed forward to begin exactly when the previous
        task finishes. Back-to-back slots from assign_slots never overlap, so
        this mainly guards against manually placed or edited times.
        """
        fixed: list[ScheduledTask] = []
        prev_end = None
        for slot in scheduled:
            start = self._to_minutes(slot.start_time)
            if prev_end is not None and start < prev_end:
                start = prev_end
                slot = ScheduledTask(
                    task=slot.task,
                    start_time=self._to_hhmm(start),
                    reason=slot.reason,
                )
            fixed.append(slot)
            prev_end = start + slot.task.duration_minutes
        return fixed

    def build_reasoning(self, scheduled: list[ScheduledTask]) -> str:
        """Produce the human-readable explanation for the plan.

        Summarizes how many tasks were placed, the total time they take, and
        why the order looks the way it does (highest priority first).
        """
        if not scheduled:
            return "No tasks fit the available time, so the plan is empty."

        total = sum(slot.task.duration_minutes for slot in scheduled)
        lines = [
            f"Planned {len(scheduled)} task(s) taking {total} minutes total, "
            "ordered by priority (highest first) to do high-impact care early."
        ]
        for slot in scheduled:
            lines.append(
                f"  {slot.start_time} - {slot.task.title} "
                f"[{slot.task.priority.name.lower()}] ({slot.task.duration_minutes} min)"
            )
        return "\n".join(lines)
