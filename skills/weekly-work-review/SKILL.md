# Weekly Work Review

Create a comprehensive review of the week's work activities by analyzing meeting notes, daily notes, and project progress.

## Task

Analyze the current week (or specified date range) to:

1. Summarize key activities day-by-day
2. Extract highlights from each meeting
3. Identify progress on work projects
4. Surface key decisions and action items

## Prerequisites

Before generating the review, **ask the user which projects in `/projects/` are work-related** to ensure only relevant projects are included in the work summary.

## Process

### 1. Determine Date Range

- If no arguments provided: Use current week (Monday-Sunday)
- If arguments provided: Parse start and end dates
- Format: `YYYY/MM/DD` for folder navigation

### 2. Gather Daily Activities

For each day in the date range:

**A. Scan Daily Notes** (`daily/{year}/{month}/{day}.md`)

- Read the daily note if it exists
- Extract key activities, accomplishments, decisions
- Note any blockers or challenges mentioned

**B. Scan Meeting Notes** (`Meetings/{year}/{month}/{day}/`)

- List all meetings that day
- For each meeting:
  - Read the meeting note
  - Extract: attendees, key topics, decisions, action items
  - Identify important outcomes or next steps

### 3. Analyze Work Projects

For each work project (from user's confirmed list):

- Check for notes modified this week
- Identify progress indicators:
  - New files or significant updates
  - Completed tasks or milestones
  - Open questions or blockers
- Summarize what moved forward

### 4. Synthesize Findings

Create a structured summary that flows chronologically by day, then synthesizes across the week.

## Output Format

Create a weekly work review note:

```markdown
---
date: [Week start date]
type: weekly-work-review
week: [Week number of year]
---

# Weekly Work Review - Week of [Date Range]

## Executive Summary

**Key Accomplishments:**

- [Major outcome 1]
- [Major outcome 2]
- [Major outcome 3]

**Meetings This Week:** [Count]
**Active Work Projects:** [Count]

---

## Daily Breakdown

### Monday, [Date]

**Daily Activities:**

- [Key activity from daily note]
- [Key activity from daily note]

**Meetings:**

#### [Meeting Title] - [Time]

- **Attendees:** [List]
- **Purpose:** [Brief description]
- **Key Discussion Points:**
  - [Point 1]
  - [Point 2]
- **Decisions Made:**
  - [Decision 1]
  - [Decision 2]
- **Action Items:**
  - [ ] [Action item 1] (@person)
  - [ ] [Action item 2] (@person)

#### [Next Meeting...]

**Blockers/Challenges:**

- [Any noted blockers]

---

### Tuesday, [Date]

[Same structure as Monday]

---

[Continue for each day of the week]

---

## Project Progress Summary

### [Work Project 1]

**Progress This Week:**

- [What moved forward]
- [Milestones reached]

**Key Activities:**

- [Activity tied to this project]
- [Activity tied to this project]

**Status:** [On track / At risk / Blocked]

**Next Week Priorities:**

- [Priority 1]
- [Priority 2]

---

### [Work Project 2]

[Same structure]

---

## Key Decisions & Outcomes

1. **[Decision/Outcome 1]**

   - Context: [Where/when this came up]
   - Impact: [Why it matters]

2. **[Decision/Outcome 2]**
   - Context: [Where/when this came up]
   - Impact: [Why it matters]

## Action Items Tracker

**High Priority:**

- [ ] [Action] - Due: [Date] - Owner: [Person]
- [ ] [Action] - Due: [Date] - Owner: [Person]

**Medium Priority:**

- [ ] [Action] - Due: [Date] - Owner: [Person]

**Blockers/Waiting On:**

- [ ] [Item] - Waiting on: [Person/Decision]

## Upcoming Focus

**Next Week's Priorities:**

1. [Priority based on this week's progress]
2. [Priority based on open items]
3. [Priority based on upcoming deadlines]

**Meetings Scheduled:**

- [Known upcoming meetings]

**Questions to Resolve:**

- [Open question 1]
- [Open question 2]

---

## Metadata

- **Total Meetings:** [Count]
- **Work Projects Touched:** [Count]
- **Days Worked:** [Count]
- **Key People Interacted With:** [List]
```

## Implementation Details

### Date Parsing

- Use `date` command or similar to determine current week boundaries
- Default to Monday-Sunday as week boundaries
- Handle edge cases (partial weeks, holidays)

### File Discovery

- Use Glob to find all files in date ranges
- Pattern for daily: `daily/{year}/{month}/{day}.md`
- Pattern for meetings: `Meetings/{year}/{month}/{day}/*.md`
- Handle missing days gracefully

### Project Detection

**Important:** Always ask user first which projects are work-related before analyzing them.

### Content Extraction

- Parse markdown structure
- Look for action item indicators: `- [ ]`, `TODO:`, `ACTION:`
- Identify decision markers: `DECISION:`, `We decided`, `Agreed to`
- Extract attendees from frontmatter or content

## Usage Examples

```bash
# Review current week (Monday-Sunday)
/weekly-work-review

# Review specific week
/weekly-work-review 2025/01/06 2025/01/12

# Review last week
/weekly-work-review last-week
```

## Output Location

Save the review to: `daily/{year}/weekly/weekly-review-{week-number}.md`

Example: `daily/2025/weekly/weekly-review-02.md`

## Follow-up Actions

After generating the review:

1. Ask user if they want to move any action items to project notes
2. Suggest archiving completed projects
3. Identify projects that may need attention next week
4. Offer to create a "Week Ahead" planning note

## Notes

- This command focuses on **work activities** specifically
- Personal projects and areas are excluded unless user specifies otherwise
- Emphasizes actionable outcomes and progress tracking
- Designed for professional reflection and planning
