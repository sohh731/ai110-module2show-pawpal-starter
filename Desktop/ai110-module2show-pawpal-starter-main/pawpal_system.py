# pawpal_system.py
# Core model classes for PawPal+ pet care scheduler

from __future__ import annotations
from dataclasses import dataclass, field
from typing import List, Optional, Tuple


@dataclass
class Owner:
    name: str
    daily_time_available: int  # minutes
    preferences: List[str] = field(default_factory=list)

    def set_daily_time(self, minutes: int) -> None:
        self.daily_time_available = minutes

    def add_preference(self, preference: str) -> None:
        self.preferences.append(preference)

    def can_schedule(self, duration: int) -> bool:
        return duration <= self.daily_time_available


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""

    def update_health_notes(self, notes: str) -> None:
        self.health_notes = notes

    def birthday(self) -> None:
        self.age += 1

    def get_summary(self) -> str:
        return f"{self.name} ({self.species}, {self.age} yrs): {self.health_notes}"


@dataclass
class Task:
    title: str
    category: str
    duration: int  # minutes
    priority: int  # higher means more important
    notes: str = ""
    completed: bool = False

    def mark_completed(self) -> None:
        self.completed = True

    def update(self, duration: Optional[int] = None, priority: Optional[int] = None, notes: Optional[str] = None) -> None:
        if duration is not None:
            self.duration = duration
        if priority is not None:
            self.priority = priority
        if notes is not None:
            self.notes = notes

    def is_high_priority(self) -> bool:
        return self.priority >= 7


@dataclass
class Scheduler:
    owner: Owner
    pet: Pet
    tasks: List[Task] = field(default_factory=list)
    plan: List[Task] = field(default_factory=list)
    reasoning: str = ""

    def add_task(self, task: Task) -> None:
        self.tasks.append(task)

    def remove_task(self, task_id: int) -> None:
        if 0 <= task_id < len(self.tasks):
            self.tasks.pop(task_id)

    def clear_tasks(self) -> None:
        self.tasks.clear()
        self.plan.clear()
        self.reasoning = ""

    def generate_plan(self) -> Tuple[List[Task], str]:
        remaining = self.owner.daily_time_available
        sorted_tasks = sorted(self.tasks, key=lambda t: (-t.priority, t.duration))
        selected: List[Task] = []
        for task in sorted_tasks:
            if task.duration <= remaining:
                selected.append(task)
                remaining -= task.duration

        self.plan = selected
        self.reasoning = (
            f"Scheduled {len(selected)} tasks out of {len(self.tasks)}. "
            f"Total available minutes: {self.owner.daily_time_available}, "
            f"remaining: {remaining}."
        )

        return self.plan, self.reasoning

    def get_reasoning(self) -> str:
        return self.reasoning
