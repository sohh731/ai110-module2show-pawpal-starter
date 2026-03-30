# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

For this assignment, I identified three core actions a user should be able to perform with the app. 
    1) Setting up their profile and pet information, entering details like their name, how much time they have available in a day, and their pet's name, species, and age. 
    2) Adding and managing care tasks such as walks, feedings, medication reminders, or grooming sessions, where each task captures at minimum how long it takes and how important it is. 
    3) Generating and viewing a daily care plan that fits within the owner's available time, prioritizes higher-importance tasks, and explains why certain tasks were included or left out.

The initial UML design was built around five classes to support those three actions. 
    1) The Owner class held the pet owner's name and total daily time available in minutes, and its responsibility was to act as a constraint source for the scheduler, representing what the owner could realistically fit into a given day. 
    2) The Pet class stored attributes like name, species, age, and any relevant health notes, serving a purely descriptive role that captured who the care tasks were being planned for. 
    3) The Task class was the central data model, where each instance held a name, category, duration in minutes, and a priority level, representing a single unit of care work in a form the scheduler could reason about.
    4) The Scheduler class served as the logic engine, accepting an Owner, a Pet, and a list of Task objects, then sorting tasks by priority and filtering them to fit within the owner's available time before returning an ordered plan. 
    5) The DailyPlan class rounded out the design as a lightweight output container, holding the scheduled tasks alongside a plain-text explanation of the reasoning behind the selections.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

The design did change during implementation in one meaningful way. The DailyPlan class was removed and its responsibilities were folded back into Scheduler. In the initial design, DailyPlan existed to cleanly separate the output structure from the scheduling logic, which seemed like a good idea on paper. In practice, the separation added unnecessary indirection, the Streamlit UI simply needed to call the scheduler and immediately render the result, and routing that data through a dedicated wrapper class created extra overhead without any real behavioral benefit. The change was made by having Scheduler.generate_plan() return a plain list of Task objects in priority order alongside a separately generated reasoning string, rather than packaging everything inside a DailyPlan instance. This simplified the data flow, made the UI code easier to follow, and reduced the number of objects that tests needed to construct.

After AI review, I refined the model relationships and scheduling behavior: `Owner` now tracks `pets`, `Task` can associate to a pet with `pet_name`, and `Scheduler.generate_plan()` uses an incremental `used_time` check through `Owner.can_schedule()` to avoid planning over the daily budget. I also changed task removal from index-based to object identity to reduce brittle indexing. These edits align with the existing rationale in 1b while making the implementation more robust to future extensions.


---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

The scheduler considers two constraints: available time and task priority. The owner's `daily_time_available` (in minutes) acts as a hard cap — no task is added to the plan if it would push the total over budget. Task priority (a number from 1 to 10) acts as the ordering rule — higher-priority tasks are always evaluated first, so they claim time before lower-priority ones can.

Time was treated as the most important constraint because it is the one the owner cannot negotiate around. A busy person has a fixed number of minutes in a day, and a scheduler that ignores that limit is not useful. Priority was treated as the second constraint because not all pet care tasks carry the same urgency — a medication reminder matters more than an enrichment activity, and the system needs a way to reflect that. Owner preferences were considered during design but not implemented as a filtering constraint, since priority already covers the same intent in a simpler and more direct way.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

