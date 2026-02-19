# Design Philosophy

## Core Concept: MAGI

The system is inspired by the MAGI system (from EVA), comprised of three distinct personas representing different reasoning modalities. This "schizophrenic" design encourages rigorous debate and error correction before a final decision is made.

### The Personas

1. **BALTHASAR (The Mother/Structure)**
    * **Role**: Constructive, Structural, Normative.
    * **Function**: Builds the Logic Trees, defines the scope, ensures MECE (Mutually Exclusive, Collectively Exhaustive).
2. **CASPER (The Woman/Divergence)**
    * **Role**: Intuitive, Creative, Risk-taking.
    * **Function**: Generates hypotheses (both standard and contrarian), thinks outside the box.
3. **MELCHIOR (The Scientist/Reality)**
    * **Role**: Critical, Objective, Empirical.
    * **Function**: Validates feasibility, checks costs/risks, filters out hallucinations.

### The Integration Core

A fourth abstract component that synthesizes the outputs of the three agents into a coherent decision.

---

## Methodological Foundation

The system implements the decision-making methodologies of top-tier strategy consulting firms.

### 1. Issue-Driven Approach (論点思考)

* **Why**: Most people solve the wrong problem.
* **How**: Before generating ideas, we rigorously define *what* question we are answering.
* **Key Heuristic**: "Is this issue verifiable?" "Can we control the outcome?"

### 2. Hypothesis-Driven Approach (仮説思考)

* **Why**: Analyzing all data is impossible (Paralysis by Analysis).
* **How**: Formulate a "likely answer" first, then test it.
* **Key Heuristic**: "Quick & Dirty is better than Slow & Perfect." Iteration speed > Accuracy of first guess.

---

## Technical Design Choices

### File-Based State Machine

* **Decision**: We use the file system (JSON/Markdown) as the database.
* **Reasoning**:
  * **Transparency**: The user can see exactly what the agent "thinks" by opening a text file.
  * **Editability**: The user can manually intervene (tweak a JSON file) mid-process if the agent goes off-track.
  * **Portability**: works entirely within a standard Obsidian vault (synced via Git/iCloud/etc.).
  * **Stateless Code**: The Python scripts are stateless executioners; they simply read current state -> compute next step.

### User-in-the-Loop

* **Decision**: The pipeline pauses for "Execution" and "Feedback".
* **Reasoning**: Strategic planning is useless without execution. The system effectively forces the user to go do the work before generating the next set of hypotheses.
