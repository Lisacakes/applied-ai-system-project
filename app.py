import streamlit as st
import os
import time
from services import PetService
from ai_helper import PetSafetyAI
from pawpal_system import Owner, Task

DATA_FILE, LOG_FILE = "data.json", "blocked_log.json"
st.set_page_config(page_title="PawPal+ Pro", page_icon="")

@st.cache_data(show_spinner=False)
def load_logs_cached(file_path: str, version_token: float):
    return PetService.get_tail_logs(file_path)

# --- 1. State Initialization ---
if "owner" not in st.session_state and os.path.exists(DATA_FILE):
    try:
        st.session_state.owner = Owner.load_from_json(DATA_FILE)
    except Exception as e:
        st.sidebar.error(f"Data Recovery Failed: {e}")

owner = st.session_state.get("owner")

if "safety_ai" not in st.session_state:
    try:
        st.session_state.safety_ai = PetSafetyAI()
    except Exception as e:
        st.session_state.safety_ai = None
        st.sidebar.error(f"AI Safety System Offline: {e}")

st.title("PawPal+ Pro")

if owner and owner.pets:
    with st.form("task_entry", clear_on_submit=True):
        p_name = st.selectbox("Pet", [p.name for p in owner.pets])
        title_raw = st.text_input("Task Title").strip()
        t_time = st.text_input("Time (HH:MM)", "08:00")
        
        ai = st.session_state.get("safety_ai")
        bypass = False
        if not ai:
            st.warning("Safety System Offline.")
            bypass = st.checkbox("Manual Bypass")

        if st.form_submit_button("Add Task"):
            is_valid, err, title = PetService.validate_and_normalize(title_raw, t_time)
            
            if not is_valid:
                st.error(err)
            else:
                pet = owner.get_pet(p_name)
                if any(t.title.lower() == title and t.time == t_time for t in pet.tasks):
                    st.error("Duplicate task detected.")
                else:
                    try:
                        raw_res = str(ai.check_task_safety(title) if ai else "OFFLINE").strip()
                    except Exception as e:
                        raw_res = f"AI_ERROR: {str(e)}"
                    
                    is_safe = raw_res.upper().startswith("SAFE")
                    is_err = raw_res == "OFFLINE" or raw_res.startswith("AI_ERROR")
                    
                    if is_safe or (bypass and is_err):
                        pet.add_task(Task(title=title_raw, time=t_time))
                        PetService.atomic_save(owner.to_dict(), DATA_FILE)
                        st.success(f"Added '{title_raw}'!")
                        st.rerun()
                    else:
                        log_entry = {"task": title_raw, "reason": raw_res, "pet": p_name}
                        PetService.append_log(log_entry, LOG_FILE)
                        st.session_state["log_ver"] = time.time()
                        st.error(f"Blocked: {raw_res}")

# --- Observability Dashboard ---
log_ver = st.session_state.get("log_ver", 0)
logs = load_logs_cached(LOG_FILE, log_ver)
if logs:
    with st.expander("Safety Audit Logs (Historical)"):
        st.table(logs)