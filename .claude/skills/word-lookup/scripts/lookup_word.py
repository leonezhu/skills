#!/usr/bin/env python3
"""
Word Lookup Script

Fetches word information from dictionary APIs and creates structured notes in the References directory.
Outputs concise word information to console.

Usage:
    python lookup_word.py <word>
    python lookup_word.py "multiple words"

Example:
    python lookup_word.py ephemeral
    python lookup_word.py "quantum leap"
    python lookup_word.py serendipity

Requirements:
    - requests library: pip install requests
    - For production: Add API keys for Merriam-Webster or Oxford Dictionary
"""

import sys
import datetime
import re
from pathlib import Path

try:
    import requests
except ImportError:
    print("Error: 'requests' library not found.")
    print("Install with: pip install requests")
    sys.exit(1)


def clean_html(text):
    """Remove HTML tags and entities from text."""
    if not text:
        return ''
    # Remove HTML tags
    text = re.sub(r'<[^>]+>', '', text)
    # Remove HTML entities
    text = re.sub(r'&[^;]+;', '', text)
    # Clean up whitespace
    text = ' '.join(text.split())
    return text


def fetch_from_wiktionary(word):
    """
    Fetch word data from Wiktionary API.
    This is a free API that doesn't require authentication.

    Returns None if word not found or API fails.
    """
    try:
        # Wiktionary API endpoint
        url = f"https://en.wiktionary.org/api/rest_v1/page/definition/{word}"
        headers = {'User-Agent': 'WordLookupBot/1.0'}

        response = requests.get(url, headers=headers, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        # Extract English definitions
        if 'en' not in data:
            return None

        en_data = data['en']

        # Extract parts of speech and definitions
        definitions = []
        part_of_speech = []
        examples = []
        synonyms = []

        for category in en_data:
            pos = category.get('partOfSpeech', '')
            if pos:
                part_of_speech.append(pos)

            for definition in category.get('definitions', []):
                def_text = definition.get('definition', '')
                if def_text:
                    # Clean HTML from definition
                    clean_def = clean_html(def_text)
                    if clean_def:
                        definitions.append(clean_def)

                # Get examples
                if 'examples' in definition:
                    for example in definition['examples']:
                        clean_ex = clean_html(example)
                        if clean_ex:
                            examples.append(clean_ex)

        # Get pronunciation (simplified)
        pronunciation = f"/{word}/"  # Placeholder
        phonetic = word

        # Try to get pronunciation from the page
        try:
            page_url = f"https://en.wiktionary.org/api/rest_v1/page/html/{word}"
            page_response = requests.get(page_url, headers=headers, timeout=10)
            if page_response.status_code == 200:
                html = page_response.text

                # Look for IPA pronunciation
                ipa_match = re.search(r'<span class="IPA">([^<]+)</span>', html)
                if ipa_match:
                    pronunciation = clean_html(ipa_match.group(1))

                # Look for synonyms section
                if 'Synonyms' in html:
                    # Extract synonyms (simplified)
                    syn_section = html.split('Synonyms')[1] if 'Synonyms' in html else ''
                    syn_match = re.findall(r'<li>([^<]+)</li>', syn_section[:1000])
                    if syn_match:
                        synonyms = [clean_html(s) for s in syn_match[:5]]
        except:
            pass  # Use defaults if parsing fails

        # Get etymology (simplified - would need more parsing)
        etymology = f"From Wiktionary. See full entry at https://en.wiktionary.org/wiki/{word}"

        # If no definitions found, return None
        if not definitions:
            return None

        return {
            'word': word,
            'pronunciation': pronunciation,
            'phonetic': phonetic,
            'part_of_speech': ', '.join(part_of_speech) if part_of_speech else 'unknown',
            'definitions': definitions[:3],  # Take first 3
            'examples': examples[:2] if examples else [f"Example usage of '{word}'"],
            'etymology': etymology,
            'synonyms': synonyms if synonyms else ['(see Wiktionary)']
        }

    except Exception as e:
        print(f"  [Wiktionary API error: {e}]", file=sys.stderr)
        return None


def fetch_from_dictionaryapi(word):
    """
    Fetch word data from free Dictionary API (https://api.dictionaryapi.dev/).
    This API doesn't require authentication but may have rate limits.

    Returns None if word not found or API fails.
    """
    try:
        url = f"https://api.dictionaryapi.dev/api/v2/entries/en/{word}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if not data or not isinstance(data, list):
            return None

        entry = data[0]

        # Extract word
        word_text = entry.get('word', word)

        # Extract phonetics
        phonetics = entry.get('phonetics', [])
        pronunciation = '/'
        phonetic = word

        for ph in phonetics:
            if ph.get('text'):
                pronunciation = ph['text']
            if ph.get('audio'):
                # There's audio, but we just need text
                pass

        # Extract meanings
        meanings = entry.get('meanings', [])

        definitions = []
        part_of_speech = []
        examples = []
        synonyms = []

        for meaning in meanings:
            pos = meaning.get('partOfSpeech', '')
            if pos:
                part_of_speech.append(pos)

            for def_obj in meaning.get('definitions', []):
                def_text = def_obj.get('definition', '')
                if def_text:
                    definitions.append(def_text)

                example = def_obj.get('example', '')
                if example:
                    examples.append(example)

                syns = def_obj.get('synonyms', [])
                if syns:
                    synonyms.extend(syns)

        # Get etymology (not provided by this API)
        etymology = f"From Dictionary API entry for '{word}'"

        if not definitions:
            return None

        return {
            'word': word_text,
            'pronunciation': pronunciation if pronunciation != '/' else f"/{word}/",
            'phonetic': phonetic,
            'part_of_speech': ', '.join(part_of_speech) if part_of_speech else 'unknown',
            'definitions': definitions[:3],
            'examples': examples[:2] if examples else [f"Example usage of '{word}'"],
            'etymology': etymology,
            'synonyms': list(set(synonyms))[:5] if synonyms else ['(not available)']
        }

    except Exception as e:
        print(f"  [DictionaryAPI error: {e}]", file=sys.stderr)
        return None


def fetch_from_merriam_webster(word, api_key=None):
    """
    Fetch word data from Merriam-Webster Collegiate Dictionary API.
    Requires API key from https://www.dictionaryapi.com/

    Returns None if word not found or API fails.
    """
    if not api_key:
        return None

    try:
        url = f"https://www.dictionaryapi.com/api/v3/references/collegiate/json/{word}?key={api_key}"
        response = requests.get(url, timeout=10)

        if response.status_code != 200:
            return None

        data = response.json()

        if not data or not isinstance(data, list):
            return None

        entry = data[0]

        # Extract word
        word_text = entry.get('meta', {}).get('id', word)

        # Extract pronunciation
        pronunciation = entry.get('hwi', {}).get('prs', [{}])[0].get('mw', f"/{word}/")
        phonetic = pronunciation

        # Extract definitions
        definitions = []
        part_of_speech = entry.get('fl', '')
        examples = []
        synonyms = []

        for def_obj in entry.get('def', {}).get('sseq', []):
            if isinstance(def_obj, list) and len(def_obj) > 0:
                inner = def_obj[0]
                if isinstance(inner, list) and len(inner) > 1:
                    sense = inner[1]
                    dt = sense.get('dt', [])
                    if dt and isinstance(dt, list) and len(dt) > 0:
                        def_text = dt[0]
                        if isinstance(def_text, str):
                            definitions.append(def_text)
                        elif isinstance(def_text, list) and len(def_text) > 1:
                            definitions.append(def_text[1])

        # Get synonyms
        syns = entry.get('meta', {}).get('syns', [])
        if syns:
            synonyms = syns[0] if isinstance(syns, list) and syns else []

        etymology = f"From Merriam-Webster Collegiate Dictionary"

        if not definitions:
            return None

        return {
            'word': word_text,
            'pronunciation': f"/{pronunciation}/",
            'phonetic': phonetic,
            'part_of_speech': part_of_speech if part_of_speech else 'unknown',
            'definitions': definitions[:3],
            'examples': examples[:2] if examples else [f"Example usage of '{word}'"],
            'etymology': etymology,
            'synonyms': synonyms[:5] if synonyms else ['(not available)']
        }

    except Exception as e:
        print(f"  [Merriam-Webster API error: {e}]", file=sys.stderr)
        return None


def lookup_word(word, api_key_mw=None):
    """
    Lookup word information using multiple sources in order of preference.

    Priority:
    1. Merriam-Webster (if API key provided)
    2. DictionaryAPI (free, no key needed)
    3. Wiktionary (free, no key needed)

    Returns dict with:
    - pronunciation: IPA notation
    - phonetic: readable pronunciation
    - part_of_speech: word category
    - definitions: list of meanings
    - examples: usage sentences
    - etymology: origin information
    - synonyms: list of related words
    """
    print(f"Looking up '{word}'...")

    # Try Merriam-Webster first (if key provided)
    if api_key_mw:
        print("  Trying Merriam-Webster...", end='')
        result = fetch_from_merriam_webster(word, api_key_mw)
        if result:
            print(" ✓")
            return result
        print(" ✗")

    # Try DictionaryAPI
    print("  Trying DictionaryAPI...", end='')
    result = fetch_from_dictionaryapi(word)
    if result:
        print(" ✓")
        return result
    print(" ✗")

    # Try Wiktionary
    print("  Trying Wiktionary...", end='')
    result = fetch_from_wiktionary(word)
    if result:
        print(" ✓")
        return result
    print(" ✗")

    # All failed - return generic placeholder
    print(f"  All sources failed. Using placeholder data.")
    return {
        'word': word,
        'pronunciation': '/wɜːrd/',
        'phonetic': 'wurd',
        'part_of_speech': 'noun',
        'definitions': [
            f'Word: "{word}"',
            'Definition not available from online sources'
        ],
        'examples': [
            f'You can look up "{word}" in a dictionary.',
            f'The word "{word}" has interesting usage.'
        ],
        'etymology': 'Etymology information not available. Try checking Wiktionary manually.',
        'synonyms': ['term', 'expression', 'vocabulary']
    }


def format_note_content(word_data):
    """Format word data into markdown note content following base template."""

    today = datetime.date.today().isoformat()

    # Front matter (based on Base Template.md)
    front_matter = f"""---
created: {today}
created_at: '[[{today}]]'
topics:
  - "[[English]]"
  - "[[Vocabulary]]"
aliases:
  - {word_data['word']}
tags:
  - vocabulary
  - english
  - word-lookup
---
"""

    # Content sections
    content = []
    content.append(f"# {word_data['word'].capitalize()}")
    content.append("")

    # Pronunciation
    content.append("## Pronunciation")
    content.append(f"- IPA: `{word_data['pronunciation']}`")
    content.append(f"- Phonetic: **{word_data['phonetic']}**")
    content.append("")

    # Part of Speech
    content.append("## Part of Speech")
    content.append(word_data['part_of_speech'])
    content.append("")

    # Definitions
    content.append("## Definitions")
    for i, definition in enumerate(word_data['definitions'], 1):
        content.append(f"{i}. {definition}")
    content.append("")

    # Examples
    content.append("## Examples")
    for example in word_data['examples']:
        content.append(f"- {example}")
    content.append("")

    # Etymology
    content.append("## Etymology")
    content.append(word_data['etymology'])
    content.append("")

    # Synonyms
    content.append("## Synonyms")
    content.append(", ".join(word_data['synonyms']))
    content.append("")

    # Related section (for Obsidian backlinks)
    content.append("---")
    content.append("")
    content.append("## Related")
    content.append("![[Backlinks.base]]")

    return front_matter + "\n".join(content)


def create_word_note(word, references_dir, word_data):
    """
    Create word note in References directory.

    Args:
        word: The word to look up
        references_dir: Path to References directory
        word_data: The word data dictionary

    Returns:
        Path to created note
    """
    # Format note content
    note_content = format_note_content(word_data)

    # Create filename (lowercase, replace spaces with hyphens)
    filename = f"{word.lower().replace(' ', '-')}.md"
    note_path = references_dir / filename

    # Write note
    note_path.write_text(note_content, encoding='utf-8')

    return note_path


def output_console_summary(word_data, note_path):
    """Output concise word information to console."""

    print(f"\n{'='*60}")
    print(f"📖 {word_data['word'].upper()} - {word_data['part_of_speech']}")
    print(f"{'='*60}")
    print(f"Pronunciation: {word_data['pronunciation']} ({word_data['phonetic']})")
    print(f"Definition: {word_data['definitions'][0]}")
    print(f"Examples: {word_data['examples'][0]}")
    print(f"Etymology: {word_data['etymology'][:80]}{'...' if len(word_data['etymology']) > 80 else ''}")
    print(f"Synonyms: {', '.join(word_data['synonyms'])}")
    print(f"{'='*60}")
    print(f"✅ Note created: {note_path}")
    print(f"{'='*60}\n")


def main():
    """Main entry point for word lookup."""

    if len(sys.argv) < 2:
        print("Word Lookup - Fetches word information from online dictionaries")
        print("")
        print("Usage: python lookup_word.py <word>")
        print("Example: python lookup_word.py ephemeral")
        print("Example: python lookup_word.py \"quantum leap\"")
        print("")
        print("Optional: Set MW_API_KEY environment variable for Merriam-Webster")
        sys.exit(1)

    word = sys.argv[1]

    # Get API key from environment
    import os
    api_key_mw = os.environ.get('MW_API_KEY')

    # Get References directory path
    script_path = Path(__file__).resolve()
    notes_root = script_path.parent.parent.parent.parent.parent
    references_dir = notes_root / "References"

    if not references_dir.exists():
        print(f"❌ Error: References directory not found at {references_dir}")
        print("Please ensure you're running from the notes root directory")
        sys.exit(1)

    try:
        # Lookup word data
        word_data = lookup_word(word, api_key_mw)

        # Create word note
        note_path = create_word_note(word, references_dir, word_data)

        # Output to console
        output_console_summary(word_data, note_path)

        # Also print a link for easy reference
        print(f"Obsidian link: [[{word.lower().replace(' ', '-')}]]\n")

    except Exception as e:
        print(f"❌ Error during lookup: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
