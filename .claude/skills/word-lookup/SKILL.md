---
name: word-lookup
description: English word dictionary lookup with pronunciation, definitions, examples, etymology, and synonyms. Use when users want to look up English words, learn vocabulary, or create word study notes. Creates structured notes in References/ directory using base template and outputs concise word information to console.
---

# Word Lookup

## Overview

This skill enables comprehensive English word dictionary lookups with detailed linguistic information. It creates structured word notes in the Obsidian References directory and displays concise summaries in the console.

## Core Workflow

### 1. Word Lookup Process

When a user requests a word lookup:
1. **Fetch word data** - Get pronunciation, definitions, examples, etymology, and synonyms
2. **Generate note content** - Format according to base template structure
3. **Save to References/** - Create markdown file with word information
4. **Output to console** - Display concise summary

### 2. Note Structure

Word notes are saved to `References/` directory with filename format: `word-name.md`

The note follows `/Templates/Base Template.md` format and includes:

**Front Matter:**
```yaml
---
created: YYYY-MM-DD
created_at: '[[YYYY-MM-DD]]'
topics:
  - "[[English]]"
  - "[[Vocabulary]]"
aliases:
  - word
tags:
  - vocabulary
  - english
  - word-lookup
---
```

**Content Sections:**
- **Pronunciation** - IPA notation and phonetic spelling
- **Part of Speech** - Word category (noun, verb, adjective, etc.)
- **Definitions** - Multiple meanings with context
- **Examples** - Usage sentences
- **Etymology** - Word origin and history
- **Synonyms** - Related words with similar meanings

### 3. Console Output

After creating the note, displays:
```
[WORD] - [Part of Speech]
Pronunciation: [IPA] ([phonetic])
Definition: [primary meaning]
Examples: [1-2 example sentences]
Etymology: [origin]
Synonyms: [list of synonyms]
Note: Created at References/word-name.md
```

## Usage

### Basic Usage

Run the word lookup script from the notes root directory:

```bash
python .claude/skills/word-lookup/scripts/lookup_word.py <word>
```

**Examples:**
```bash
python .claude/skills/word-lookup/scripts/lookup_word.py ephemeral
python .claude/skills/word-lookup/scripts/lookup_word.py "quantum leap"
python .claude/skills/word-lookup/scripts/lookup_word.py serendipity
```

### Integration with Claude

When users ask to look up words:
1. Execute the lookup script
2. The script creates a note in `References/`
3. Display the console output to the user
4. Optionally link to the created note using `[[word-name]]`

## Script Implementation

### `scripts/lookup_word.py`

The main script handles word lookup and note creation:

**Key Functions:**
- `lookup_word(word, api_key_mw)` - Fetches word data from multiple dictionary APIs
- `fetch_from_wiktionary(word)` - Fetches from Wiktionary (free, no API key)
- `fetch_from_dictionaryapi(word)` - Fetches from DictionaryAPI.dev (free, no API key)
- `fetch_from_merriam_webster(word, api_key)` - Fetches from Merriam-Webster (requires API key)
- `format_note_content(word_data)` - Formats data into markdown with base template
- `create_word_note(word, references_dir, word_data)` - Creates note file in References/
- `output_console_summary(word_data, note_path)` - Displays concise output

**Dependencies:**
- Python 3.x
- `requests` library: `pip install requests`
- Obsidian vault with `References/` and `Templates/` directories

**API Sources (in priority order):**
1. **Merriam-Webster** - Requires API key from https://www.dictionaryapi.com/
   - Set environment variable: `MW_API_KEY`
   - Most comprehensive and authoritative

2. **DictionaryAPI.dev** - Free, no API key needed
   - https://api.dictionaryapi.dev/
   - Good for common words

3. **Wiktionary API** - Free, no API key needed
   - https://en.wiktionary.org/api/rest_v1/
   - Fallback option

**Note:** The script tries each source in order until it gets data. If all fail, it creates a placeholder note.

## Resources

### scripts/
- `lookup_word.py` - Main word lookup and note creation script

### references/
- (Optional) API documentation for dictionary services
- (Optional) Word data schemas

### assets/
- (Not needed for this skill)

---

## Example Output

When looking up the word "ephemeral":

```
Looking up 'ephemeral'...
  Trying Merriam-Webster... ✗
  Trying DictionaryAPI... ✓

============================================================
📖 EPHEMERAL - adjective
============================================================
Pronunciation: /ɪˈfemərəl/ (ih-fem-uh-ruhl)
Definition: lasting for a very short time
Examples: The mayfly is an ephemeral creature, living only one day.
Etymology: From Dictionary API entry for 'ephemeral'
Synonyms: transient, fleeting, momentary, temporary, evanescent
============================================================
✅ Note created: /path/to/notes/References/ephemeral.md
============================================================

Obsidian link: [[ephemeral]]
```

The note file `References/ephemeral.md` will contain the full structured information:

```markdown
---
created: 2025-12-24
created_at: '[[2025-12-24]]'
topics:
  - "[[English]]"
  - "[[Vocabulary]]"
aliases:
  - ephemeral
tags:
  - vocabulary
  - english
  - word-lookup
---
# Ephemeral

## Pronunciation
- IPA: `/ɪˈfemərəl/`
- Phonetic: **ih-fem-uh-ruhl**

## Part of Speech
adjective

## Definitions
1. lasting for a very short time
2. short-lived, transient

## Examples
- The mayfly is an ephemeral creature, living only one day.
- Beauty is often ephemeral, like morning dew.

## Etymology
From Dictionary API entry for 'ephemeral'

## Synonyms
transient, fleeting, momentary, temporary, evanescent

---

## Related
![[Backlinks.base]]
```
