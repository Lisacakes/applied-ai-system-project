"""
PawPal+ — backend logic layer.
Classes: Task, Pet, Owner, Scheduler
"""

from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional


# ─────────────────────────────────────────────
# Task
# ─────────────────────────────────────────────

@dataclass
class Task:
    """A single care activity for a pet."""
    title: str
    time: str                          # "HH:MM" 24-hour format
    duration_minutes: int
    priority: str = "medium"           # "low" | "medium" | "high"
    frequency: str = "once"            # "once" | "daily" | "weekly"
    completed: bool = False
    due_date: str = field(default_factory=lambda: datetime.today().strftime("%Y-%m-%d"))

    def mark_complete(self) -> Optional["Task"]:
        """Mark this task complete and return a rescheduled copy if recurring."""
        self.completed = True
        if self.frequency == "daily":
            next_date = (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            return Task(self.title, self.time, self.duration_minutes, self.priority, self.frequency, due_date=next_date)
        if self.frequency == "weekly":
            next_date = (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(weeks=1)).strftime("%Y-%m-%d")
            return Task(self.title, self.time, self.duration_minutes, self.priority, self.frequency, due_date=next_date)
        return None

    def __str__(self):
        status = "✅" if self.completed else "⏳"
        return f"{status} [{self.time}] {self.title} ({self.duration_minutes}min, {self.priority}, {self.frequency})"


# ─────────────────────────────────────────────
# Pet
# ─────────────────────────────────────────────

@dataclass
class Pet:
    """A pet belonging to an owner."""
    name: str
    species: str
    tasks: list = field(default_factory=list)

    def add_task(self, task: Task) -> None:
        """Add a task to this pet's task list."""
        self.tasks.append(task)

    def remove_task(self, title: str) -> bool:
        """Remove a task by title. Returns True if found and removed."""
        for t in self.tasks:
            if t.title.lower() == title.lower():
                self.tasks.remove(t)
                return True
        return False

    def task_count(self) -> int:
        """Return total number of tasks."""
        return len(self.tasks)

    def __str__(self):
        return f"{self.name} ({self.species}) — {self.task_count()} task(s)"


# ─────────────────────────────────────────────
# Owner
# ─────────────────────────────────────────────

@dataclass
class Owner:
    """An owner who manages one or more pets."""
    name: str
    pets: list = field(default_factory=list)

    def add_pet(self, pet: Pet) -> None:
        """Add a pet to the owner's roster."""
        self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Remove a pet by name. Returns True if found."""
        for p in self.pets:
            if p.name.lower() == name.lower():
                self.pets.remove(p)
                return True
        return False

    def get_all_tasks(self) -> list[tuple[Pet, Task]]:
        """Return all (pet, task) pairs across every pet."""
        return [(pet, task) for pet in self.pets for task in pet.tasks]

    def get_pet(self, name: str) -> Optional[Pet]:
        """Look up a pet by name."""
        for p in self.pets:
            if p.name.lower() == name.lower():
                return p
        return None
    
        # ── Persistence ────────────────────────────

    def save_to_json(self, filepath: str = "data.json") -> None:
        """Serialise owner, pets, and tasks to a JSON file."""
        import json
        data = {
            "name": self.name,
            "pets": [
                {
                    "name": pet.name,
                    "species": pet.species,
                    "tasks": [
                        {
                            "title": t.title,
                            "time": t.time,
                            "duration_minutes": t.duration_minutes,
                            "priority": t.priority,
                            "frequency": t.frequency,
                            "completed": t.completed,
                            "due_date": t.due_date,
                        }
                        for t in pet.tasks
                    ],
                }
                for pet in self.pets
            ],
        }
        with open(filepath, "w") as f:
            json.dump(data, f, indent=2)

    @classmethod
    def load_from_json(cls, filepath: str = "data.json") -> "Owner":
        """Deserialise an Owner (with pets and tasks) from a JSON file."""
        import json
        with open(filepath, "r") as f:
            data = json.load(f)
        owner = cls(name=data["name"])
        for pd in data["pets"]:
            pet = Pet(name=pd["name"], species=pd["species"])
            for td in pd["tasks"]:
                pet.add_task(Task(**td))
            owner.add_pet(pet)
        return owner



# ─────────────────────────────────────────────
# Scheduler
# ─────────────────────────────────────────────

PRIORITY_ORDER = {"high": 0, "medium": 1, "low": 2}
PRIORITY_EMOJI = {"high": "🔴", "medium": "🟡", "low": "🟢"}


class Scheduler:
    """Organises, sorts, filters, and validates tasks across all pets."""

    def __init__(self, owner: Owner):
        """Initialise with an Owner instance."""
        self.owner = owner

    # ── Retrieval ──────────────────────────────

    def get_todays_schedule(self) -> list[tuple[Pet, Task]]:
        """Return all tasks for today, sorted by time."""
        today = datetime.today().strftime("%Y-%m-%d")
        pairs = [(pet, task) for pet, task in self.owner.get_all_tasks()
                 if task.due_date == today]
        return self.sort_by_time(pairs)

    def get_all_sorted(self) -> list[tuple[Pet, Task]]:
        """Return every task across all dates, sorted by time."""
        return self.sort_by_time(self.owner.get_all_tasks())

    # ── Sorting ────────────────────────────────

    def sort_by_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort (pet, task) pairs by task time in HH:MM format."""
        return sorted(pairs, key=lambda pt: pt[1].time)

    def sort_by_priority(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """Sort by priority (high → medium → low), then by time."""
        return sorted(pairs, key=lambda pt: (PRIORITY_ORDER.get(pt[1].priority, 1), pt[1].time))
    
    def sort_by_priority_then_time(self, pairs: list[tuple[Pet, Task]]) -> list[tuple[Pet, Task]]:
        """
        Priority-based scheduling: high tasks always surface first.
        Within the same priority tier, tasks are ordered chronologically.
        Ties in both priority and time are broken alphabetically by task title.
        """
        return sorted(
            pairs,
            key=lambda pt: (
                PRIORITY_ORDER.get(pt[1].priority, 1),
                pt[1].time,
                pt[1].title.lower(),
            ),
        )


    # ── Filtering ──────────────────────────────

    def filter_by_status(self, completed: bool) -> list[tuple[Pet, Task]]:
        """Filter tasks by completion status."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks()
                if task.completed == completed]

    def filter_by_pet(self, pet_name: str) -> list[tuple[Pet, Task]]:
        """Filter tasks to a single pet by name."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks()
                if pet.name.lower() == pet_name.lower()]

    def filter_by_priority(self, priority: str) -> list[tuple[Pet, Task]]:
        """Filter tasks by priority level."""
        return [(pet, task) for pet, task in self.owner.get_all_tasks()
                if task.priority == priority]

    # ── Conflict Detection ─────────────────────

    def detect_conflicts(self) -> list[str]:
        """
        Return warning strings for any two tasks sharing the same time slot
        on the same date (across all pets).
        """
        warnings = []
        all_tasks = self.owner.get_all_tasks()
        seen: dict[tuple, list] = {}

        for pet, task in all_tasks:
            key = (task.due_date, task.time)
            seen.setdefault(key, []).append((pet.name, task.title))

        for (date, time), entries in seen.items():
            if len(entries) > 1:
                names = ", ".join(f"{p}: {t}" for p, t in entries)
                warnings.append(f"⚠️ Conflict on {date} at {time} → {names}")

        return warnings

    # ── Task Completion (with recurrence) ──────

    def mark_task_complete(self, pet_name: str, task_title: str) -> str:
        """
        Mark a task complete. If recurring, auto-schedules the next occurrence.
        Returns a status message.
        """
        pet = self.owner.get_pet(pet_name)
        if not pet:
            return f"Pet '{pet_name}' not found."
        for task in pet.tasks:
            if task.title.lower() == task_title.lower() and not task.completed:
                next_task = task.mark_complete()
                if next_task:
                    pet.add_task(next_task)
                    return f"✅ '{task.title}' complete. Next occurrence added for {next_task.due_date}."
                return f"✅ '{task.title}' marked complete."
        return f"Task '{task_title}' not found or already complete."

    # ── Schedule Summary ───────────────────────

    def todays_summary(self) -> str:
        """Return a formatted CLI string of today's schedule."""
        pairs = self.get_todays_schedule()
        conflicts = self.detect_conflicts()
        lines = [f"📅 Today's Schedule for {self.owner.name}", "─" * 40]
        if not pairs:
            lines.append("No tasks scheduled for today.")
        for pet, task in pairs:
            lines.append(f"  {pet.name:10} {task}")
        if conflicts:
            lines.append("")
            lines.extend(conflicts)
        return "\n".join(lines)