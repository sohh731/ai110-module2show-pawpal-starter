import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet, Owner, Scheduler


def test_task_completion():
    """Verify that calling mark_completed() changes the task's completed status."""
    task = Task(description="Feed the dog", duration=10, frequency="daily")
    assert not task.completed  # Initially False

    task.mark_completed()
    assert task.completed  # Should be True after marking complete


def test_task_addition_to_pet():
    """Verify that adding a task to a Pet increases that pet's task count."""
    pet = Pet(name="Buddy", species="Dog", age=3)
    initial_count = len(pet.tasks)
    assert initial_count == 0

    task = Task(description="Walk the dog", duration=30, frequency="daily")
    pet.add_task(task)

    assert len(pet.tasks) == initial_count + 1
    assert pet.tasks[0] == task
    assert task.pet_name == "Buddy"


def test_recurring_task_rollover():
    """Verify that completing a daily task creates a new task for tomorrow."""
    task = Task(description="Feed the cat", duration=10, frequency="daily", due_date=date.today())
    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is not None
    assert next_task.frequency == "daily"
    assert next_task.completed is False
    assert next_task.due_date == date.today() + timedelta(days=1)


# --- Sorting correctness ---

def test_sort_by_time_chronological_order():
    """Verify tasks are returned in chronological order by start_time."""
    owner = Owner(name="Alex", daily_time_available=120)
    scheduler = Scheduler(owner=owner)

    task_early = Task(description="Morning walk", duration=30, frequency="daily", start_time="07:00")
    task_mid = Task(description="Lunch feed", duration=10, frequency="daily", start_time="12:00")
    task_late = Task(description="Evening play", duration=20, frequency="daily", start_time="18:00")

    # Pass in intentionally out-of-order
    sorted_tasks = scheduler.sort_by_time([task_late, task_early, task_mid])

    assert sorted_tasks[0].start_time == "07:00"
    assert sorted_tasks[1].start_time == "12:00"
    assert sorted_tasks[2].start_time == "18:00"


def test_sort_by_time_missing_start_time_goes_last():
    """Verify tasks with no start_time sort to the end."""
    owner = Owner(name="Alex", daily_time_available=120)
    scheduler = Scheduler(owner=owner)

    task_timed = Task(description="Morning walk", duration=30, frequency="daily", start_time="08:00")
    task_no_time = Task(description="Groom", duration=20, frequency="weekly")

    sorted_tasks = scheduler.sort_by_time([task_no_time, task_timed])

    assert sorted_tasks[0].start_time == "08:00"
    assert sorted_tasks[1].start_time is None


# --- Recurrence logic ---

def test_weekly_task_recurrence():
    """Verify that completing a weekly task creates a new task 7 days later."""
    task = Task(description="Vet checkup", duration=60, frequency="weekly", due_date=date.today())
    next_task = task.mark_completed()

    assert next_task is not None
    assert next_task.due_date == date.today() + timedelta(days=7)
    assert next_task.completed is False


def test_non_recurring_task_returns_none():
    """Verify that completing an 'as needed' task does not create a follow-up."""
    task = Task(description="Emergency bath", duration=20, frequency="as needed")
    next_task = task.mark_completed()

    assert task.completed is True
    assert next_task is None


# --- Conflict detection ---

def test_detect_conflicts_flags_duplicate_times():
    """Verify the scheduler flags two tasks scheduled at the exact same time."""
    owner = Owner(name="Alex", daily_time_available=120)
    pet = Pet(name="Milo", species="Dog", age=2)
    owner.add_pet(pet)

    task1 = Task(description="Morning walk", duration=30, frequency="daily", start_time="08:00")
    task2 = Task(description="Litter box clean", duration=15, frequency="daily", start_time="08:00")
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.detect_conflicts()

    assert len(warnings) == 1
    assert "08:00" in warnings[0]
    assert "Morning walk" in warnings[0]
    assert "Litter box clean" in warnings[0]


def test_detect_conflicts_no_conflict():
    """Verify no conflict warning when all tasks have different start times."""
    owner = Owner(name="Alex", daily_time_available=120)
    pet = Pet(name="Milo", species="Dog", age=2)
    owner.add_pet(pet)

    task1 = Task(description="Morning walk", duration=30, frequency="daily", start_time="07:00")
    task2 = Task(description="Evening feed", duration=10, frequency="daily", start_time="18:00")
    pet.add_task(task1)
    pet.add_task(task2)

    scheduler = Scheduler(owner=owner)
    warnings = scheduler.detect_conflicts()

    assert warnings == ["No conflicts detected."]


# --- Edge cases ---

def test_generate_plan_empty_pet():
    """Verify generate_plan handles a pet with no tasks without crashing."""
    owner = Owner(name="Alex", daily_time_available=60)
    pet = Pet(name="Ghost", species="Cat", age=1)
    owner.add_pet(pet)

    scheduler = Scheduler(owner=owner)
    plan, reasoning = scheduler.generate_plan()

    assert plan == []
    assert "0" in reasoning


def test_generate_plan_excludes_tasks_over_budget():
    """Verify tasks that exceed the daily time budget are left out of the plan."""
    owner = Owner(name="Alex", daily_time_available=30)
    pet = Pet(name="Milo", species="Dog", age=2)
    owner.add_pet(pet)

    task_fits = Task(description="Short walk", duration=20, frequency="daily", priority=5)
    task_too_long = Task(description="Long grooming", duration=60, frequency="weekly", priority=9)
    pet.add_task(task_fits)
    pet.add_task(task_too_long)

    scheduler = Scheduler(owner=owner)
    plan, _ = scheduler.generate_plan()

    descriptions = [t.description for t in plan]
    assert "Short walk" in descriptions
    assert "Long grooming" not in descriptions
