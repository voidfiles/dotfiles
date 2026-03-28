# Daily Activity Summary

Creates an in-depth summary of:

- Meetings for alexkessinger@stripe.com for a given day
- Google Drive files owned by me and modified in the last 2 days

## Task

Generate a detailed daily activity summary organized by date:

1. Meeting summary at `daily/{YEAR}/{MONTH}/{DAY}/meetings.md`
2. Downloaded copies of recently modified files at `daily/{YEAR}/{MONTH}/{DAY}/{filename}.md`

For each meeting, include the meeting name, time range, description, and attendees. If attendee notes exist in `person/work/*`, link to them in the attendee list.

For modified files, download and save files that were modified in the last 2 days, organizing them by their modification date.

## Process

### Part 1: Meeting Summary

1. Parse the date argument (or use today's date if not provided)
2. Create the directory structure: `daily/{YEAR}/{MONTH}/{DAY}/`
3. Fetch the user's available Google calendars
4. Retrieve calendar events for the specified date
   - Make sure to use the configured date to query for the correct time frame (arguments are unix timestamps)
   - Use bash to convert 7AM local time to 9PM local time to unix timestamps
5. Only include meetings that have been Accepted
6. If an attendee has `{name}@stripe.com` email, automatically create a link from their {name} to `person/work/{name}`
7. Generate meeting summary using the template format
8. Write the summary to `daily/{YEAR}/{MONTH}/{DAY}/meetings.md`

### Part 2: Recently Modified Files

8. Get the current user's username using org_info_get_current_user
9. Search Google Drive for files owned by the current user (no specific text search, just owner filter)
10. Sort results by most recently modified first
11. For each file modified in the last 2 days:
    - Sanitize the filename (replace spaces with hyphens, lowercase, remove special chars)
    - Define the canonical path: `resources/google-drive/{sanitized-filename}.md`
    - Check if file already exists at `resources/google-drive/{sanitized-filename}.md`

    **If file exists (update flow):**
    - Read the existing file content
    - Download the new content from Google Drive using get_google_drive_file
    - Compare old vs new content to identify changes
    - Create/append to changelog at `resources/google-drive/{sanitized-filename}.changelog.md` with:
      - Date/time of change
      - Summary of what changed (sections added/removed/modified)
      - Diff highlights (key additions and deletions)
    - Archive the old version to `archives/google-drive/{sanitized-filename}-{YYYY-MM-DD}.md`
    - Write the new content to `resources/google-drive/{sanitized-filename}.md`

    **If file doesn't exist (new file flow):**
    - Create the directory structure: `resources/google-drive/` if it doesn't exist
    - Download the file content using get_google_drive_file
    - Write the content to `resources/google-drive/{sanitized-filename}.md`
    - If the file is binary, use download_google_drive_file instead

12. Record all file activity in the daily note at `daily/{YEAR}/{MONTH}/{DAY}/files.md`:
    - List of new files downloaded with links
    - List of updated files with links to both the file and its changelog
    - Summary of significant changes detected

### Part 3: Recently Referenced Files

1. Look through yesterdays files `meetings/{YEAR}/{MONTH}/{DAY}` `daily/{YEAR}/{MONTH}/{DAY}`
2. Download any referenced google files to `resources/google-drive/` following the same update/new flow as Part 2
3. Record downloads in the daily note

## Template Format

```markdown
# Meetings for {Month}, {Day} {Year}

## {Meeting Name}: {Start Time}-{End Time}

{Description of meeting}

Attendees:

- {attendee} (or [[person/work/attendee-name]] if attendee has {name}@stripe.com email)
- {attendee}
```

## Date Handling

- If no date argument is provided, use today's date
- If date argument is provided, use format: YYYY-MM-DD
- Extract year, month (zero-padded), and day (zero-padded) for directory structure

## Attendee Linking

- if attendee has `{name}@stripe.com` email do a wiki style link
- create a wiki-style link: `[[person/work/{name}]]`

## Output

Creates the following files:

### Meetings File

`daily/{YEAR}/{MONTH}/{DAY}/meetings.md` containing:

- Formatted header with full date
- Each meeting as a section with name and time range
- Meeting description (if available)
- List of attendees with links to person notes where applicable

### Modified Files

All Google Drive files are stored in `resources/google-drive/{sanitized-filename}.md`

- Files use sanitized names (lowercase, hyphens instead of spaces)
- Changelogs are stored alongside: `resources/google-drive/{sanitized-filename}.changelog.md`
- Previous versions archived to: `archives/google-drive/{sanitized-filename}-{YYYY-MM-DD}.md`
- Text-based Google Drive files (Docs, Sheets as CSV) are saved as markdown

### Daily Files Summary

`daily/{YEAR}/{MONTH}/{DAY}/files.md` containing:

- Links to newly downloaded files
- Links to updated files with their changelogs
- Summary of changes detected

## Notes on File Search

- The search looks for ALL files owned by you modified in the last 2 days
- Files are automatically sorted by most recently modified first
- No text content filtering is applied - only ownership and modification date matter
- All files are stored centrally in `resources/google-drive/` with version tracking

## Changelog Format

Each changelog entry should follow this format:

```markdown
## {YYYY-MM-DD HH:MM}

### Summary
Brief description of what changed in this update.

### Changes
- **Added**: New sections or content added
- **Modified**: Sections that were changed
- **Removed**: Content that was deleted

### Key Differences
> Highlighted excerpts of significant changes
```

## Directory Structure

```
resources/
  google-drive/
    {filename}.md              # Current version of each file
    {filename}.changelog.md    # Change history for each file

archives/
  google-drive/
    {filename}-{YYYY-MM-DD}.md # Archived previous versions

daily/
  {YEAR}/{MONTH}/{DAY}/
    meetings.md                # Meeting summary
    files.md                   # File download/update summary for the day
```

## Example Usage

```
/daily-meetings
```

Generates:

- Meeting summary at `daily/2026/01/09/meetings.md`
- Files downloaded/updated in `resources/google-drive/`
- File activity summary at `daily/2026/01/09/files.md`
- Changelogs updated for any modified files
- Previous versions archived to `archives/google-drive/`

```
/daily-meetings 2026-01-10
```

Generates:

- Meeting summary for January 10, 2026 at `daily/2026/01/10/meetings.md`
- Files downloaded/updated in `resources/google-drive/`
- File activity summary at `daily/2026/01/10/files.md`
