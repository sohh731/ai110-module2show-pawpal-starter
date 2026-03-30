# PawPal+ (Module 2 Project)

You are building **PawPal+**, a Streamlit app that helps a pet owner plan care tasks for their pet.

## Scenario

A busy pet owner needs help staying consistent with pet care. They want an assistant that can:

- Track pet care tasks (walks, feeding, meds, enrichment, grooming, etc.)
- Consider constraints (time available, priority, owner preferences)
- Produce a daily plan and explain why it chose that plan

Your job is to design the system first (UML), then implement the logic in Python, then connect it to the Streamlit UI.

## What you will build

Your final app should:

- Let a user enter basic owner + pet info
- Let a user add/edit tasks (duration + priority at minimum)
- Generate a daily schedule/plan based on constraints and priorities
- Display the plan clearly (and ideally explain the reasoning)
- Include tests for the most important scheduling behaviors

## Smarter Scheduling

PawPal+ goes beyond a basic task list with four scheduling features.

**Priority-first plan generation.** `Scheduler.generate_plan()` sorts all pending tasks by descending priority, then ascending duration, and greedily fills the owner's daily time budget. Higher-importance tasks (e.g. medication) always land in the plan before lower-priority ones, and shorter tasks are preferred when two tasks share the same priority.

**Chronological sorting.** `sort_by_time()` orders any task list by `start_time` (HH:MM), converting times to minutes since midnight for accurate numeric comparison. Tasks without a start time are placed at the end of the day automatically.

**Flexible filtering.** `filter_tasks()` lets you slice the full task list by pet name, completion status, or both at once. This is useful for showing only a specific pet's pending tasks in the UI.

**Conflict detection.** `detect_conflicts()` scans pending tasks and flags any time slot where two or more tasks share an exact start time, reporting each conflict with the task names and pet labels involved.

---

## Testing PawPal+

To run the full test suite:

```bash
python -m pytest test_pawpal.py -v
```

The suite contains 11 tests covering three main areas.

**Sorting correctness.** Tests confirm that `sort_by_time()` returns tasks in chronological order (07:00 before 12:00 before 18:00) and that tasks with no start time are placed at the end of the list.

**Recurrence logic.** Tests confirm that completing a daily task produces a follow-up task due the next day, that completing a weekly task produces one due 7 days later, and that completing a one-off task (frequency "as needed") returns nothing.

**Conflict detection.** Tests confirm that two tasks sharing an exact start time produce a warning naming both tasks, and that tasks at different times produce a clean "No conflicts detected." message.

**Edge cases.** Additional tests verify that `generate_plan()` handles a pet with zero tasks without crashing, and that tasks exceeding the owner's daily time budget are correctly excluded from the plan.

**Confidence level: 4 out of 5 stars.**

All 11 tests pass. The core scheduling behaviors — priority ordering, time budgeting, recurrence, sorting, and conflict detection — are verified. The rating is not a full 5 because conflict detection only checks for exact start-time matches and does not catch overlapping durations, which is a known limitation. That gap is documented in the Smarter Scheduling section above.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.
