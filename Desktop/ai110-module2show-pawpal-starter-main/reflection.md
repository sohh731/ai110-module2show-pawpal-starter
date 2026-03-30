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

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
