---
name: create-project
description: Use when creating an Obsidian project home from source notes, meetings, action items, and related context.
---

# Project Home

Establish a comprehensive home base for a project by researching related notes, summarizing the project, identifying action items, and setting up a structure for tracking key meetings, documents, and artifacts.

Don't try to guess at what needs to be done. Use source material to generate action items. It should be backed up by a meeting, note, or document.

## Process

1. **Create the project folder and index**
   - Folder name: `projects/{lowercase-kebab-case-name}/`
   - File: `projects/{name}/index.md`
   - The index.md **must** include a `description` field in frontmatter (1-2 sentences)

2. **Research Related Notes**
   - Search for notes from the last 2-3 months related to the project
   - Look for:
     - Direct mentions of the project name
     - Related concepts and themes
     - Meeting notes that reference the project
     - Action items or decisions
   - Cast a wide net to capture all relevant context

3. **Create Project Summary**
   - What is this project about?
   - What's the current status?
   - What's been done?
   - What's left to do?

4. **Extract Action Items**
   - Immediate next steps

5. **Set Up Weekly Updates Structure**
   - Create a dedicated section for weekly changes
   - Include template for consistent updates

## Output Format

Create `projects/{name}/index.md` using the template: [project_template.md](project_template.md)

## Guidelines

- **Be thorough**: Cast a wide net when searching for related notes
- **Be concise**: Synthesize rather than dump - the summary should be readable
- **Be actionable**: Every section should enable better decision-making
- **Be honest**: Call out blockers, challenges, and unknowns clearly
- **Be temporal**: Time-stamp decisions and use the weekly updates actively
- **Don't explain, quote**: Don't explain things, use quotes from source materialy liberally

## Follow-up Actions

After creating the project home:

1. Link it from related notes
2. Add it to your daily review
3. Set a recurring reminder to update weekly section
4. Share with stakeholders for feedback
5. Archive or link old related notes to this central hub
