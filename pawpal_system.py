"""PawPal+ system skeleton.

Class stubs generated from the initial UML design (diagrams/uml.mmd).
No logic yet — attributes and empty method stubs only.
"""

from dataclasses import dataclass, field # for "@" decorator and helper for defaults

# field: config tool of data classes; used to customize how an individual variable behaves

@dataclass  # help skip writing def __init__(self, name, ...)
class Owner:
    """Holds the owner's basic info and preferences."""

    name: str
    preferences: str = ""


@dataclass
class Pet:
    """Represents the animal the tasks are for."""

    name: str
    species: str = ""


@dataclass
class Task:
    """Describes one care task that needs to happen."""

    title: str
    duration_minutes: int
    priority: str


@dataclass
class Plan:
    """Holds the final ordered list of scheduled tasks and the explanation."""

    tasks: list[Task] = field(default_factory=list) # new empty for each plan, no sharing
    reasoning: str = ""


class Scheduler: # hold no data, just do work
    """Logic class: takes tasks plus constraints and produces a Plan."""

    def generate_plan(self, tasks: list[Task], available_minutes: int) -> Plan:
        """Sort tasks, drop what does not fit, assign order, build reasoning."""
        raise NotImplementedError 
