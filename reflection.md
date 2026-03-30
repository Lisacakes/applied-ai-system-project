# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
My initial UML had four classes. Task held the details of a single care activity like the title, time, duration, priority, frequency, and whether it was done. Pet stored a pet's name and species and kept a list of its tasks. Owner held a list of pets and was the main entry point for getting all tasks across the whole system. Scheduler took an Owner and handled all the logic like sorting, filtering, conflict detection, and generating the daily schedule. The key relationship was that Scheduler did not store any data itself. It just worked with what Owner and Pet already had.
- What classes did you include, and what responsibilities did you assign to each?

so i designed 4 classes; they were the tesk class which held everthign about each care activity: title, time, duration, priority e.t.c

then there's the pet class, which stores a pets name, species, and their task. it handles removing and adding and repoting task count

then there's the owner class which manages a list of pets and prrovides the information of all the tasks for eevr pet. 

then the scheduler is the brain. it doesn't store any data, but it takes an owner and sorts fileters, e.t.c 



**b. Design changes**

- Did your design change during implementation?

Yes

- If yes, describe at least one change and why you made it.

after checking my skeleton, i added a due_date to Task, which i hadn't put before. Cause without it, i couldn't distinguish between a task scheduled for tday versus one rescheduled for tomorrow after being amrked complete. 
---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
the scheduler considers three main constraints: time (what order tasks happen in), priority (high, medium, or low), and frequency (whether a task repeats daily, weekly, or just once).
- How did you decide which constraints mattered most?
When generating a schedule, priority comes first, a high priority medication will always show up before a low priority enrichment activity, even if the enrichment is scheduled earlier in the day. Time is the tiebreaker within the same priority level. I decided priority mattered most because missing a medication is a bigger deal than missing a play session, and the scheduler should reflect that automatically without the owner having to think about it.
**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.

The conflict detection only catches tasks that are scheduled at the exact same time. It won't warn you if a 30-minute walk starts at 8:00am and a feeding starts at 8:15am, even though those overlap. 


- Why is that tradeoff reasonable for this scenario?

Checking for overlapping time ranges would be more accurate, but it's also a lot more complex to build. 
---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
i used the ai tools to geenrate tests for the test suite. It helped think of cases i didnt think of, I also used it to generate the class skeletons. 
- What kinds of prompts or questions were most helpful?
one that was particularly helpful for me was  "what edge cases should I test for a scheduler that handles recurring tasks and conflict detection?" 
**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.

At a point Claude suggested making the Scheduler extend the Owner class so it could access the pet list through inheritance.

- How did you evaluate or verify what the AI suggested?
 I didn't go with it because a Scheduler isn't a type of Owner, it just works with one. Accepting that suggestion would have mixed the data and logic layers together in a way that would make the code harder to maintain and test. I evaluated it by asking myself: if I needed to change how Owner stores pets, would that break the Scheduler? With inheritance, yes.

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
I tested 13 behaviors across the core system:

Marking a task complete changes its status to done
A one-time task doesn't reschedule after being completed
Adding a task to a pet increases its task count
Tasks come back in chronological order when sorted by time
A daily task reschedules to tomorrow after completion
A weekly task reschedules 7 days out after completion
Two tasks at the same time trigger a conflict warning
Tasks at different times produce no conflict warnings
Filtering by status only returns tasks with the right completion state
Filtering by pet name only returns that pet's tasks
High priority tasks appear before low priority ones in a priority sort
Time breaks ties correctly within the same priority level
Saving and loading from JSON produces the same owner, pets, and task count
Task fields like title, priority, and frequency survive a save/load roundtrip
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
I'm mostly confident the core logic works
- What edge cases would you test next if you had more time?

If I had more time I'd test what happens when two pets have the exact same name,

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

the recurring task logic went well. 
**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

I would improve the conflict detection for overlapping periods. 

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?


The main thing I took away from this project is that AI is really good at writing code fast, but it doesn't know what a good design looks like for your specific situation. It'll suggest whatever works, not whatever is clean. I had to be the one deciding which classes should be separate, what logic belongs where, and when a shortcut is okay versus when it'll cause problems later. AI sped up the building part.