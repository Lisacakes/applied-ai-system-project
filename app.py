import streamlit as st
import os, time
from services import PetService
from ai_helper import PetSafetyAI
from pawpal_system import Owner, Pet, Task, Scheduler

# Configuration for data storage
DATA_FILE, LOG_FILE = "data.json", "blocked_log.json"
st.set_page_config(page_title="PawPal+ Pro", page_icon="🐾", layout="wide")

@st.cache_data
def load_logs(path, ver):
    """Retrieves the last 20 safety audit logs."""
    return PetService.get_tail_logs(path)

# --- 1. DATA INITIALIZATION ---
# Checks if an owner already exists in the JSON database
if "owner" not in st.session_state:
    if os.path.exists(DATA_FILE):
        try:
            st.session_state.owner = Owner.load_from_json(DATA_FILE)
        except:
            st.session_state.owner = None
    else:
        st.session_state.owner = None

# Initializes the AI layer once per session
if "ai" not in st.session_state:
    st.session_state.ai = PetSafetyAI()

st.title("PawPal+ Pro")

# --- 2. REGISTRATION (Initial Setup) ---
# If no owner is found, force the user to register
if not st.session_state.owner:
    st.info("Welcome! Create your profile to begin.")
    with st.form("reg"):
        o_name = st.text_input("Owner Name", "Lisa")
        p_name = st.text_input("Pet Name", "Lori")
        p_spec = st.selectbox("Species", ["Dog", "Cat", "Other"])
        if st.form_submit_button("Register"):
            new_owner = Owner(name=o_name)
            new_owner.add_pet(Pet(name=p_name, species=p_spec))
            new_owner.save_to_json(DATA_FILE)
            st.session_state.owner = new_owner
            st.rerun()
    st.stop()

owner = st.session_state.owner

# --- 3. SIDEBAR (Manage Pets) ---
# Allows the user to add multiple pets like Cami
with st.sidebar:
    st.header("🐾 My Pets")
    for p in owner.pets:
        st.write(f"**{p.name}** ({p.species})")
    
    st.divider()
    if not st.session_state.ai.rules_loaded:
        st.warning("⚠️ RAG Layer Offline: Using Hard Rules only.")
    
    with st.expander("➕ Add Another Pet"):
        with st.form("add_pet_form", clear_on_submit=True):
            new_p_name = st.text_input("Pet Name")
            new_p_spec = st.selectbox("Species", ["Dog", "Cat", "Bird", "Other"], key="new_spec")
            if st.form_submit_button("Add Pet"):
                if new_p_name:
                    owner.add_pet(Pet(name=new_p_name, species=new_p_spec))
                    PetService.atomic_save(owner.to_dict(), DATA_FILE)
                    st.success(f"Added {new_p_name}!")
                    st.rerun()

# --- 4. MAIN TASK UI ---
with st.form("task"):
    p_sel = st.selectbox("Select Pet", [x.name for x in owner.pets])
    title_in = st.text_input("What is the task? (e.g., Give Lori grapes)").strip()
    t_in = st.text_input("Time (HH:MM)", "08:00")
    d_in = st.number_input("Duration (mins)", 1, 480, 30)

    if st.form_submit_button("Add to Schedule"):
        # Basic field validation
        ok, err, norm = PetService.validate_and_normalize(title_in, t_in, d_in)
        if not ok:
            st.error(err)
        else:
            pet = owner.get_pet(p_sel)
            ai = st.session_state.ai
            
            # The Safety Gatekeeper
            res = ai.check_task_safety(norm) if ai else "SAFE"
            
            # THE FINAL GATE: Deterministic strictness
            if res.strip().upper() == "SAFE":
                pet.add_task(Task(title_in, t_in, d_in))
                PetService.atomic_save(owner.to_dict(), DATA_FILE)
                st.success(f"Added '{title_in}'!")
                st.rerun()
            else:
                # Log and block everything that isn't SAFE
                PetService.append_log({"task": title_in, "reason": res, "pet": p_sel}, LOG_FILE)
                st.session_state["log_ver"] = time.time()
                st.error(f"🛑 {res}")

# --- 5. SCHEDULE VIEW ---
st.divider()
st.subheader("Daily Schedule")
sched = Scheduler(owner)
all_tasks = sched.get_all_sorted()

if not all_tasks:
    st.info("No tasks scheduled yet.")
else:
    for pet, task in all_tasks:
        c1, c2, c3, c4 = st.columns([1, 3, 1, 1])
        c1.write(f"**{task.time}**")
        c2.write(f"{pet.name}: {task.title}")
        if c3.button("Done", key=f"do_{task.time}_{task.title}"):
            task.mark_complete()
            PetService.atomic_save(owner.to_dict(), DATA_FILE)
            st.rerun()
        if c4.button("🗑️", key=f"del_{task.time}_{task.title}"):
            pet.remove_task(task.title, task.time)
            PetService.atomic_save(owner.to_dict(), DATA_FILE)
            st.rerun()

# --- 6. AUDIT LOGS ---
# Observability: Tracks blocked dangerous tasks
logs = load_logs(LOG_FILE, st.session_state.get("log_ver", 0))
if logs:
    with st.expander("Safety Audit Logs (RAG History)"):
        st.table(logs)