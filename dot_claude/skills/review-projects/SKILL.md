# Review Projects

Review all open projects, generate weekly status updates, and identify stale projects that should be archived.

## Purpose

This skill implements the PARA method's principle that projects should either be actively worked on or archived. It helps maintain a healthy project list by:

1. Generating weekly updates for active projects
2. Identifying stale projects that haven't progressed
3. Suggesting archival for projects that appear abandoned or completed

## Process

### Step 1: Discover All Open Projects

Scan the `projects/` folder to find all active projects:

```bash
# List all project folders
ls projects/
```

For each project:
- Read the `index.md` or main project file
- Check frontmatter for `status`, `last_updated`, `deadline`
- Note any `## Weekly Updates` section and last entry date

### Step 2: Gather Activity Signals

For each project, determine recent activity by:

1. **File modifications**: Check when files in the project folder were last modified
2. **Meeting references**: Search `Meetings/` for mentions of the project in the last 30 days
3. **Daily note mentions**: Search `daily/` for project references in the last 30 days
4. **Linked notes**: Check if related notes have been updated recently

Activity scoring:
- **Active**: Modified in last 7 days OR referenced in meetings/daily notes this week
- **Stale**: No modifications in 14-30 days AND no recent references
- **Dormant**: No modifications in 30+ days AND no recent references

### Step 3: Generate Weekly Updates

For each **Active** project:

1. Read the project's current state (index.md, todos, recent notes)
2. Search for related activity:
   - Meeting notes mentioning the project
   - Daily notes with project references
   - Recently modified files in the project folder
3. Generate a weekly update entry:

```markdown
### Week of YYYY-MM-DD

**Progress:**
- [Summarize what moved forward based on evidence]
- [Reference specific meetings or notes: [[Meeting Name]]]

**Blockers/Challenges:**
- [Any identified issues or stalls]

**Next Steps:**
- [Extracted from existing todos or implied from context]

**Activity Level:** [High/Medium/Low] - [Brief explanation]
```

4. Append the update to the project's index.md under `## Weekly Updates`

### Step 4: Identify Archival Candidates

Flag projects for archival review if:

1. **Dormant (30+ days)**: No file changes, no meeting mentions, no daily note references
2. **Completed signals**:
   - All todos checked off
   - Contains phrases like "shipped", "launched", "completed", "done"
   - Deadline has passed
3. **Abandoned signals**:
   - No updates in 60+ days
   - Single-file projects with no recent edits
   - No linked meetings or notes

### Step 5: Generate Review Report

Create a comprehensive report at `projects/PROJECT-REVIEW-YYYY-MM-DD.md`:

```markdown
# Project Review - YYYY-MM-DD

## Summary

- **Total Projects:** X
- **Active:** X projects
- **Stale:** X projects (14-30 days inactive)
- **Dormant:** X projects (30+ days inactive)

---

## Active Projects

### [Project Name]
**Last Activity:** YYYY-MM-DD
**Recent Progress:** [1-2 sentence summary]
**Weekly Update:** Added to project index

---

## Stale Projects (Attention Needed)

### [Project Name]
**Last Activity:** YYYY-MM-DD (X days ago)
**Last Meeting Reference:** YYYY-MM-DD or "None found"
**Assessment:** [Why it might be stalled]
**Recommendation:** [Check in / Reprioritize / Consider archiving]

---

## Archival Candidates

These projects appear inactive and may be ready for archival:

### [Project Name]
**Last Activity:** YYYY-MM-DD (X days ago)
**Reason:** [Dormant / Appears completed / No recent references]
**Archive Command:** `/archive-project [project-name]`

### [Project Name]
**Last Activity:** YYYY-MM-DD (X days ago)
**Reason:** [Reason]
**Archive Command:** `/archive-project [project-name]`

---

## Recommended Actions

1. **Archive now:** [List projects clearly done or abandoned]
2. **Check in on:** [List stale projects that need attention]
3. **Keep monitoring:** [List projects that are borderline]

---

## Notes

- Projects archived can always be resurrected from `archives/projects/`
- Run `/archive-project [name]` to archive with link updates
- Consider weekly project reviews to prevent staleness
```

### Step 6: Interactive Archival (Optional)

After presenting the report, ask the user:

> "I found X projects that appear ready for archival. Would you like me to:
> 1. Archive all suggested projects
> 2. Review each one individually before archiving
> 3. Skip archival for now"

If user chooses to archive:
- Use the `archive-project` skill for each project
- Update daily note with archival summary

## Output

1. **Weekly updates** appended to each active project's index.md
2. **Review report** saved to `projects/PROJECT-REVIEW-YYYY-MM-DD.md`
3. **Summary** displayed to user with actionable recommendations

## Arguments

- `--skip-updates`: Only generate the review report, don't add weekly updates to projects
- `--auto-archive`: Automatically archive dormant projects (30+ days) without confirmation

## Example Usage

**Full weekly review:**
```
/review-projects
```

**Quick status check without modifying projects:**
```
/review-projects --skip-updates
```

**Aggressive cleanup:**
```
/review-projects --auto-archive
```

## Second Brain Integration

This skill supports several PARA principles:

- **Projects are time-bound**: If a project has no deadline and no activity, it may belong in Areas or Resources
- **Archive liberally**: Completed or abandoned projects should move to Archives immediately
- **Regular review**: Weekly project reviews prevent "project debt" accumulation
- **Trust resurrection**: Archived projects remain fully searchable and can be restored

## Tips

- Run this weekly as part of your review routine
- Pair with `/start-the-day` to surface project todos
- Use the archival suggestions to keep your project list focused
- Don't be afraid to archive - it's not deletion

## Edge Cases

- **New projects (< 7 days old)**: Always mark as Active, skip staleness check
- **Projects with future deadlines**: Note the deadline in the report even if activity is low
- **Single-file projects**: May be notes that should move to Resources, flag for review
- **Projects with active todos but no edits**: Still consider Active if todos exist
