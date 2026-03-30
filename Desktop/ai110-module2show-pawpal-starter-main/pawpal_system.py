# pawpal_system.py
# Core model classes for PawPal+ pet care scheduler

from __future__ import annotations
from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import List, Optional, Tuple


@dataclass
class Task:
    description: str
    duration: int  # in minutes
    frequency: str  # e.g. "daily", "weekly", "as needed"
    priority: int = 5
    pet_name: Optional[str] = None
    completed: bool = False
    notes: str = ''
    start_time: Optional[str] = None  # e.g. "09:00" format
    due_date: Optional[date] = None

    def mark_completed(self) -> Optional['Task']:
        """Mark the task as completed and return the next recurring task when applicable.

        Sets ``completed`` to True. For daily or weekly tasks, computes the next
        due date by adding 1 or 7 days respectively to ``due_date`` (defaulting
        to today if ``due_date`` is not set), then returns a new Task copy with
        that due date and ``completed=False``. Returns None for one-off tasks.

        Returns:
            Task: A new Task scheduled for the next occurrence, or None if the
            frequency is not 'daily' or 'weekly'.
        """
        self.completed = True
        if self.frequency.lower() in {'daily', 'weekly'}:
            if self.due_date is None:
                self.due_date = date.today()
            delta = timedelta(days=1 if self.frequency.lower() == 'daily' else 7)
            next_due_date = self.due_date + delta
            next_task = Task(
                description=self.description,
                duration=self.duration,
                frequency=self.frequency,
                priority=self.priority,
                pet_name=self.pet_name,
                notes=self.notes,
                start_time=self.start_time,
                due_date=next_due_date,
                completed=False,
            )
            return next_task
        return None

    def mark_incomplete(self) -> None:
        """Mark the task as incomplete."""
        self.completed = False

    def update(self,
               duration: Optional[int] = None,
               frequency: Optional[str] = None,
               priority: Optional[int] = None,
               notes: Optional[str] = None) -> None:
        """Update task attributes."""
        if duration is not None:
            self.duration = duration
        if frequency is not None:
            self.frequency = frequency
        if priority is not None:
            self.priority = priority
        if notes is not None:
            self.notes = notes

    def is_high_priority(self) -> bool:
        """Check if the task is high priority."""
        return self.priority >= 7


@dataclass
class Pet:
    name: str
    species: str
    age: int
    health_notes: str = ""
    tasks: List[Task] = field(default_factory=list)

    def update_health_notes(self, notes: str) -> None:
        """Update the pet's health notes."""
        self.health_notes = notes

    def birthday(self) -> None:
        """Increment the pet's age by one year."""
        self.age += 1

    def add_task(self, task: Task) -> None:
        """Add a task to the pet."""
        task.pet_name = self.name
        self.tasks.append(task)

    def remove_task(self, task: Task) -> None:
        """Remove a task from the pet."""
        self.tasks = [t for t in self.tasks if t is not task]

    def get_tasks(self) -> List[Task]:
        """Get a list of the pet's tasks."""
        return list(self.tasks)

    def get_summary(self) -> str:
        """Get a summary string of the pet."""
        return f"{self.name} ({self.species}, {self.age} yrs): {self.health_notes}"


