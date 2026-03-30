"""
pytest suite for PawPal+ core logic.
Run with: python -m pytest test_pawpal.py -v
"""

import pytest
from datetime import datetime, timedelta
from pawpal_system import Owner, Pet, Task, Scheduler

TODAY = datetime.today().strftime("%Y-%m-%d")
TOMORROW = (datetime.today() + timedelta(days=1)).strftime("%Y-%m-%d")


@pytest.fixture
def sample_owner():
    owner = Owner("Jordan")
    mochi = Pet("Mochi", "cat")
    rex   = Pet("Rex",   "dog")
    mochi.add_task(Task("Evening meds",    "19:00", 5,  "high",   "daily",  due_date=TODAY))
    mochi.add_task(Task("Morning feeding", "08:00", 10, "high",   "daily",  due_date=TODAY))
    rex.add_task(Task("Morning walk",      "07:30", 30, "high",   "daily",  due_date=TODAY))
    rex.add_task(Task("Afternoon walk",    "16:00", 30, "medium", "once",   due_date=TODAY))
    owner.add_pet(mochi)
    owner.add_pet(rex)
    return owner


# ── Task completion ─────────────────────────────

def test_mark_complete_changes_status(sample_owner):
    task = sample_owner.get_pet("Mochi").tasks[0]
    task.mark_complete()
    assert task.completed is True


def test_mark_complete_returns_none_for_once():
    task = Task("Vet visit", "10:00", 60, frequency="once", due_date=TODAY)
    result = task.mark_complete()
    assert result is None


# ── Pet task count ──────────────────────────────

def test_add_task_increases_count():
    pet = Pet("Buddy", "dog")
    assert pet.task_count() == 0
    pet.add_task(Task("Walk", "09:00", 20, due_date=TODAY))
    assert pet.task_count() == 1


# ── Sorting ─────────────────────────────────────

def test_sort_by_time_is_chronological(sample_owner):
    sched = Scheduler(sample_owner)
    pairs = sched.get_all_sorted()
    times = [task.time for _, task in pairs]
    assert times == sorted(times)


# ── Recurrence ──────────────────────────────────

def test_daily_task_reschedules_to_tomorrow():
    task = Task("Morning meds", "08:00", 5, frequency="daily", due_date=TODAY)
    next_task = task.mark_complete()
    assert next_task is not None
    assert next_task.due_date == TOMORROW
    assert next_task.completed is False


def test_weekly_task_reschedules_7_days():
    task = Task("Bath time", "11:00", 30, frequency="weekly", due_date=TODAY)
    next_task = task.mark_complete()
    expected = (datetime.today() + timedelta(weeks=1)).strftime("%Y-%m-%d")
    assert next_task.due_date == expected


# ── Conflict detection ──────────────────────────

def test_conflict_detected_for_same_time(sample_owner):
    # Add a second pet with a task at the same time as Mochi's 19:00
    rex = sample_owner.get_pet("Rex")
    rex.add_task(Task("Flea meds", "19:00", 5, due_date=TODAY))
    sched = Scheduler(sample_owner)
    warnings = sched.detect_conflicts()
    assert len(warnings) >= 1
    assert "19:00" in warnings[0]


def test_no_conflict_when_times_differ(sample_owner):
    sched = Scheduler(sample_owner)
    # Default fixture has no overlapping times
    warnings = sched.detect_conflicts()
    assert warnings == []


# ── Filtering ───────────────────────────────────

def test_filter_incomplete_returns_only_pending(sample_owner):
    sched = Scheduler(sample_owner)
    sample_owner.get_pet("Mochi").tasks[0].completed = True
    pending = sched.filter_by_status(completed=False)
    assert all(not task.completed for _, task in pending)


def test_filter_by_pet_name(sample_owner):
    sched = Scheduler(sample_owner)
    mochi_tasks = sched.filter_by_pet("Mochi")
    assert all(pet.name == "Mochi" for pet, _ in mochi_tasks)


# ── Priority scheduling ──────────────────────────────────────────────────────

def test_priority_sort_high_before_low():
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("Low task",  "07:00", 10, priority="low",  due_date=TODAY))
    pet.add_task(Task("High task", "09:00", 10, priority="high", due_date=TODAY))
    owner.add_pet(pet)
    sched = Scheduler(owner)
    pairs = sched.sort_by_priority_then_time(owner.get_all_tasks())
    assert pairs[0][1].priority == "high"


def test_priority_sort_tiebreak_by_time():
    owner = Owner("Test")
    pet = Pet("Buddy", "dog")
    pet.add_task(Task("High late",  "10:00", 10, priority="high", due_date=TODAY))
    pet.add_task(Task("High early", "08:00", 10, priority="high", due_date=TODAY))
    owner.add_pet(pet)
    sched = Scheduler(owner)
    pairs = sched.sort_by_priority_then_time(owner.get_all_tasks())
    assert pairs[0][1].title == "High early"


# ── JSON persistence ─────────────────────────────────────────────────────────

def test_save_and_load_roundtrip(tmp_path, sample_owner):
    filepath = str(tmp_path / "test_data.json")
    sample_owner.save_to_json(filepath)
    loaded = Owner.load_from_json(filepath)
    assert loaded.name == sample_owner.name
    assert len(loaded.pets) == len(sample_owner.pets)
    orig_tasks  = sum(p.task_count() for p in sample_owner.pets)
    loaded_tasks = sum(p.task_count() for p in loaded.pets)
    assert orig_tasks == loaded_tasks


def test_load_preserves_task_fields(tmp_path, sample_owner):
    filepath = str(tmp_path / "test_data.json")
    sample_owner.save_to_json(filepath)
    loaded = Owner.load_from_json(filepath)
    orig_task   = sample_owner.get_pet("Mochi").tasks[0]
    loaded_task = loaded.get_pet("Mochi").tasks[0]
    assert loaded_task.title    == orig_task.title
    assert loaded_task.priority == orig_task.priority
    assert loaded_task.frequency == orig_task.frequency