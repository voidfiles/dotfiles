# Archive Project

Archives a completed project by moving it to `archives/projects/`, updating all wiki links across the vault, and logging the completion to today's daily note.

## Task

Complete the full project archival workflow:

1. Move project from `projects/` to `archives/projects/`
2. Update all wiki links referencing the project
3. Add completion entry to today's daily note
4. Report summary of changes

## Arguments

- `project-name`: Name of the project folder in `projects/` to archive (e.g., `accounts_risk_onsite`)

## Process

1. **Validate project exists**

   - Check that `projects/<project-name>/` exists
   - Read project index.md to extract context (title, deliverables, etc.)
   - Fail early if project doesn't exist

2. **Create archives directory structure**

   - Ensure `archives/projects/` exists
   - Create if necessary

3. **Find all wiki link references**

   - Search vault for links to `projects/<project-name>/`
   - Report which files will be updated
   - Track all files that reference the project

4. **Move project to archives**

   - Move `projects/<project-name>/` to `archives/projects/<project-name>/`
   - Preserve all file metadata and timestamps

5. **Update all wiki links**

   - For each file with references to the project:
     - Read the file
     - Update wiki links from `projects/<project-name>/` to `archives/projects/<project-name>/`
     - Add "(archived)" notation to link display text
   - Report all updated files

6. **Log to daily note**

   - Determine today's date and daily note path: `daily/YYYY/MM/DD/daily.md`
   - Create daily note if it doesn't exist
   - Add entry under "## Completed Projects" section:
     - Project name
     - Archive location
     - Brief summary from project index (if available)
   - If the state of the project is unclear, ask what the result was and append that information to the daily note
   - If daily note has existing content, append to it appropriately

7. **Update Project Index**

   - run the `/update-project-index` command to update the project index file

8. **Report completion**
   - Confirm project archived
   - List updated files
   - Show daily note entry
   - Provide archive location

## Daily Note Entry Format

```markdown
## Completed Projects

- **Project Name** - Archived completed project to `archives/projects/<project-name>`
  - Brief summary or key deliverables from project
```

## Output

Provides comprehensive summary:

- ✅ Project archived location
- 📝 Number of wiki links updated
- 📋 List of files with updated links
- 📅 Daily note updated with completion entry
- 🔗 Link to archived project

## Example Usage

**Archive a completed project:**

```
/archive-project accounts_risk_onsite
```

**Archive another project:**

```
/archive-project Risk Staff Eng Onsite 2026
```

## Second Brain Integration

This command follows the PARA method principle of archiving completed projects immediately. According to Second Brain methodology:

- **Projects** are time-bound efforts with specific outcomes
- Once complete, projects should be archived to reduce active clutter
- Archived projects remain fully retrievable through search and links
- Daily notes track project completions for retrospective review

## Safety Features

- Validates project exists before moving
- Creates necessary directories automatically
- Updates all wiki links to prevent broken references
- Preserves complete project history and metadata
- Logs action for future reference
- Reports all changes comprehensively

## Notes

- Project name should match the folder name in `projects/`
- Automatically handles spaces in project names
- Creates daily note file/directories if they don't exist
- Appends to existing daily notes without overwriting
- Maintains vault link integrity throughout process
- Archive structure: `archives/projects/<project-name>/`