@dataclass
class Owner:
    name: str
    daily_time_available: int  # minutes
    preferences: List[str] = field(default_factory=list)
    pets: List[Pet] = field(default_factory=list)

    def set_daily_time(self, minutes: int) -> None:
        """Set the owner's daily available time."""
        self.daily_time_available = minutes

    def add_preference(self, preference: str) -> None:
        """Add a preference to the owner."""
        self.preferences.append(preference)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner."""
        self.pets.append(pet)

    def remove_pet(self, pet_name: str) -> None:
        """Remove a pet from the owner by name."""
        self.pets = [p for p in self.pets if p.name != pet_name]

    def can_schedule(self, duration: int, used_time: int = 0) -> bool:
        """Check if the owner can schedule a task of given duration."""
        return duration <= (self.daily_time_available - used_time)


@dataclass
class Scheduler:
    owner: Owner
    plan: List[Task] = field(default_factory=list)
    reasoning: str = ""

    def get_all_tasks(self) -> List[Task]:
        """Get all tasks from all pets."""
        tasks: List[Task] = []
        for pet in self.owner.pets:
            tasks.extend(pet.get_tasks())
        return tasks

    def get_pending_tasks(self) -> List[Task]:
        """Get all uncompleted tasks."""
        return [task for task in self.get_all_tasks() if not task.completed]

    def mark_task_complete(self, task: Task) -> Optional[Task]:
        """Complete a task and schedule next occurrence for daily/weekly tasks."""
        next_task = task.mark_completed()
        if next_task and task.pet_name:
            self.add_task_to_pet(task.pet_name, next_task)
        return next_task

    def add_task_to_pet(self, pet_name: str, task: Task) -> bool:
        """Add a task to a specific pet."""
        pet = self._find_pet(pet_name)
        if pet:
            pet.add_task(task)
            return True
        return False

    def remove_task_from_pet(self, pet_name: str, task: Task) -> bool:
        """Remove a task from a specific pet."""
        pet = self._find_pet(pet_name)
        if pet and task in pet.tasks:
            pet.remove_task(task)
            return True
        return False

    def _find_pet(self, pet_name: str) -> Optional[Pet]:
        """Find a pet by name."""
        for pet in self.owner.pets:
            if pet.name == pet_name:
                return pet
        return None

    def generate_plan(self) -> Tuple[List[Task], str]:
        """Generate a daily schedule plan using a greedy priority-first algorithm.

        Retrieves all uncompleted tasks across every pet, sorts them by
        descending priority and then ascending duration (so equal-priority tasks
        that are shorter are preferred when time is tight), and greedily appends
        each task to the plan as long as its duration fits within the owner's
        remaining daily budget.  Updates ``self.plan`` and ``self.reasoning``
        in-place before returning them.

        Returns:
            Tuple[List[Task], str]: The ordered list of scheduled tasks and a
            human-readable string explaining how many tasks were selected and
            how much time was used vs. available.
        """
        uncompleted = self.get_pending_tasks()
        ordered = sorted(uncompleted, key=lambda t: (-t.priority, t.duration))

        self.plan.clear()
        used_time = 0

        for task in ordered:
            if self.owner.can_schedule(task.duration, used_time):
                self.plan.append(task)
                used_time += task.duration

        remaining = self.owner.daily_time_available - used_time
        self.reasoning = (
            f"Selected {len(self.plan)} tasks out of {len(uncompleted)} pending tasks. "
            f"Used {used_time}/{self.owner.daily_time_available} minutes, remaining {remaining}."
        )

        return self.plan, self.reasoning

    def set_owner_time(self, minutes: int) -> None:
        """Set the owner's daily time."""
        self.owner.set_daily_time(minutes)

    def get_reasoning(self) -> str:
        """Get the reasoning for the current plan."""
        return self.reasoning

    def sort_by_time(self, tasks: List[Task]) -> List[Task]:
        """Sort tasks chronologically by their start_time in HH:MM format.

        Converts each task's start_time string to total minutes since midnight
        for numeric comparison. Tasks with no start_time are placed at the end
        (treated as 24:00 / 1440 minutes).

        Args:
            tasks (List[Task]): The tasks to sort; the original list is not mutated.

        Returns:
            List[Task]: A new list ordered from earliest to latest start time.
        """
        def time_to_minutes(time_str: str) -> int:
            if not time_str:
                return 24 * 60  # Late default
            h, m = map(int, time_str.split(':'))
            return h * 60 + m

        return sorted(tasks, key=lambda t: time_to_minutes(t.start_time or ""))

    def filter_tasks(self, pet_name: Optional[str] = None, completed: Optional[bool] = None) -> List[Task]:
        """Filter tasks across all pets by pet name and/or completion status.

        Retrieves all tasks from every pet and applies up to two optional
        filters. Either filter can be omitted to skip that constraint.

        Args:
            pet_name (Optional[str]): If provided, only return tasks assigned
                to the pet with this name.
            completed (Optional[bool]): If provided, only return tasks whose
                completed flag matches this value.

        Returns:
            List[Task]: Tasks that match all supplied filter criteria.
        """
        tasks = self.get_all_tasks()
        if pet_name is not None:
            tasks = [t for t in tasks if t.pet_name == pet_name]
        if completed is not None:
            tasks = [t for t in tasks if t.completed == completed]
        return tasks

    def detect_conflicts(self) -> List[str]:
        """Detect scheduling conflicts among pending tasks that share an exact start time.

        Groups all uncompleted tasks by their start_time string. Any time slot
        with more than one task is reported as a conflict. Tasks without a
        start_time are ignored. If no conflicts are found, returns a single
        confirmation message.

        Returns:
            List[str]: Warning strings describing each conflicting time slot,
            or ["No conflicts detected."] if the schedule is clean.
        """
        tasks = self.get_pending_tasks()
        by_time: dict[str, List[Task]] = {}
        for task in tasks:
            if task.start_time:
                by_time.setdefault(task.start_time, []).append(task)

        warnings: List[str] = []
        for start_time, group in by_time.items():
            if len(group) > 1:
                conflict_desc = ", ".join(f"{t.description} ({t.pet_name or 'unknown'})" for t in group)
                warnings.append(f"Conflict at {start_time}: {conflict_desc}")

        if not warnings:
            warnings.append("No conflicts detected.")

        return warnings
