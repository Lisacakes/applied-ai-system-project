import os
import re
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")
genai.configure(api_key=API_KEY)

class PetSafetyAI:
    def __init__(self, rules_path="knowledge_base/pet_safety_rules.txt"):
        self.rules_path = rules_path if os.path.exists(rules_path) else None
        self.rules_loaded = bool(self.rules_path)
        self.rules_context = ""
        self.model = None

        # DYNAMIC DISCOVERY: Find a model your key is authorized to use
        try:
            # We look for the newest flash models first
            potential_models = ['gemini-2.5-flash', 'gemini-2.0-flash', 'gemini-1.5-flash-latest']
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            # Pick the best available one from our list, or fallback to the first one the API gives us
            selected = next((m for m in potential_models if any(m in a for a in available)), None)
            if not selected and available:
                selected = available[0]
            
            if selected:
                self.model = genai.GenerativeModel(model_name=selected)
        except Exception as e:
            print(f"Discovery failed: {e}")

        if self.rules_loaded:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.rules_context = f.read().strip()

    def _hard_safety_check(self, task: str) -> str | None:
        """Deterministic block for toxic items."""
        task_lower = task.lower()
        tokens = re.findall(r"\b\w+\b", task_lower)
        toxins = ["grapes", "grape", "raisins", "raisin", "chocolate", "xylitol"]
        
        for item in toxins:
            if (item in tokens) or (item in task_lower):
                return f"UNSAFE (Deterministic): {item.capitalize()} is toxic."
        return None

    def check_task_safety(self, task: str) -> str:
        # 1. Hard Gate (Always works even if API fails)
        hard_result = self._hard_safety_check(task)
        if hard_result:
            return hard_result

        # 2. RAG Logic
        if not self.model:
            return "UNSAFE (Infrastructure Error: No compatible Gemini model found)"
        
        if not self.rules_loaded:
            return "UNSAFE (RAG Error: Rulebook not found)"

        prompt = f"RULES:\n{self.rules_context}\n\nTASK: {task}\n\nRespond SAFE or UNSAFE."

        try:
            # We use the discovered model to generate the response
            response = self.model.generate_content(prompt, generation_config={"temperature": 0.0})
            return response.text.strip()
        except Exception as e:
            return f"UNSAFE (AI Connection Error: {str(e)[:40]}...)"