import os
import re
import logging
import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()
API_KEY = os.getenv("GEMINI_API_KEY")

if not API_KEY:
    logging.error("GEMINI_API_KEY is missing.")
else:
    genai.configure(api_key=API_KEY)

class PetSafetyAI:
    def __init__(self, rules_path="knowledge_base/pet_safety_rules.txt"):
        # RAG Retrieval Configuration
        search_paths = [rules_path, "pet_safety_rules.txt", "knowledge_base/pet_safety_rules.txt"]
        self.rules_path = next((path for path in search_paths if os.path.exists(path)), None)
        
        self.rules_loaded = bool(self.rules_path)
        self.rules_context = ""
        self.model = None

        # DYNAMIC DISCOVERY: April 2026 Stable Model Selection
        try:
            # We prioritize the newest Gemini 3 Flash models
            potential_models = ['gemini-3.1-flash-preview', 'gemini-3-flash-preview', 'gemini-2.0-flash']
            available = [m.name for m in genai.list_models() if 'generateContent' in m.supported_generation_methods]
            
            selected = next((m for m in potential_models if any(m in a for a in available)), None)
            if not selected and available:
                selected = available[0]
            
            if selected:
                self.model = genai.GenerativeModel(model_name=selected)
        except Exception as e:
            logging.error(f"Model discovery failed: {e}")

        if self.rules_loaded:
            with open(self.rules_path, "r", encoding="utf-8") as f:
                self.rules_context = f.read().strip()

    def _hard_safety_check(self, task: str) -> str | None:
        """Layer 1: Deterministic Token matching for toxicity."""
        task_lower = task.lower()
        tokens = re.findall(r"\b\w+\b", task_lower)
        toxins = ["grapes", "grape", "raisins", "raisin", "chocolate", "xylitol", "lilies", "lily"]
        
        for item in toxins:
            if (item in tokens) or (item in task_lower) or (re.search(rf"\b{re.escape(item)}\b", task_lower)):
                return f"UNSAFE (Deterministic Block): {item.capitalize()} is toxic."
        return None

    def check_task_safety(self, task: str) -> str:
        # 1. HARD GATE
        hard_result = self._hard_safety_check(task)
        if hard_result:
            return hard_result

        # 2. RAG LAYER
        if not self.model:
            return "UNSAFE (Infrastructure Error: No compatible Gemini model found)"
        
        if not self.rules_loaded:
            return "UNSAFE (RAG Error: Rulebook not found in knowledge_base/)"

        prompt = f"RULES:\n{self.rules_context}\n\nTASK: {task}\n\nRespond SAFE or UNSAFE."

        try:
            response = self.model.generate_content(prompt, generation_config={"temperature": 0.0})
            res_text = response.text.strip().upper()
            return "SAFE" if res_text.startswith("SAFE") and "UNSAFE" not in res_text else f"UNSAFE: {response.text.strip()}"
        except Exception as e:
            return f"UNSAFE (AI Connection Error: {str(e)[:40]}...)"