import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")

# Initialize session state for persistent data
if 'owner' not in st.session_state:
    st.session_state.owner = Owner(name="Jordan", daily_time_available=120)  # Default owner
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = Scheduler(owner=st.session_state.owner)

st.title("🐾 PawPal+")

st.markdown(
    """
Welcome to the PawPal+ starter app.

This file is intentionally thin. It gives you a working Streamlit app so you can start quickly,
but **it does not implement the project logic**. Your job is to design the system and build it.

Use this app as your interactive demo once your backend classes/functions exist.
"""
)

with st.expander("Scenario", expanded=True):
    st.markdown(
        """
**PawPal+** is a pet care planning assistant. It helps a pet owner plan care tasks
for their pet(s) based on constraints like time, priority, and preferences.

You will design and implement the scheduling logic and connect it to this Streamlit UI.
"""
    )

with st.expander("What you need to build", expanded=True):
    st.markdown(
        """
At minimum, your system should:
- Represent pet care tasks (what needs to happen, how long it takes, priority)
- Represent the pet and the owner (basic info and preferences)
- Build a plan/schedule for a day that chooses and orders tasks based on constraints
- Explain the plan (why each task was chosen and when it happens)
"""
    )

st.divider()

st.subheader("Quick Demo Inputs (UI only)")
owner_name = st.text_input("Owner name", value=st.session_state.owner.name)
pet_name = st.text_input("Pet name", value="Mochi")
species = st.selectbox("Species", ["dog", "cat", "other"])
age = st.number_input("Pet age", min_value=0, max_value=30, value=2)

if st.button("Add Pet"):
    new_pet = Pet(name=pet_name, species=species, age=age)
    st.session_state.owner.add_pet(new_pet)
    st.success(f"Added pet: {pet_name}")

# Display current pets
if st.session_state.owner.pets:
    st.write("Current pets:")
    pet_data = [{"Name": p.name, "Species": p.species, "Age": p.age} for p in st.session_state.owner.pets]
    st.table(pet_data)
else:
    st.info("No pets added yet.")

st.markdown("### Tasks")
st.caption("Add a few tasks. In your final version, these should feed into your scheduler.")

if "tasks" not in st.session_state:
    st.session_state.tasks = []

col1, col2, col3 = st.columns(3)
with col1:
    task_title = st.text_input("Task title", value="Morning walk")
with col2:
    duration = st.number_input("Duration (minutes)", min_value=1, max_value=240, value=20)
with col3:
    priority = st.selectbox("Priority", ["low", "medium", "high"], index=2)

if st.button("Add task"):
    st.session_state.tasks.append(
        {"title": task_title, "duration_minutes": int(duration), "priority": priority}
    )

if st.session_state.tasks:
    st.write("Current tasks:")
    st.table(st.session_state.tasks)
else:
    st.info("No tasks yet. Add one above.")

st.divider()

st.subheader("Build Schedule")
st.caption("Generate a daily schedule based on your pets' tasks.")

if st.button("Generate schedule"):
    plan, reasoning = st.session_state.scheduler.generate_plan()
    if plan:
        st.success("Schedule generated!")
        st.write("**Reasoning:**", reasoning)
        st.write("**Today's Schedule:**")
        schedule_data = [
            {"Task": t.description, "Duration": f"{t.duration} min", "Priority": t.priority, "Pet": t.pet_name or "N/A"}
            for t in plan
        ]
        st.table(schedule_data)
    else:
        st.info("No tasks to schedule or no time available.")
