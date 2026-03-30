import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="wide")

# ── Session state: load from data.json if it exists ───────────────────────────
if "owner" not in st.session_state:
    loaded = Owner.load_from_json("data.json")
    st.session_state.owner = loaded if loaded else Owner(name="Jordan", daily_time_available=120)
if "scheduler" not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

scheduler: Scheduler = st.session_state.scheduler
owner: Owner = st.session_state.owner

# ── Task-type emoji helper ────────────────────────────────────────────────────
def task_type_emoji(description: str) -> str:
    """Return an emoji that matches the task type based on keywords."""
    desc = description.lower()
    if any(w in desc for w in ["walk", "run", "exercise", "hike"]):
        return "🦮"
    if any(w in desc for w in ["feed", "food", "meal", "breakfast", "lunch", "dinner", "water"]):
        return "🍖"
    if any(w in desc for w in ["medication", "medicine", "med", "pill", "tablet"]):
        return "💊"
    if any(w in desc for w in ["groom", "brush", "bath", "wash", "trim", "nail"]):
        return "✂️"
    if any(w in desc for w in ["play", "game", "toy", "fetch", "enrichment"]):
        return "🎾"
    if any(w in desc for w in ["vet", "checkup", "appointment", "clinic"]):
        return "🏥"
    if any(w in desc for w in ["litter", "poop", "potty", "clean"]):
        return "🪣"
    return "📋"

# ── Sidebar: owner summary ────────────────────────────────────────────────────
with st.sidebar:
    st.title("🐾 PawPal+")
    st.caption("Smart daily pet care planner")
    st.divider()

    st.markdown(f"**Owner:** {owner.name}")
    st.markdown(f"**Daily budget:** {owner.daily_time_available} min")
    st.divider()

    if owner.pets:
        st.markdown("**Your Pets**")
        for p in owner.pets:
            species_emoji = {"Dog": "🐶", "Cat": "🐱"}.get(p.species, "🐾")
            task_count = len(p.tasks)
            pending = sum(1 for t in p.tasks if not t.completed)
            st.markdown(f"{species_emoji} **{p.name}** — {p.species}, age {p.age}")
            st.caption(f"{pending} pending / {task_count} total tasks")
    else:
        st.info("No pets added yet.")

    st.divider()
    all_tasks = scheduler.get_all_tasks()
    high = sum(1 for t in all_tasks if t.priority_label == "High" and not t.completed)
    if high:
        st.error(f"🔴 {high} high-priority task{'s' if high > 1 else ''} pending")

# ── Main header ───────────────────────────────────────────────────────────────
st.title("🐾 PawPal+")
st.caption("A smart daily care planner for your pets.")

# ── Dashboard metrics row ─────────────────────────────────────────────────────
all_tasks = scheduler.get_all_tasks()
pending   = [t for t in all_tasks if not t.completed]
used_min  = sum(t.duration for t in scheduler.plan) if scheduler.plan else 0
remaining = owner.daily_time_available - used_min

m1, m2, m3, m4 = st.columns(4)
m1.metric("Total Tasks",     len(all_tasks))
m2.metric("Pending",         len(pending))
m3.metric("Time Used",       f"{used_min} min")
m4.metric("Time Remaining",  f"{remaining} min")

if owner.daily_time_available > 0:
    st.progress(min(used_min / owner.daily_time_available, 1.0),
                text=f"Daily budget: {used_min} / {owner.daily_time_available} min used")

st.divider()

# ── Owner settings ────────────────────────────────────────────────────────────
with st.expander("⚙️ Owner Settings", expanded=False):
    col1, col2 = st.columns(2)
    with col1:
        owner_name = st.text_input("Your name", value=owner.name)
        owner.name = owner_name
    with col2:
        daily_time = st.number_input(
            "Daily time available (minutes)",
            min_value=10, max_value=480, value=owner.daily_time_available, step=10
        )
        owner.daily_time_available = daily_time

st.divider()

# ── Pet management ────────────────────────────────────────────────────────────
st.subheader("🐾 Your Pets")

with st.form("add_pet_form", clear_on_submit=True):
    col1, col2, col3 = st.columns(3)
    with col1:
        pet_name = st.text_input("Pet name")
    with col2:
        species = st.selectbox("Species", ["Dog", "Cat", "Other"])
    with col3:
        age = st.number_input("Age", min_value=0, max_value=30, value=1)
    if st.form_submit_button("➕ Add Pet") and pet_name.strip():
        owner.add_pet(Pet(name=pet_name.strip(), species=species, age=age))
        owner.save_to_json("data.json")
        st.success(f"Added {pet_name} to your pets.")

if owner.pets:
    cols = st.columns(len(owner.pets))
    for col, pet in zip(cols, owner.pets):
        species_emoji = {"Dog": "🐶", "Cat": "🐱"}.get(pet.species, "🐾")
        pending_count = sum(1 for t in pet.tasks if not t.completed)
        with col:
            st.markdown(f"### {species_emoji} {pet.name}")
            st.caption(f"{pet.species} · Age {pet.age}")
            if pet.health_notes:
                st.caption(f"📝 {pet.health_notes}")
            st.metric("Pending tasks", pending_count)
