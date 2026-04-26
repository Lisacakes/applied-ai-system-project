import os
import logging
from dotenv import load_dotenv
import google.generativeai as genai

# --- Global Setup (run once) ---
load_dotenv()

API_KEY = os.getenv("GEMINI_API_KEY")
if not API_KEY:
    raise RuntimeError("GEMINI_API_KEY not found.")

genai.configure(api_key=API_KEY)

logging.basicConfig(level=logging.ERROR)


class PetSafetyAI:
    def __init__(self, rules_path="knowledge_base/pet_safety_rules.txt"):
        self.rules_path = rules_path
        self._rules_cache = None

        # Model configured once per instance (lightweight)
        self.model = genai.GenerativeModel(
            model_name="gemini-1.5-flash",
            generation_config={"temperature": 0.0},
            system_instruction=(
                "You are a pet safety validator.\n"
                "Respond ONLY with:\n"
                "- SAFE\n"
                "- or a clear, concise safety warning.\n"
                "Do not include extra text."
            ),
        )

    @property
    def safety_rules(self) -> str:
        """Lazy-load and cache safety rules."""
        if self._rules_cache is None:
            try:
                with open(self.rules_path, "r", encoding="utf-8") as f:
                    self._rules_cache = f.read().strip()
            except FileNotFoundError as e:
                logging.error(f"Missing rules file: {self.rules_path}")
                raise e  # Fail fast — don't silently degrade
        return self._rules_cache

    def check_task_safety(self, task: str) -> str:
        """Evaluate whether a task is safe for a pet."""
        if not task:
            return "SAFE"

        prompt = f"RULES:\n{self.safety_rules}\n\nTASK: {task}"

        try:
            response = self.model.generate_content(prompt)
            result = (response.text or "").strip()

            # Enforce output format
            if result.upper() == "SAFE":
                return "SAFE"
            return result if result else "Safety Check Unavailable"

        except Exception as e:
            logging.error(f"AI Error: {e}")
            return "Safety Check Unavailable"


# --- Quick Test ---
if __name__ == "__main__":
    ai = PetSafetyAI()

    print("Test 1 (Toxic):", ai.check_task_safety("Give the dog chocolate"))
    print("Test 2 (Safe):", ai.check_task_safety("Go for a 10 minute walk"))