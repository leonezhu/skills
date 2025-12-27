---
name: draft2note
description: Converts files from the Drafts directory into well-formatted Obsidian notes in References directory. Handles single or multiple files, analyzes content for relevance, organizes attachments, and follows the Base template format. Use when user wants to process draft files into proper notes with proper frontmatter, topics, and attachment management.
---

# Draft2note

## Overview

This skill transforms raw draft files into properly formatted Obsidian notes following the Zettelkasten methodology and your vault's established templates. It intelligently analyzes content, creates meaningful connections, and organizes attachments.

## Quick Start

**Basic usage:**
- "Convert my drafts to notes" - Process all files in Drafts/
- "Convert draft 'my ideas.md' to a note" - Process specific file
- "Process these drafts: file1.md, file2.md" - Batch process multiple files

**What happens automatically:**
1. Scans `Drafts/` directory for files
2. Analyzes content for topics and relevance
3. Formats notes using `Templates/Base template.md`
4. Moves and renames attachments to `Attachments/`
5. Creates notes in `References/` with proper frontmatter

## Core Workflow

### 1. File Discovery & Analysis

**Input sources:**
- `Drafts/` directory (primary)
- Individual file paths provided by user
- Multiple files for batch processing

**Content analysis for each file:**
- Extract key concepts and topics
- Identify potential [[bidirectional links]]
- Determine appropriate note title
- Detect embedded images or attachments

### 2. Content Processing Pipeline

For each draft file, the skill performs:

1. **Read content** - Parse raw text/markdown
2. **Determine title** - Use filename or extract from content
3. **Extract topics** - Identify main themes for frontmatter
4. **Process attachments** - Find and rename embedded files
5. **Format note** - Apply Base template structure
6. **Save to References/** - Create final note
7. **Clean up** - Remove original draft (optional)

### 3. Attachment Management

**Attachment detection:**
- Embedded images: `![image](path/to/file.png)`
- Linked files: `[file](path/to/document.pdf)`
- Direct file references

**Renaming strategy:**
- Format: `{note-title}-{original-name}.{ext}`
- Example: `新手健身注意事项-training-plan.png`
- Sanitize special characters and spaces

**Attachment location:**
- All files moved to `Attachments/`
- Paths updated in note content
- Original draft files deleted after successful conversion

### 4. Note Structure

**Frontmatter format:**
```yaml
---
created: 2025-12-27
created_at: '[[2025-12-27]]'
topics:
  - "[[Topic 1]]"
  - "[[Topic 2]]"
aliases:
  - Alternative name
---
```

**Content structure:**
- Original content preserved
- Attachment paths updated
- Related links section added
- Backlinks reference included

## Processing Logic

### Content Analysis

**Topic extraction:**
- Keywords from content
- Categories from context
- User-provided hints
- Related existing notes

**Title determination priority:**
1. User-specified title
2. First heading in content
3. Descriptive filename
4. Generated summary title

**Relevance scoring:**
- High: Clear topics, structured content
- Medium: Mixed concepts, needs organization
- Low: Requires manual review or splitting

### Batch Processing

**Multiple files:**
- Process sequentially
- Group by topic similarity
- Create index note if needed
- Report summary of conversions

**Conflict resolution:**
- Duplicate titles: Add timestamp or increment
- Missing attachments: Warn and continue
- Parse errors: Flag for manual review

## File Operations

### Directory Structure

```
notes/
├── Drafts/              # Source files
│   ├── raw-ideas.md
│   ├── workout-notes.md
│   └── image1.png
├── References/          # Output notes
│   ├── Raw Ideas.md
│   └── Workout Notes.md
└── Attachments/         # Processed files
    ├── Raw Ideas-image1.png
    └── Workout Notes-plan.png
```

### Safety Features

**Before operations:**
- Verify source files exist
- Check destination availability
- Validate attachment paths
- Confirm template exists

**During operations:**
- Create backup of original if needed
- Atomic file operations where possible
- Error handling with rollback capability

**After operations:**
- Verify note creation
- Confirm attachment placement
- Validate content integrity
- Clean up temporary files

## Usage Examples

### Single File Conversion

```
User: "Convert draft 'project-ideas.md' to a note"
```

**Process:**
1. Read `Drafts/project-ideas.md`
2. Extract topics: `[[Projects]]`, `[[Ideas]]`
3. Check for attachments in content
4. Create `References/Project Ideas.md`
5. Move attachments to `Attachments/`
6. Delete original draft

### Batch Processing

```
User: "Process all my drafts into notes"
```

**Process:**
1. List all files in `Drafts/`
2. Group by content similarity
3. Process each file individually
4. Create summary note with links
5. Report completion status

### With Custom Topics

```
User: "Convert 'meeting-notes.md' with topics [[Work]] and [[Meetings]]"
```

**Process:**
1. Read draft file
2. Use provided topics in frontmatter
3. Add additional topics from content analysis
4. Create formatted note
5. Handle any attachments

## Error Handling

### Common Issues

**Missing Drafts directory:**
- Create directory automatically
- Prompt user to add files
- Suggest alternative locations

**Template not found:**
- Fall back to basic format
- Create minimal template
- Alert user to configure

**Attachment errors:**
- Skip problematic files
- Log errors for review
- Continue with other files

**Parse errors:**
- Try alternative parsers
- Preserve raw content
- Flag for manual review

### Recovery Options

**Partial failures:**
- Continue with remaining files
- Create error log
- Suggest manual fixes

**Complete failures:**
- Preserve original files
- Provide detailed error messages
- Suggest troubleshooting steps

## Best Practices

### Draft Preparation

**Before processing:**
- Organize related content together
- Use clear filenames
- Include relevant keywords
- Note any special requirements

### After Processing

**Review created notes:**
- Verify topics are accurate
- Check attachment placement
- Test internal links
- Add additional connections

**Maintain organization:**
- Regular cleanup of Drafts
- Archive processed files
- Update templates as needed
- Monitor attachment folder size

## Troubleshooting

### Common Problems

**Notes not created:**
- Check Drafts directory path
- Verify file permissions
- Ensure template exists

**Attachments missing:**
- Confirm attachment detection
- Check file paths in content
- Verify destination directory

**Topics incorrect:**
- Review content analysis
- Manually specify topics
- Update topic extraction logic

**Links broken:**
- Verify note naming
- Check link format
- Test backlink functionality

### Getting Help

**For issues:**
1. Check error messages in console
2. Review created notes for accuracy
3. Verify directory structure
4. Test with single file first

**For improvements:**
- Suggest new topic patterns
- Request attachment handling updates
- Propose template modifications
- Share workflow suggestions

---

## Implementation Details

This skill provides Python scripts for processing drafts and managing attachments. The core functionality is implemented in the scripts directory.
