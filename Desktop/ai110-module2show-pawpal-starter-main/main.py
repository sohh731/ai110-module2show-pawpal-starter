from pawpal_system import Owner, Pet, Task, Scheduler


def main():
    # Create owner and pets
    owner = Owner(name="Alex", daily_time_available=180)
    pet1 = Pet(name="Milo", species="Dog", age=3)
    pet2 = Pet(name="Luna", species="Cat", age=2)

    owner.add_pet(pet1)
    owner.add_pet(pet2)

    # Add tasks out of order with start times
    task1 = Task(description="Morning walk", duration=30, frequency="daily", priority=9, start_time="08:00")
    task2 = Task(description="Feed breakfast", duration=15, frequency="daily", priority=10, start_time="07:00")
    task3 = Task(description="Litter box clean", duration=20, frequency="daily", priority=8, start_time="08:00")
    task4 = Task(description="Evening play session", duration=25, frequency="daily", priority=7, start_time="18:00")

    # Add in random order
    pet2.add_task(task3)
    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task4)

    # Create scheduler and generate plan
    scheduler = Scheduler(owner=owner)
    plan, reasoning = scheduler.generate_plan()

    # Demonstrate sorting and filtering
    all_tasks = scheduler.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    milo_tasks = scheduler.filter_tasks(pet_name="Milo")
    pending_tasks = scheduler.filter_tasks(completed=False)

    print("All Tasks (unsorted):")
    for t in all_tasks:
        print(f"  {t.description} at {t.start_time}")
    print()

    print("Tasks Sorted by Time:")
    for t in sorted_tasks:
        print(f"  {t.description} at {t.start_time}")
    print()

    print("Tasks for Milo:")
    for t in milo_tasks:
        print(f"  {t.description}")
    print()

    print("Pending Tasks:")
    for t in pending_tasks:
        print(f"  {t.description}")
    print()

    # Conflict detection
    conflict_warnings = scheduler.detect_conflicts()
    print("Conflict Warnings:")
    for w in conflict_warnings:
        print(f"  {w}")
    print()

    # Print schedule
    print("Today's Schedule")
    print("--------------")
    for i, t in enumerate(plan, start=1):
        pet_label = t.pet_name or "Unknown"
        status = "Done" if t.completed else "Pending"
        print(f"{i}. {t.description} (pet: {pet_label}, duration: {t.duration}m, priority: {t.priority}, status: {status})")

    print("\n", reasoning)


if __name__ == "__main__":
    main()