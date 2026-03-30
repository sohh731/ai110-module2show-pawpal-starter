from tabulate import tabulate
from pawpal_system import Owner, Pet, Task, Scheduler


def priority_badge(label: str) -> str:
    return {"High": "🔴 High", "Medium": "🟡 Medium", "Low": "🟢 Low"}.get(label, label)


def status_badge(completed: bool) -> str:
    return "✅ Done" if completed else "⏳ Pending"


def main():
    # ── Setup ─────────────────────────────────────────────────────────────────
    owner = Owner(name="Alex", daily_time_available=180)
    pet1  = Pet(name="Milo", species="Dog", age=3)
    pet2  = Pet(name="Luna", species="Cat", age=2)
    owner.add_pet(pet1)
    owner.add_pet(pet2)

    task1 = Task(description="Morning walk",      duration=30, frequency="daily",  priority=9,  start_time="08:00")
    task2 = Task(description="Feed breakfast",    duration=15, frequency="daily",  priority=10, start_time="07:00")
    task3 = Task(description="Litter box clean",  duration=20, frequency="daily",  priority=8,  start_time="08:00")
    task4 = Task(description="Evening play",      duration=25, frequency="daily",  priority=7,  start_time="18:00")

    pet2.add_task(task3)
    pet1.add_task(task1)
    pet1.add_task(task2)
    pet2.add_task(task4)

    scheduler = Scheduler(owner=owner)

    # ── All tasks sorted by time ───────────────────────────────────────────────
    print("\n" + "=" * 62)
    print("  🐾  PawPal+ Daily Planner")
    print("═" * 62)

    all_tasks    = scheduler.get_all_tasks()
    sorted_tasks = scheduler.sort_by_time(all_tasks)

    rows = [
        [
            t.priority_emoji,
            priority_badge(t.priority_label),
            t.pet_name or "—",
            t.description,
            t.start_time or "Unscheduled",
            f"{t.duration} min",
            status_badge(t.completed),
        ]
        for t in sorted_tasks
    ]
    print("\n📋  All Tasks (sorted by start time)\n")
    print(tabulate(
        rows,
        headers=["", "Priority", "Pet", "Task", "Start", "Duration", "Status"],
        tablefmt="rounded_outline",
    ))

    # ── Conflict warnings ──────────────────────────────────────────────────────
    print("\n⚠️   Conflict Check\n")
    for w in scheduler.detect_conflicts():
        prefix = "✅" if w == "No conflicts detected." else "🚨"
        print(f"  {prefix}  {w}")

    # ── Next available slot ────────────────────────────────────────────────────
    slot = scheduler.find_next_available_slot(duration=30)
    print(f"\n🕐  Next available 30-min slot: {slot or 'none found'}")

    # ── Daily plan ────────────────────────────────────────────────────────────
    plan, reasoning = scheduler.generate_plan()
    print("\n" + "=" * 62)
    print("  📅  Today's Schedule")
    print("═" * 62)

    plan_rows = [
        [
            t.priority_emoji,
            priority_badge(t.priority_label),
            t.pet_name or "—",
            t.description,
            t.start_time or "Flexible",
            f"{t.duration} min",
        ]
        for t in plan
    ]
    print(tabulate(
        plan_rows,
        headers=["", "Priority", "Pet", "Task", "Start", "Duration"],
        tablefmt="rounded_outline",
    ))
    print(f"\n  📊  {reasoning}\n")


if __name__ == "__main__":
    main()