else:
    st.info("No pets added yet. Add one above.")

st.divider()

# ── Task management ───────────────────────────────────────────────────────────
st.subheader("📋 Add a Care Task")

pet_names = [p.name for p in owner.pets]
if not pet_names:
    st.warning("Add a pet first before creating tasks.")
else:
    with st.form("add_task_form", clear_on_submit=True):
        col1, col2 = st.columns(2)
        with col1:
            task_desc  = st.text_input("Task description", value="Morning walk")
            duration   = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
            frequency  = st.selectbox("Frequency", ["daily", "weekly", "as needed"])
        with col2:
            assigned_pet = st.selectbox("Assign to pet", pet_names)
            priority     = st.slider("Priority (1 = low, 10 = high)", min_value=1, max_value=10, value=5)
            start_time   = st.text_input("Start time (HH:MM, optional)", value="")

        if st.form_submit_button("➕ Add Task") and task_desc.strip():
            scheduler.add_task_to_pet(assigned_pet, Task(
                description=task_desc.strip(),
                duration=duration,
                frequency=frequency,
                priority=priority,
                start_time=start_time.strip() if start_time.strip() else None,
            ))
            owner.save_to_json("data.json")
            st.success(f"Added '{task_desc}' for {assigned_pet}.")

# ── All tasks table ───────────────────────────────────────────────────────────
all_tasks = scheduler.get_all_tasks()
if all_tasks:
    st.markdown("**All Tasks (sorted by start time):**")
    sorted_tasks = scheduler.sort_by_time(all_tasks)
    task_rows = [
        {
            "":          task_type_emoji(t.description),
            "Priority":  f"{t.priority_emoji} {t.priority_label}",
            "Pet":       t.pet_name or "N/A",
            "Task":      t.description,
            "Start":     t.start_time or "Unscheduled",
            "Duration":  f"{t.duration} min",
            "Frequency": t.frequency,
            "Status":    "✅ Done" if t.completed else "⏳ Pending",
        }
        for t in sorted_tasks
    ]
    st.dataframe(task_rows, use_container_width=True, hide_index=True)

st.divider()

# ── Conflict detection ────────────────────────────────────────────────────────
st.subheader("⚠️ Conflict Check")

if all_tasks:
    warnings = scheduler.detect_conflicts()
    if warnings == ["No conflicts detected."]:
        st.success("✅ No scheduling conflicts found.")
    else:
        for w in warnings:
            st.error(
                f"**Time conflict detected:** {w}\n\n"
                "Two or more tasks are scheduled at the same start time. "
                "Shift one to a different time to avoid missed care."
            )
else:
    st.info("Add tasks above to check for conflicts.")

st.divider()

# ── Next available slot ───────────────────────────────────────────────────────
st.subheader("🕐 Find Next Available Slot")
slot_dur = st.number_input("Task duration to fit (minutes)", min_value=5, max_value=120, value=30, step=5)
if st.button("Find Slot"):
    slot = scheduler.find_next_available_slot(slot_dur)
    if slot:
        st.success(f"Next open slot for a {slot_dur}-min task: **{slot}**")
    else:
        st.warning("No open slot found in the 07:00–21:00 window for that duration.")

st.divider()

# ── Generate daily plan ───────────────────────────────────────────────────────
st.subheader("📅 Generate Today's Plan")

if st.button("Generate Schedule", type="primary"):
    plan, reasoning = scheduler.generate_plan()
    if plan:
        high_count = sum(1 for t in plan if t.priority_label == "High")
        total_min  = sum(t.duration for t in plan)

        st.success(f"✅ Plan ready — {len(plan)} tasks, {total_min} min, {high_count} high-priority.")

        p1, p2, p3 = st.columns(3)
        p1.metric("Tasks scheduled", len(plan))
        p2.metric("Total time",      f"{total_min} min")
        p3.metric("High priority",   high_count)

        st.markdown("**Today's Schedule — by priority then time:**")
        schedule_rows = [
            {
                "":         task_type_emoji(t.description),
                "Priority": f"{t.priority_emoji} {t.priority_label}",
                "Pet":      t.pet_name or "N/A",
                "Task":     t.description,
                "Start":    t.start_time or "Flexible",
                "Duration": f"{t.duration} min",
            }
            for t in plan
        ]
        st.dataframe(schedule_rows, use_container_width=True, hide_index=True)

        st.markdown("**Same Plan — chronological order:**")
        sorted_plan = scheduler.sort_by_time(plan)
        chrono_rows = [
            {
                "Start":    t.start_time or "Flexible",
                "":         task_type_emoji(t.description),
                "Priority": f"{t.priority_emoji} {t.priority_label}",
                "Task":     t.description,
                "Pet":      t.pet_name or "N/A",
                "Duration": f"{t.duration} min",
            }
            for t in sorted_plan
        ]
        st.dataframe(chrono_rows, use_container_width=True, hide_index=True)

        st.caption(reasoning)
    else:
        st.warning(
            "No tasks could be scheduled. All tasks may be completed, "
            "or total task time exceeds your available time today."
        )
