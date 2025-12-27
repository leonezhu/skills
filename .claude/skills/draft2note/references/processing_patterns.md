# Draft Processing Patterns

## Topic Extraction Patterns

### Explicit Topic Markers

The processor looks for these patterns in content:

```markdown
## 主题: [[Topic1]], [[Topic2]]
## Topics: [[Health]], [[Exercise]]
## 分类: [[People]]
## Categories: [[Books]]
```

### Alias Patterns

```markdown
别名: Alternative Name
aliases: Alt1, Alt2
also known as: Nickname
```

## Title Extraction Priority

1. **First heading** (`# Title`)
2. **Filename** (converted to Title Case)
3. **Generated** (from first sentence)

## Attachment Patterns

### Embedded Images

```markdown
![description](path/to/image.png)
![截图](screenshot.jpg)
```

### Linked Files

```markdown
[document.pdf](files/document.pdf)
[Download](attachment.pdf)
```

## Filename Sanitization

### Rules
- Remove special characters: `!@#$%^&*()`
- Replace spaces with hyphens
- Keep Chinese characters
- Preserve word boundaries

### Examples

| Original | Sanitized |
|----------|-----------|
| `my notes.md` | `My-Notes.md` |
| `健身计划.md` | `健身计划.md` |
| `draft-1.md` | `Draft-1.md` |

## Attachment Naming

### Format
```
{note-title}-{original-name}.{ext}
```

### Examples
- `新手健身注意事项-training-plan.png`
- `My-Ideas-screenshot.png`
- `项目想法-设计图.jpg`

## Conflict Resolution

### Duplicate Titles

When `References/Title.md` exists:

1. Try `Title-1.md`
2. Try `Title-2.md`
3. Continue until unique

### Missing Attachments

- Log warning
- Continue processing
- Report at end

## Error Handling

### Common Errors

| Error | Cause | Solution |
|-------|-------|----------|
| File not found | Wrong path | Verify Drafts directory |
| Permission denied | File locked | Close file in other apps |
| Invalid YAML | Special chars in frontmatter | Sanitize content |
| Missing template | Base template not found | Use basic format |

### Recovery

1. **Preserve original** - Never delete on error
2. **Log details** - Save error information
3. **Continue batch** - Process other files
4. **Report summary** - Show what failed

## Content Analysis

### Keyword Extraction

**Process:**
1. Remove markdown syntax
2. Split into words
3. Filter stop words
4. Count frequency
5. Return top 5

**Stop words:**
- English: the, a, an, and, or, but, in, on, at...
- Chinese: 的, 了, 和, 就, 都, 而, 及, 与...

### Topic Suggestions

Based on:
- Repeated keywords
- Existing note topics
- Category patterns
- User hints

## Template Integration

### Base Template Structure

```
---
created: YYYY-MM-DD
created_at: [[YYYY-MM-DD]]
topics:
  - "[[Topic]]"
aliases:
  - Alias
---

[Content]

![[Backlinks.base]]
```

### Dynamic Elements

- Date calculation
- Automatic linking
- Backlink insertion

## Batch Processing

### Sequential Processing

```
1. file1.md → Note 1
2. file2.md → Note 2
3. file3.md → Note 3
```

### Grouping Strategy

**By topic similarity:**
- Extract topics from all files
- Group similar topics
- Create index note for each group

**By content type:**
- Meeting notes together
- Research notes together
- Ideas together

### Summary Generation

**Index note includes:**
- Processing date
- Files processed
- Topics covered
- Links to all notes

## Quality Checks

### Before Saving

- [ ] Frontmatter valid
- [ ] Topics formatted as links
- [ ] Attachments moved
- [ ] Paths updated
- [ ] Content readable

### After Processing

- [ ] Note exists in References/
- [ ] Attachments in Attachments/
- [ ] Original removed (if not keep-original)
- [ ] Links work in Obsidian
- [ ] Backlinks functional

## Performance Optimization

### Large Files

- Process in chunks if >10MB
- Stream content reading
- Batch attachment moves

### Many Files

- Process in parallel (if supported)
- Show progress indicators
- Report summary statistics

### Memory Usage

- Clean up temp files
- Close file handles
- Release unused resources