Model Card: PawPal+ Pro Safety System
1. Project Overview

Original System: PawPal+ (Modules 1–2), a CLI-based pet management application built with Python OOP principles.

Initial Scope:

Manage owner–pet relationships
Schedule and track pet-related tasks

Current Evolution:
The system has been extended into an Applied AI application that integrates Retrieval-Augmented Generation (RAG) to evaluate task safety. It provides real-time validation and maintains an observable audit log for user transparency.

2. System Architecture

The system follows a Retrieval-Augmented Generation (RAG) pattern:

Retrieval Layer:
Safety constraints are loaded from a local knowledge base (pet_safety_rules.txt).
Generation Layer:
Retrieved context is injected into a Gemini 1.5 Flash model configured with temperature = 0.0 to ensure deterministic, safety-focused outputs.
Application Layers:
UI Layer: Streamlit interface for user interaction
Service Layer: Python-based logic handling validation, logging, and atomic file operations
Logging & Observability:
Safety decisions are persistently logged, with efficient tail-reading to maintain bounded memory usage (O(limit)) during log inspection.
3. Reflection: Ethics & Responsibility
Limitations & Biases

The system’s knowledge is strictly constrained by the contents of pet_safety_rules.txt.

If a hazard is missing (e.g., breed-specific sensitivities or less common toxins), the system may incorrectly classify a task as safe.
The dataset may reflect Western-centric pet care standards, introducing potential bias unless expanded with more diverse sources.
Potential Misuse & Mitigation

A key risk is over-reliance on the system in situations requiring professional veterinary care.

To mitigate this:

The UI provides explicit warnings when the AI system is unavailable
Blocked actions are clearly surfaced with strong visual feedback
The system is positioned as a decision-support tool, not a replacement for medical expertise
Reliability Insights

Model behavior was highly sensitive to configuration.

At higher temperatures, outputs included conversational variability that broke downstream parsing
Setting temperature = 0.0 significantly improved determinism and system reliability
4. AI Collaboration Reflection
Helpful Suggestion

The recommendation to use collections.deque for log retrieval was a key optimization.
It ensures that log reading operates in O(limit) space, regardless of total log size, improving scalability.

Flawed Suggestion

An initial recommendation to validate outputs using:

if status == "SAFE"

proved too brittle due to minor variations in model output (e.g., punctuation, casing).

This was improved to:

raw_res.upper().startswith("SAFE")

which provides more robust handling of model variability while preserving deterministic behavior.