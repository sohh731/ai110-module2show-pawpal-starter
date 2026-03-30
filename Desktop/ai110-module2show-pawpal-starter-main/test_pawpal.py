import pytest
from datetime import date, timedelta
from pawpal_system import Task, Pet


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

