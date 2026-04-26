# PawPal+ (Module 2 Project)

You are building PawPal+ Pro, a Streamlit-based application that helps pet owners plan and validate pet care tasks using an AI-powered safety system.

## Scenario

A busy pet owner needs help staying consistent with pet care—but also wants to ensure that every task is safe and appropriate for their pet.

They want an intelligent assistant that can:

-Track and manage pet care tasks (walks, feeding, medication, grooming, enrichment)
-Validate tasks against known safety constraints (e.g., toxic foods, unsafe activities)
-Adapt to system limitations (e.g., AI offline scenarios)
-Maintain a transparent audit trail of unsafe or blocked actions
-Provide a clear, reliable daily plan

## What you will build

Your final app should:

-Allow users to enter and manage owner + pet information
-Allow users to create, edit, and validate tasks (time, priority, etc.)
-Use an AI-powered Safety Gatekeeper to evaluate tasks before they are saved
-Generate and display a structured daily plan
-Persist data reliably using atomic file operations
-Maintain a persistent safety audit log for all blocked or flagged tasks
-Handle AI failures gracefully (e.g., offline fallback with user bypass)
-Display system outputs clearly, including validation feedback and logs
## Getting started

### Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

### Suggested workflow

1. Read the scenario carefully and identify requirements and edge cases.
2. Draft a UML diagram (classes, attributes, methods, relationships).
3. Convert UML into Python class stubs (no logic yet).
4. Implement scheduling logic in small increments.
5. Add tests to verify key behaviors.
6. Connect your logic to the Streamlit UI in `app.py`.
7. Refine UML so it matches what you actually built.


System Architecture

The system follows a layered architecture with an AI evaluation pipeline:

UI Layer (Streamlit):
Handles user interaction, task input, and system observability

Service Layer (Python):
Encapsulates business logic, validation, logging, and atomic persistence

AI Engine (RAG-based):
Uses a retrieval step (pet_safety_rules.txt) combined with a generative model (Gemini 1.5 Flash) to evaluate task safety

Persistence Layer:
-JSON for structured data (data.json)
-JSONL for append-only audit logs (blocked_log.json)


Suggested Workflow

-Analyze the scenario and identify functional and safety requirements
-Design a UML diagram (classes, relationships, responsibilities)
-Implement core data models (Owner, Pet, Task, Scheduler)
-Build validation and scheduling logic
-Integrate the AI Safety Gatekeeper using a RAG pattern
-Implement persistence (atomic writes + logging)
-Add tests for validation, scheduling, and safety behavior
-Connect all components to the Streamlit UI
-Refine architecture to match the final system design

Key Design Considerations
-Safety First:
Tasks must be validated before being committed to storage

Deterministic AI Behavior:
Use controlled model settings (e.g., temperature = 0.0) to reduce variability

Reliability:
The system must remain usable even if the AI component fails

Performance:
Log handling and data operations should scale efficiently (bounded memory where possible)

Observability:
Users should be able to see why actions were blocked or allowed


Testing & Reliability Expectations
    Unit tests should validate:
        Time format validation
        Duplicate task prevention
        Scheduling behavior
    The system should correctly:
        Block unsafe tasks
        Log all blocked actions
        Handle AI failures without crashing