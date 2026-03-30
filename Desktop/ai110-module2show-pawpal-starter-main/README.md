# PawPal+

A smart daily pet care planner built with Python and Streamlit. PawPal+ helps pet owners schedule care tasks across multiple pets, respects their available time, and explains every scheduling decision it makes.

---

## Features

**Priority-first scheduling.**
`Scheduler.generate_plan()` uses a greedy algorithm that sorts all pending tasks by descending priority, then ascending duration. Tasks with higher importance (e.g. medication, feeding) are always selected first. When two tasks share the same priority, the shorter one is preferred so more tasks fit within the daily time budget.

**Chronological sorting.**
`sort_by_time()` converts each task's `start_time` (HH:MM string) into total minutes since midnight and sorts numerically. Tasks with no start time are automatically placed at the end of the day. The schedule is shown both by priority order and chronological order so the owner can read it either way.

**Flexible task filtering.**
`filter_tasks()` lets the UI slice the full task list by pet name, completion status, or both at once. This powers per-pet views and pending-only displays without duplicating any logic.

**Next available slot finder.**
`find_next_available_slot(duration)` uses an interval scheduling algorithm to find the earliest open window in the day that fits a task of the requested length. It converts all timed tasks into `(start, end)` minute intervals, sorts and merges overlapping ones, then walks the gaps to return the first slot large enough. The search is bounded by a configurable day window (default 07:00–21:00). This was implemented using Agent Mode to reason through the interval-merging logic and edge cases before writing the code.

**Conflict warnings.**
`detect_conflicts()` groups all pending tasks by exact start time. Any slot with two or more tasks triggers a `st.warning` in the UI that names every conflicting task and its pet, and tells the owner to shift one to a different time.

**Daily and weekly recurrence.**
`Task.mark_completed()` automatically creates the next occurrence of a recurring task. Daily tasks get a new due date of today + 1 day; weekly tasks get today + 7 days. One-off tasks ("as needed") return nothing when completed.

**Multi-pet support.**
An `Owner` can have any number of `Pet` objects. The scheduler aggregates tasks from every pet and plans across all of them in a single pass.

---

## Demo

Run the app locally:

```bash
streamlit run app.py
```

<a href="/course_images/ai110/pawpal_screenshot.png" target="_blank">
  <img src='/course_images/ai110/pawpal_screenshot.png' title='PawPal App' width='' alt='PawPal App' class='center-block' />
</a>

> To update the screenshot: run the app, take a screenshot, save it as `pawpal_screenshot.png` in this folder, then replace the filename above if needed.

---

## Project Structure

```
pawpal_system.py   — core classes: Task, Pet, Owner, Scheduler
app.py             — Streamlit UI
test_pawpal.py     — automated test suite (11 tests)
uml_final.png      — final class diagram
reflection.md      — design decisions and tradeoffs
requirements.txt   — dependencies
```

---

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

All 11 tests pass. The core scheduling behaviors — priority ordering, time budgeting, recurrence, sorting, and conflict detection — are verified. The rating is not a full 5 because conflict detection only checks for exact start-time matches and does not catch overlapping durations, which is a known limitation.

---

## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Run

```bash
streamlit run app.py
```
