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


Testing Summary: I implemented a suite of unit tests for input normalization and time validation using pytest. 100% of tests passed, confirming that the system correctly sanitizes pet task titles (handling case sensitivity and erratic spacing) and rejects invalid scheduling formats before they reach the AI or persistence layers.





![System Architecture](assets/architecture.png)


#PART 2

#PawPal+ Pro: Applied AI Pet Safety System

## Demo Video
[![Watch the Demo](https://www.loom.com/share/ab7d718a12df470abc6e6b5da3ed8ced)]

## Project Background
**Original Project:** PawPal+ (Modules 1-3)
**Summary:** Originally a CLI and basic Streamlit tool for managing pet schedules. 
**The Evolution:** This project transforms a simple task manager into a **Safety-Aware System**. Using Retrieval-Augmented Generation (RAG), the app now reasons about pet safety before any data is saved, preventing common household hazards (like toxic foods) from being scheduled.

## 🏗 System Architecture
The system uses a decoupled, three-tier architecture to ensure reliability and safety.
![System Architecture](assets/architecture.png)

## 🛠 Design Decisions
* **RAG-Driven Safety:** Used a local `pet_safety_rules.txt` to ground the AI, ensuring evaluations are based on verified facts rather than general LLM "hallucinations."
* **Atomic Persistence:** Implemented a "write-to-temp-then-replace" strategy to prevent data corruption during saves.
* **Efficient Observability:** Used `collections.deque` for log retrieval, ensuring that as the safety logs grow, memory usage remains constant ($O(limit)$).
* **Hardened Validation:** Built a custom Service Layer to handle input normalization and regex-based time validation before the AI is even triggered.

## Testing Summary
* **19/19 Unit Tests Passed:** Verified core OOP logic and Service Layer validation.
* **Safety Accuracy:** 100% success rate in blocking high-toxicity inputs (Grapes, Chocolate, Lilies) during manual and automated verification.

Setup Instructions
To get this app running on your computer, follow these steps:

Download the project folder and open it in your code editor.

Install the necessary tools by typing this in your terminal:
pip install streamlit google-generativeai python-dotenv

Create a new file named .env in the main folder. Inside that file, paste your API key like this:
GEMINI_API_KEY=your_key_here

Make sure you have a folder named knowledge_base with a text file inside called pet_safety_rules.txt.

Start the app by typing:
streamlit run app.py

Sample Interactions
Example 1: A normal activity

User Input: Morning walk

System Output: Added 'Morning walk'!

What happened: The system checked the rulebook and found no issues with walking at that time.

Example 2: A dangerous food

User Input: Feed Lori grapes

System Output: UNSAFE (Deterministic Block): Grape is toxic to dogs.

What happened: The code instantly recognized "grape" as a toxin and blocked it before even asking the AI.

Example 3: A weather risk

User Input: Walk Lori in 100°F

System Output: UNSAFE: High temperature detected in rules.

What happened: The AI read the specific temperature rules in the text file and flagged the heat as a danger.

Design Decisions
I built this using a two layer safety approach. The first layer is a simple list of toxic items. If the app sees a word like chocolate or grapes, it stops the task immediately. I did this because it is faster and more reliable than waiting for an AI to think.

The second layer uses the Gemini AI. This layer reads my custom rulebook to handle more complicated situations, like weather or specific health needs. A major decision I made was to have the app fail closed. This means if the internet goes out or the AI makes a mistake, the app assumes the task is unsafe just to be careful. I believe it is better to block a safe walk than to accidentally allow a dangerous meal.

Testing Summary
The hybrid system worked well because it caught words like raisin bread that a basic search might miss. I also fixed a bug where the app would crash if you tried to add the same task twice.

One challenge was getting the app to talk to the right AI model. I solved this by adding a discovery feature that lets the code find the correct model version automatically. This makes the app much more stable and less likely to break if the AI provider changes something.

Reflection
This project showed me that you cannot rely on AI alone for safety. When lives are at stake, you need hard rules in the code to act as a backup. It taught me how to take a big list of safety policies and turn them into a working system. Solving the connection issues also reminded me that a good engineer has to plan for things to go wrong and make sure the system stays safe no matter what.

