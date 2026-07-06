"""PawPal+ system skeleton.

Class stubs generated from the initial UML design (diagrams/uml.mmd) and
refined to close relationship, data, and logic gaps found during review.
No scheduling logic yet — attributes and empty method stubs only.
"""

from dataclasses import dataclass, field
from enum import Enum


# --- Fix 5: Priority as enum (no more typo-prone plain strings, and sortable) ---
class Priority(Enum):
    """Fixed set of task priorities. Numeric values allow sorting."""

    LOW = 1
    MEDIUM = 2
    HIGH = 3


# --- Fix 7: Recurring tasks (README names daily vs weekly) ---
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
    priority: Priority  # Fix 5: was str
    frequency: Frequency = Frequency.DAILY  # Fix 7: recurring support
    completed: bool = False  # Fix 11: track completion status


@dataclass
class Pet:
    """Represents the animal the tasks are for."""

    name: str
    species: str = ""
    tasks: list[Task] = field(default_factory=list)  # Fix 1/2: Pet owns its Tasks


@dataclass
class Owner:
    """Holds the owner's basic info and preferences."""

    name: str
    preferences: str = ""
    pets: list[Pet] = field(default_factory=list)  # Fix 1: Owner has Pets

    # Fix 12: give the Scheduler one place to retrieve every pet's tasks
    def all_tasks(self) -> list[Task]:
        """Flatten and return the tasks from every pet."""
        raise NotImplementedError


# --- Fix 3: a Task placed at a specific time, with a per-task reason (Fix 10) ---
@dataclass
class ScheduledTask:
    """A Task assigned a start time in the plan, plus why it was chosen."""

    task: Task
    start_time: str  # "HH:MM", enables the "08:00 — Morning walk" output
    reason: str = ""  # Fix 10: per-task explanation, not one big blob


# --- Fix 6: constraints grouped in one object (time window + preferences) ---
@dataclass
class Constraints:
    """The limits the scheduler must respect for a given day."""

    available_minutes: int
    day_start: str = "08:00"  # Fix 6: when the day begins
    day_end: str = "20:00"  # Fix 6: when the day ends
    preferences: str = ""  # Fix 4: owner preferences feed the scheduler


@dataclass
class Plan:
    """Holds the final ordered scheduled tasks and the overall explanation."""

    scheduled_tasks: list[ScheduledTask] = field(default_factory=list)  # Fix 3
    reasoning: str = ""


class Scheduler:
    """Logic class: takes tasks plus constraints and produces a Plan."""

    # --- Fix 8: split the one fat method into focused, testable steps ---
    # Fix 13: take the Owner and retrieve tasks across pets via owner.all_tasks()
    def generate_plan(self, owner: Owner, constraints: Constraints) -> Plan:
        """Retrieve owner's tasks, then sort, filter, place, resolve, explain."""
        raise NotImplementedError

    def _sort_tasks(self, tasks: list[Task]) -> list[Task]:
        """Order tasks by priority (and duration as a tiebreaker)."""
        raise NotImplementedError

    def _filter_by_time(
        self, tasks: list[Task], available_minutes: int
    ) -> list[Task]:
        """Drop tasks that do not fit in the remaining time budget."""
        raise NotImplementedError

    def _assign_slots(
        self, tasks: list[Task], day_start: str
    ) -> list[ScheduledTask]:
        """Give each kept task a start time, back to back from day_start."""
        raise NotImplementedError

    # --- Fix 9: conflict handling (overlapping slots) ---
    def _resolve_conflicts(
        self, scheduled: list[ScheduledTask]
    ) -> list[ScheduledTask]:
        """Detect and fix overlapping time slots."""
        raise NotImplementedError

    def _build_reasoning(self, scheduled: list[ScheduledTask]) -> str:
        """Produce the human-readable explanation for the plan."""
        raise NotImplementedError
