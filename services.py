import json, os, re, logging
from collections import deque
from typing import Tuple, List, Dict, Any

TIME_PATTERN = re.compile(r"^(0[0-9]|1[0-9]|2[0-3]):[0-5][0-9]$")


class PetService:

    @staticmethod
    def validate_and_normalize(title: str, t_time: str, duration: int) -> Tuple[bool, str, str]:
        clean = " ".join(title.split()).lower()

        if not clean or len(clean) > 100:
            return False, "Invalid title.", ""
        if not TIME_PATTERN.match(t_time):
            return False, "Invalid time format.", ""
        if duration <= 0 or duration > 1440:
            return False, "Invalid duration.", ""

        return True, "", clean

    @staticmethod
    def atomic_save(data: Any, path: str):
        tmp = f"{path}.tmp"
        try:
            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2)
            os.replace(tmp, path)
        except IOError as e:
            logging.error(e)

    @staticmethod
    def append_log(entry: Dict, path: str):
        try:
            with open(path, "a", encoding="utf-8") as f:
                f.write(json.dumps(entry) + "\n")
        except IOError as e:
            logging.error(e)

    @staticmethod
    def get_tail_logs(path: str, limit=20) -> List[Dict]:
        if not os.path.exists(path):
            return []
        try:
            with open(path, "r", encoding="utf-8") as f:
                return [json.loads(l) for l in deque(f, maxlen=limit)][::-1]
        except Exception:
            return []