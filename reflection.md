# PawPal+ Project Reflection

## 1. System Design

User should be able to:
- enter basic owner & pet info
- add & edit care tasks (duration + priority)
- trigger plan generation & view the result (with reasoning)

**a. Initial design**

- Briefly describe your initial UML design.

    - My initial UML design had five classes: four data-holding classes (Owner, Pet, Task, and Plan) plus one logic class (Scheduler). I split data from logic so that what gets scheduled stays separate from how it gets decided, keeping each class focused on one responsibility. The classes connect as: Owner has Pet, Pet has Tasks, the Scheduler takes Tasks and produces a Plan, and the Plan orders Tasks (all shown as associations in the diagram).

- What classes did you include, and what responsibilities did you assign to each?

    - **Owner** — holds the owner's basic info (name) and preferences. Responsible for storing who is planning the care.
    - **Pet** — holds the pet's info (name, species). Responsible for representing the animal the tasks are for.
    - **Task** — holds a single care task's data (title, duration in minutes, priority). Responsible for describing one thing that needs to happen.
    - **Scheduler** — the logic class. Takes a list of tasks plus constraints (time available, priority) and produces a Plan. Responsible for sorting tasks by priority, dropping tasks when time runs out, assigning time slots, and building the reasoning.
    - **Plan** — holds the final ordered list of scheduled tasks and the explanation. Responsible for representing the finished daily schedule that gets displayed.
    
**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
