"""
main.py — CLI demo script to verify PawPal+ backend logic.
Run with: python main.py
"""

from pawpal_system import Owner, Pet, Task, Scheduler
from datetime import datetime

TODAY = datetime.today().strftime("%Y-%m-%d")

# ── Setup ──────────────────────────────────────
owner = Owner(name="Jordan")

mochi = Pet(name="Mochi", species="cat")
rex   = Pet(name="Rex",   species="dog")

owner.add_pet(mochi)
owner.add_pet(rex)

# ── Tasks (intentionally out of order) ─────────
mochi.add_task(Task("Evening meds",   "19:00", 5,  "high",   "daily",  due_date=TODAY))
mochi.add_task(Task("Morning feeding","08:00", 10, "high",   "daily",  due_date=TODAY))
mochi.add_task(Task("Enrichment play","14:00", 20, "medium", "weekly", due_date=TODAY))

rex.add_task(Task("Morning walk",     "07:30", 30, "high",   "daily",  due_date=TODAY))
rex.add_task(Task("Afternoon walk",   "16:00", 30, "medium", "daily",  due_date=TODAY))
# Conflict: same time as Mochi's evening meds
rex.add_task(Task("Flea medication",  "19:00", 5,  "high",   "weekly", due_date=TODAY))

# ── Scheduler ──────────────────────────────────
sched = Scheduler(owner)

# Today's sorted schedule + conflict warnings
print(sched.todays_summary())

# ── Demo: mark complete + recurrence ───────────
print("\n--- Completing 'Morning walk' (daily) ---")
print(sched.mark_task_complete("Rex", "Morning walk"))
rex_tasks = [str(t) for t in rex.tasks]
print("Rex's tasks after completion:")
for t in rex_tasks:
    print(" ", t)

# ── Demo: filter incomplete tasks ──────────────
print("\n--- Incomplete tasks ---")
for pet, task in sched.filter_by_status(completed=False):
    print(f"  {pet.name}: {task.title}")

# ── Demo: priority sort ─────────────────────────
print("\n--- All tasks sorted by priority → time ---")
for pet, task in sched.sort_by_priority(sched.owner.get_all_tasks()):
    print(f"  [{task.priority:6}] {pet.name}: {task}")