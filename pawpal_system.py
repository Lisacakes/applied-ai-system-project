from dataclasses import dataclass, field
from datetime import datetime, timedelta
from typing import Optional, List, Tuple, Dict, Any

# ───────────── Task ─────────────

@dataclass
class Task:
    title: str
    time: str
    duration_minutes: int
    priority: str = "medium"
    frequency: str = "once"
    completed: bool = False
    due_date: str = field(default_factory=lambda: datetime.today().strftime("%Y-%m-%d"))

    def mark_complete(self) -> Optional["Task"]:
        self.completed = True
        if self.frequency == "daily":
            next_date = (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(days=1)).strftime("%Y-%m-%d")
            return Task(self.title, self.time, self.duration_minutes, self.priority, self.frequency, due_date=next_date)
        if self.frequency == "weekly":
            next_date = (datetime.strptime(self.due_date, "%Y-%m-%d") + timedelta(weeks=1)).strftime("%Y-%m-%d")
            return Task(self.title, self.time, self.duration_minutes, self.priority, self.frequency, due_date=next_date)
        return None

    def to_dict(self) -> Dict[str, Any]:
        return {
            "title": self.title, "time": self.time, "duration_minutes": self.duration_minutes,
            "priority": self.priority, "frequency": self.frequency, "completed": self.completed, "due_date": self.due_date,
        }

    @classmethod
    def from_dict(cls, d: Dict[str, Any]) -> "Task":
        return cls(
            title=d["title"], time=d["time"], duration_minutes=d.get("duration_minutes", 30),
            priority=d.get("priority", "medium"), frequency=d.get("frequency", "once"),
            completed=d.get("completed", False), due_date=d.get("due_date", datetime.today().strftime("%Y-%m-%d")),
        )

# ───────────── Pet ─────────────

@dataclass
class Pet:
    name: str
    species: str
    tasks: List[Task] = field(default_factory=list)

    def add_task(self, task: Task):
        self.tasks.append(task)

    def remove_task(self, title: str, time: str) -> bool:
        """Added: Required for the delete button in your UI"""
        for t in self.tasks:
            if t.title.lower() == title.lower() and t.time == time:
                self.tasks.remove(t)
                return True
        return False

    def to_dict(self):
        return {"name": self.name, "species": self.species, "tasks": [t.to_dict() for t in self.tasks]}

    @classmethod
    def from_dict(cls, d):
        pet = cls(d["name"], d["species"])
        pet.tasks = [Task.from_dict(t) for t in d.get("tasks", [])]
        return pet

# ───────────── Owner ─────────────

@dataclass
class Owner:
    name: str
    pets: List[Pet] = field(default_factory=list)

    def add_pet(self, pet: Pet):
        if not any(p.name.lower() == pet.name.lower() for p in self.pets):
            self.pets.append(pet)

    def remove_pet(self, name: str) -> bool:
        """Added: Required to manage your profile"""
        initial_count = len(self.pets)
        self.pets = [p for p in self.pets if p.name.lower() != name.lower()]
        return len(self.pets) < initial_count

    def get_pet(self, name: str) -> Optional[Pet]:
        return next((p for p in self.pets if p.name.lower() == name.lower()), None)

    def get_all_tasks(self) -> List[Tuple[Pet, Task]]:
        return [(p, t) for p in self.pets for t in p.tasks]

    def to_dict(self):
        return {"name": self.name, "pets": [p.to_dict() for p in self.pets]}

    @classmethod
    def from_dict(cls, d):
        owner = cls(d["name"])
        owner.pets = [Pet.from_dict(p) for p in d.get("pets", [])]
        return owner

    def save_to_json(self, path="data.json"):
        import json
        with open(path, "w", encoding="utf-8") as f:
            json.dump(self.to_dict(), f, indent=2)

    @classmethod
    def load_from_json(cls, path="data.json"):
        import json
        with open(path, "r", encoding="utf-8") as f:
            return cls.from_dict(json.load(f))

# ───────────── Scheduler ─────────────

class Scheduler:
    def __init__(self, owner: Owner):
        self.owner = owner

    def get_all_sorted(self) -> List[Tuple[Pet, Task]]:
        """Added: Required for the 'Daily Schedule' display"""
        return sorted(self.owner.get_all_tasks(), key=lambda x: x[1].time)

    def filter_by_status(self, completed: bool):
        """Added: Required for your unit tests"""
        return [(p, t) for p, t in self.owner.get_all_tasks() if t.completed == completed]

    def filter_by_pet(self, pet_name: str):
        """Added: Required for your unit tests"""
        return [(p, t) for p, t in self.owner.get_all_tasks() if p.name.lower() == pet_name.lower()]

    def get_todays(self):
        today = datetime.today().strftime("%Y-%m-%d")
        return sorted(
            [(p, t) for p, t in self.owner.get_all_tasks() if t.due_date == today],
            key=lambda x: x[1].time
        )