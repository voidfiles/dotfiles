# Start the Day

Run a morning routine that combines gratitude practice, warm-up reflection, and daily planning based on recent notes and action items.

## Process

### 1. Gratitude Collection (2 minutes)

Ask the user to share 2-3+ things they're grateful for today. Keep it conversational and warm.

### 2. Warm-Up Questions (3-4 minutes)

- Find the 10 most recently edited markdown files in the vault (excluding the Daily folder)
- Read those files to understand what the user is currently working on
- Generate 2-3 thoughtful questions about the content to get their brain engaged
- Examples:
  - "I noticed you've been working on [X] - how's that coming along?"
  - "You updated notes on [Y] - what's the main challenge there?"
  - "What's on your mind about [Z]?"
- Have a brief conversation based on their answers

### 3. Self-Talk Scripts for Today (2 minutes)

- Read `self talk scripts.md` to understand the available self-talk strategies
- Based on what you learned from the warm-up questions and recent notes, identify 2-3 relevant challenges or contexts the user is facing today (e.g., ambiguity & pressure, technical tradeoffs, advocating for quality, coordination challenges, burnout risk)
- Select 3-5 self-talk phrases that match their context from different categories:
  - Distanced self-talk for stress
  - Motivational for tradeoffs
  - Instructional for technical focus
  - Regulation and recovery
  - Team coaching/stewardship
- Present them conversationally: "Based on what you're working on, here are some mental anchors for today:"
- Keep it practical and connected to their actual challenges

### 4. Automated Review (2 minutes)

- Scan all markdown files edited in the last 2 days
- Extract ALL markdown todos: `- [ ] action item`
- Also look for action-oriented phrases like "need to", "should", "next step", "TODO", "ACTION"
- Present a consolidated list organized by source file

### 5. Prioritization Conversation (2-3 minutes)

- Show the user what todos and action items exist
- Ask: "Looking at these, what feels most important to move forward today?"
- Help them identify **the main thing** - their intention for the day
- Help them select 3-5 prioritized tasks

### 6. Create Daily Note

Create a note at `Daily/YYYY-MM-DD.md` with this format:

```markdown
# [Day of week], [Month DD, YYYY]

## Gratitude

- [Item 1]
- [Item 2]
- [Item 3]

## Self-Talk Scripts for Today

[3-5 selected self-talk phrases tailored to today's challenges, organized by category]

## Main Intention

[The main thing they want to tackle today - stated clearly and concretely]

## Tasks

- [ ] [Prioritized task 1]
- [ ] [Prioritized task 2]
- [ ] [Prioritized task 3]
- [ ] [Prioritized task 4]
- [ ] [Prioritized task 5]

## Notes

[Space for them to add notes throughout the day]
```

## Important Guidelines

- **Tone:** Warm, conversational, supportive - this is a ritual to start the day well
- **Timing:** Keep the whole flow to ~12 minutes total
- **Don't generate new todos** - only surface what already exists in their notes
- **Self-talk selection:** Choose scripts that genuinely match their current challenges - don't force it
- **Focus on clarity:** Help them articulate the main intention clearly
- **Make the daily note** - don't just summarize, actually create the file
- **Consistency over perfection:** Better to do this regularly than to overthink it

## Daily Folder Setup

- Check if `Daily/` folder exists, create it if needed
- Use ISO date format for filenames: `YYYY-MM-DD.md`
- Store in `/home/alex/Documents/Alex3/Daily/`
