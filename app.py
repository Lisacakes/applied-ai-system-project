"""
app.py — PawPal+ Streamlit UI
Includes: JSON persistence, priority-based scheduling with color coding.
"""

import os
import streamlit as st
from pawpal_system import Owner, Pet, Task, Scheduler

DATA_FILE = "data.json"
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}

st.set_page_config(page_title="PawPal+", page_icon="🐾", layout="centered")
st.title("PawPal+")

# ── Session state bootstrap (load from JSON if available) ────────────────────
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
            st.session_state.scheduler = Scheduler(st.session_state.owner)
        except Exception:
            st.session_state.owner = None
            st.session_state.scheduler = None
    else:
        st.session_state.owner = None
        st.session_state.scheduler = None

def save():
    """Persist current state to disk after every mutation."""
    if st.session_state.owner:
        st.session_state.owner.save_to_json(DATA_FILE)

def get_sched() -> Scheduler:
    return st.session_state.scheduler

# ── Step 1: Owner setup ───────────────────────────────────────────────────────
st.subheader(" Owner Setup")

if st.session_state.owner:
    st.success(f"Loaded saved data for **{st.session_state.owner.name}**.")
    if st.button("Start fresh (clear saved data)"):
        if os.path.exists(DATA_FILE):
            os.remove(DATA_FILE)
        st.session_state.owner = None
        st.session_state.scheduler = None
        st.rerun()
else:
    with st.form("owner_form"):
        owner_name = st.text_input("Your name", value="Jordan")
        if st.form_submit_button("Set owner"):
            st.session_state.owner = Owner(name=owner_name)
            st.session_state.scheduler = Scheduler(st.session_state.owner)
            save()
            st.success(f"Welcome, {owner_name}!")

if st.session_state.owner is None:
    st.info("Enter your name above to get started.")
    st.stop()

owner: Owner = st.session_state.owner
sched: Scheduler = get_sched()

# ── Step 2: Add a pet ─────────────────────────────────────────────────────────
st.divider()
st.subheader("Manage Pets")

with st.form("add_pet_form"):
    c1, c2 = st.columns(2)
    pet_name = c1.text_input("Pet name")
    species  = c2.selectbox("Species", ["dog", "cat", "rabbit", "bird", "other"])
    if st.form_submit_button("Add pet"):
        if pet_name.strip():
            if owner.get_pet(pet_name):
                st.warning(f"'{pet_name}' already exists.")
            else:
                owner.add_pet(Pet(name=pet_name.strip(), species=species))
                save()
                st.success(f"Added {pet_name} the {species}!")
        else:
            st.error("Pet name can't be empty.")

if owner.pets:
    st.write("**Your pets:**")
    for p in owner.pets:
        st.write(f"- {p.name} ({p.species}) — {p.task_count()} task(s)")
else:
    st.info("No pets yet — add one above.")

# ── Step 3: Add a task ────────────────────────────────────────────────────────
st.divider()
st.subheader("Add a Task")

if not owner.pets:
    st.info("Add a pet first before scheduling tasks.")
else:
    with st.form("add_task_form"):
        pet_choice = st.selectbox("Assign to pet", [p.name for p in owner.pets])
        t_title = st.text_input("Task title", value="Morning walk")
        c1, c2, c3, c4 = st.columns(4)
        t_time = c1.text_input("Time (HH:MM)", value="08:00")
        t_dur  = c2.number_input("Duration (min)", 1, 240, 20)
        t_pri  = c3.selectbox("Priority", ["high", "medium", "low"])
        t_freq = c4.selectbox("Frequency", ["once", "daily", "weekly"])
        t_date = st.date_input("Date")

        if st.form_submit_button("Add task"):
            try:
                h, m = t_time.split(":")
                assert 0 <= int(h) <= 23 and 0 <= int(m) <= 59
            except Exception:
                st.error("Use HH:MM format (e.g. 08:30).")
            else:
                pet = owner.get_pet(pet_choice)
                pet.add_task(Task(
                    title=t_title.strip(),
                    time=t_time,
                    duration_minutes=int(t_dur),
                    priority=t_pri,
                    frequency=t_freq,
                    due_date=str(t_date),
                ))
                save()
                st.success(f"Task '{t_title}' added to {pet_choice}!")

# ── Step 4: Generate schedule ─────────────────────────────────────────────────
st.divider()
st.subheader("Today's Schedule")

sort_mode = st.radio(
    "Sort by",
    ["Time (chronological)", "Priority → Time"],
    horizontal=True,
)

if st.button("Generate schedule"):
    pairs = sched.get_todays_schedule()
    conflicts = sched.detect_conflicts()

    for w in conflicts:
        st.warning(w)

    if sort_mode == "Priority → Time":
        pairs = sched.sort_by_priority_then_time(pairs)

    if not pairs:
        st.info("No tasks scheduled for today.")
    else:
        rows = []
        for pet, task in pairs:
            rows.append({
                "Priority":  f"{PRIORITY_EMOJI.get(task.priority, '')} {task.priority}",
                "Pet":       pet.name,
                "Task":      task.title,
                "Time":      task.time,
                "Duration":  f"{task.duration_minutes} min",
                "Frequency": task.frequency,
                "Status":    "Done" if task.completed else "Pending",
            })
        st.table(rows)

# ── Step 5: Mark task complete ────────────────────────────────────────────────
st.divider()
st.subheader("Mark Task Complete")

if owner.pets:
    c1, c2 = st.columns(2)
    comp_pet  = c1.selectbox("Pet", [p.name for p in owner.pets], key="comp_pet")
    comp_task = c2.text_input("Task title", key="comp_task")
    if st.button("Mark complete"):
        msg = sched.mark_task_complete(comp_pet, comp_task)
        if msg.startswith("✅"):
            save()
            st.success(msg)
        else:
            st.error(msg)

# ── Step 6: Filter view ───────────────────────────────────────────────────────
st.divider()
st.subheader("Filter Tasks")

col1, col2, col3 = st.columns(3)
filter_pet      = col1.selectbox("Pet",      ["All"] + [p.name for p in owner.pets], key="fp")
filter_status   = col2.selectbox("Status",   ["All", "Pending", "Completed"], key="fs")
filter_priority = col3.selectbox("Priority", ["All", "high", "medium", "low"], key="fpr")

if st.button("Apply filters"):
    pairs = owner.get_all_tasks()
    if filter_pet != "All":
        pairs = [(p, t) for p, t in pairs if p.name == filter_pet]
    if filter_status == "Pending":
        pairs = [(p, t) for p, t in pairs if not t.completed]
    elif filter_status == "Completed":
        pairs = [(p, t) for p, t in pairs if t.completed]
    if filter_priority != "All":
        pairs = [(p, t) for p, t in pairs if t.priority == filter_priority]

    pairs = sched.sort_by_priority_then_time(pairs)

    if not pairs:
        st.info("No tasks match those filters.")
    else:
        rows = [
            {
                "Priority": f"{PRIORITY_EMOJI.get(t.priority, '')} {t.priority}",
                "Pet": p.name, "Task": t.title, "Time": t.time,
                "Date": t.due_date, "Status": "✅" if t.completed else "⏳",
            }
            for p, t in pairs
        ]
        st.table(rows)