The scheduler uses exact start-time matching for conflict detection instead of checking whether two tasks overlap in duration. For example, if "Morning walk" starts at 08:00 and lasts 30 minutes, and "Litter box clean" also starts at 08:00 and lasts 20 minutes, the conflict is caught but if a third task starts at 08:15 (inside the walk's window), it is not flagged as a conflict because its start time is different.

This tradeoff is reasonable for a personal pet care scheduler because the tasks involved are informal and flexible by nature. A pet owner is not running a tight production schedule; they are managing rough daily routines where "08:00" means "around breakfast time," not a hard clock-in. Checking exact time-slot collisions catches the most obvious double-bookings (two things scheduled at the exact same time) without requiring the added complexity of interval-overlap logic, which would also demand that every task have a reliable end time. Since many tasks in this system are left without a start time at all, a full interval-based conflict model would either produce false negatives on unscheduled tasks or require enforcing start times as mandatory — both of which add friction without meaningful benefit for the target use case.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

AI tools were used at several stages of this project. During design, Copilot Chat was used with `#codebase` to ask what edge cases a pet scheduler should handle and what the most important behaviors to test were. This helped surface scenarios like a pet with no tasks or tasks that exceed the daily budget, which would have been easy to overlook. During implementation, the Generate Docs smart action was used to add docstrings to the algorithmic methods, and Copilot Chat was used to review the `generate_plan` algorithm for readability, which produced a side-by-side comparison of the original version and a compressed Pythonic version. During testing, the Generate Tests smart action was used to draft the initial test functions, which were then reviewed and adjusted before saving. For the README and reflection, prompts asking for plain-language explanations of specific methods produced useful starting points that were edited for accuracy and tone.

For the advanced algorithmic feature, Agent Mode was used to implement `find_next_available_slot()`. Rather than asking for a single code suggestion, Agent Mode was given the full context — the existing Scheduler class, the Task structure, and the goal of finding the first open time window of a given length — and allowed to reason through the interval-merging logic, identify edge cases (overlapping tasks, no timed tasks, no gap large enough), and produce a working implementation with docstring and tests in one pass. The difference from standard Chat was that the agent could hold the full problem in context and work through it step by step without needing follow-up prompts to handle each edge case separately.

Starting a new Copilot Chat session for each phase — design, implementation, testing, and documentation — helped keep the context focused. When a session carried too much history from a previous phase, suggestions started mixing concerns, for example offering UI advice during a backend logic discussion. A fresh session for each phase meant the AI's context matched the current task, which produced more relevant and on-topic responses.

The most helpful prompts were specific ones that referenced the actual code rather than asking general questions. For example, asking "what are the most important edge cases to test for a scheduler with sorting and recurring tasks" with `#codebase` attached gave more actionable results than asking "how do I test a scheduler." Asking AI to explain a piece of test code before accepting it was also useful, since it made it easier to catch cases where the generated test was checking the wrong thing.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When asked to review `generate_plan` for readability, Copilot suggested a compressed version that inlined the `uncompleted` variable and collapsed several lines into one. The suggestion was technically correct and slightly more Pythonic, but it was not accepted as-is. The original version kept `uncompleted` as a named variable, which made it clear that two separate things were happening — filtering tasks and then sorting them. In the compressed version, those two steps were merged into a single expression that was harder to read at a glance and harder to inspect in a debugger.

The evaluation came down to one question: does this change make the code easier or harder for a person to understand? Since the compressed version offered no performance improvement and only saved one line, readability won. The one part of Copilot's suggestion that was worth keeping was inlining the `remaining` calculation directly into the f-string, since that was a minor cleanup with no readability cost. The rest was left as originally written. This showed that AI suggestions are worth reading closely rather than accepting or rejecting entirely — the right call is often to take the useful part and leave the rest.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

The test suite covers five areas. Task completion was tested to confirm that calling `mark_completed()` sets the completed flag to True and that daily and weekly tasks return a correctly dated follow-up task, while one-off tasks return nothing. Sorting was tested to confirm that `sort_by_time()` returns tasks in chronological order and that tasks with no start time always end up last. Conflict detection was tested to confirm that two tasks sharing an exact start time produce a warning naming both tasks, and that tasks at different times produce a clean result. Plan generation was tested to confirm that tasks exceeding the owner's daily time budget are excluded, and that a pet with no tasks does not crash the scheduler. Task assignment was tested to confirm that adding a task to a pet correctly sets the task's pet name and increases the pet's task count.

These tests mattered because they cover the parts of the system where a silent bug would be hardest to notice. A scheduling bug that quietly drops a high-priority task or creates a recurring task with the wrong due date would not raise an error — it would just produce a wrong result. Testing these behaviors explicitly means the system can be changed later without accidentally breaking the logic that users rely on most.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

Confidence is high for the core behaviors: plan generation, recurrence, sorting, and conflict detection all pass their tests and behave as expected when running the app manually. The greedy scheduling algorithm is simple enough that there are few hidden code paths to worry about. The areas of lower confidence are around conflict detection and edge input values. Conflict detection only flags exact start-time matches, so two tasks that overlap in duration but start at different times will not be caught. That is a known gap rather than a hidden bug, but it means the feature is less complete than it appears.

The edge cases to test next would be: two tasks where one starts inside the other's duration window (overlap without exact time match), an owner with zero minutes of daily time available, a task with a duration of zero, and marking the same task complete twice in a row to check whether duplicate follow-up tasks are created. These were left out of the current suite not because they are unlikely, but because they require slightly more setup and the core behaviors were the priority within the project timeline.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

The part of the project that went best was the connection between the backend logic and the Streamlit UI. Early in the build, the app stored tasks as plain dictionaries that had nothing to do with the Scheduler class. By the end, every UI action, adding a pet, adding a task, generating the schedule, checking for conflicts, called a real method on the backend classes. The UI did not duplicate any logic; it just called the scheduler and displayed the result. That separation made the app easier to reason about and meant that fixing a bug in the backend automatically fixed it in the UI as well. Getting that connection clean and consistent was the most satisfying part of the build.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

The first thing to improve would be conflict detection. The current implementation only flags tasks that share an exact start time string. A more useful version would check whether any two tasks overlap in duration, if a 30-minute task starts at 08:00 and another starts at 08:15, those genuinely conflict but the current code misses it entirely. Fixing this would require calculating each task's end time and checking for interval overlap, which is straightforward but was left out to keep the first version simple.

The second improvement would be connecting task completion to the UI. The `mark_task_complete()` method already exists in the Scheduler class and the recurrence logic is fully built and tested, but the app has no button to actually mark a task as done. This means the recurrence feature works in code but a user can never trigger it from the app. Adding a "Mark Done" button next to each task in the schedule would complete the feature and make the daily and weekly recurrence logic visible and usable in practice, without requiring any new backend logic to be written.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

The most important thing learned was that working with AI requires staying in the role of lead architect. AI can generate code, suggest tests, and draft documentation quickly, but it does not know which design decisions matter, which tradeoffs are acceptable, or what the system is actually supposed to do. Every suggestion it made had to be evaluated against those things, and that evaluation could only come from the person who understood the project. When that role was held firmly — deciding what to build, reviewing what AI produced, and rejecting or modifying suggestions that did not fit — the collaboration worked well. When prompts were vague and suggestions were accepted without review, the output drifted away from the design. The lesson is that AI accelerates execution but does not replace the thinking that has to happen before execution begins.

---

## 6. Prompt Comparison

The task chosen for comparison was writing a `reschedule_overdue()` method for the `Scheduler` class — a method that finds all recurring tasks whose `due_date` has already passed and reschedules them to today. This was a good candidate because it involves date logic, nested object traversal, and a choice between using existing class abstractions or bypassing them.

The prompt sent to both models was: "Write a method for the Scheduler class that finds all overdue recurring tasks where due_date is before today, reschedules them to today by updating their due_date, and returns the list of rescheduled tasks. The class already has get_all_tasks() and get_pending_tasks() helper methods."

GPT-4o produced a solution that used a nested loop directly over `owner.pets` and `pet.tasks`, bypassing the `get_pending_tasks()` helper the class already provides. It also mixed the filtering logic and the mutation in the same loop, checked frequency with a case-sensitive list comparison, and did not include a return type annotation. Because it ignored `get_pending_tasks()`, it would silently reschedule tasks that were already marked complete — a logic error that would not raise an exception but would produce wrong results.

Claude produced a solution that called `get_pending_tasks()` to do the filtering, which excludes completed tasks and respects the abstraction the class already provides. It separated the filter step from the mutation step — finding all overdue tasks first, then updating them — which makes each step easier to read and test on its own. It applied `.lower()` to handle mixed-case frequency values, used a set for O(1) lookup, and included a return type annotation.

The Claude version is more modular and more correct. Both models arrived at the same core algorithm, but Claude's version works within the existing class design while GPT-4o's bypasses it. The final implementation in `pawpal_system.py` follows the Claude version.
