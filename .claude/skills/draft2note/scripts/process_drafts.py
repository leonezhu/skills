#!/usr/bin/env python3
"""
Draft2Note - Process draft files into formatted Obsidian notes

This script converts files from Drafts/ directory into properly formatted
notes in References/ directory, handling attachments and following the
Base template format.

Usage:
    python process_drafts.py [options]

Options:
    --file <path>      Process specific file
    --all              Process all files in Drafts/
    --dry-run          Preview without making changes
    --keep-original    Don't delete original drafts after processing
"""

import re
import sys
import shutil
import argparse
from pathlib import Path
from datetime import datetime


class DraftProcessor:
    def __init__(self, vault_root: Path, dry_run: bool = False, keep_original: bool = False):
        self.vault_root = Path(vault_root)
        self.drafts_dir = self.vault_root / "Drafts"
        self.references_dir = self.vault_root / "References"
        self.attachments_dir = self.vault_root / "Attachments"
        self.templates_dir = self.vault_root / "Templates"

        self.dry_run = dry_run
        self.keep_original = keep_original

        # Ensure directories exist
        self.references_dir.mkdir(exist_ok=True)
        self.attachments_dir.mkdir(exist_ok=True)
        self.drafts_dir.mkdir(exist_ok=True)

    def process_file(self, draft_path: Path) -> dict:
        """Process a single draft file."""
        if not draft_path.exists():
            return {"success": False, "error": f"File not found: {draft_path}"}

        try:
            # Read draft content
            content = draft_path.read_text(encoding='utf-8')

            # Extract metadata
            title = self._extract_title(draft_path, content)
            topics = self._extract_topics(content)
            aliases = self._extract_aliases(content)

            # Process attachments
            processed_content, attachments = self._process_attachments(content, draft_path, title)

            # Generate frontmatter
            frontmatter = self._generate_frontmatter(title, topics, aliases)

            # Create final note content
            note_content = self._assemble_note(frontmatter, processed_content)

            # Determine output path
            output_path = self._get_output_path(title)

            # Handle conflicts
            if output_path.exists():
                output_path = self._resolve_conflict(output_path)

            # Write note
            if not self.dry_run:
                output_path.write_text(note_content, encoding='utf-8')

                # Move attachments
                for old_path, new_path in attachments.items():
                    if old_path.exists():
                        shutil.move(str(old_path), str(new_path))

                # Delete original if not keeping
                if not self.keep_original:
                    draft_path.unlink()

            return {
                "success": True,
                "original": str(draft_path),
                "output": str(output_path),
                "title": title,
                "topics": topics,
                "attachments": len(attachments)
            }

        except Exception as e:
            return {"success": False, "error": str(e), "file": str(draft_path)}

    def _extract_title(self, draft_path: Path, content: str) -> str:
        """Extract title from filename or content."""
        # Priority 1: First heading
        match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
        if match:
            return match.group(1).strip()

        # Priority 2: Filename without extension
        name = draft_path.stem
        # Convert kebab-case/snake-case to Title Case
        title = re.sub(r'[-_]+', ' ', name).title()
        return title

    def _extract_topics(self, content: str) -> list:
        """Extract topics from content."""
        topics = []

        # Look for explicit topic markers
        topic_patterns = [
            r'##?\s+主题[:：]\s*(.+)',
            r'##?\s+Topics[:：]\s*(.+)',
            r'##?\s+Categories[:：]\s*(.+)',
            r'##?\s+分类[:：]\s*(.+)',
        ]

        for pattern in topic_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw_topics = match.group(1)
                # Split by comma or space
                for topic in re.split(r'[,，\s]+', raw_topics):
                    topic = topic.strip()
                    if topic and topic not in topics:
                        topics.append(topic)

        # If no explicit topics, analyze content for keywords
        if not topics:
            keywords = self._analyze_keywords(content)
            topics.extend(keywords[:3])  # Top 3 keywords

        # Format as Obsidian links
        formatted_topics = []
        for topic in topics:
            if not topic.startswith('[['):
                topic = f'[[{topic}]]'
            formatted_topics.append(topic)

        return formatted_topics

    def _extract_aliases(self, content: str) -> list:
        """Extract aliases from content."""
        aliases = []

        # Look for alias patterns
        alias_patterns = [
            r'别名[:：]\s*(.+)',
            r'aliases[:：]\s*(.+)',
            r'also known as[:：]\s*(.+)',
        ]

        for pattern in alias_patterns:
            match = re.search(pattern, content, re.IGNORECASE)
            if match:
                raw_aliases = match.group(1)
                for alias in re.split(r'[,，\s]+', raw_aliases):
                    alias = alias.strip()
                    if alias and alias not in aliases:
                        aliases.append(alias)

        return aliases

    def _analyze_keywords(self, content: str) -> list:
        """Analyze content to extract meaningful keywords."""
        # Remove markdown syntax
        clean_content = re.sub(r'[#*_`\[\]()]', '', content)

        # Common words to ignore
        stop_words = {'the', 'a', 'an', 'and', 'or', 'but', 'in', 'on', 'at', 'to', 'for', 'of', 'with', 'by', 'is', 'are', 'was', 'were', 'be', 'been', 'being', 'have', 'has', 'had', 'do', 'does', 'did', 'will', 'would', 'could', 'should'}

        # Extract words
        words = re.findall(r'\b[\u4e00-\u9fff\w]{2,}\b', clean_content.lower())

        # Count frequency
        word_freq = {}
        for word in words:
            if word not in stop_words:
                word_freq[word] = word_freq.get(word, 0) + 1

        # Return top keywords
        sorted_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)
        return [word for word, _ in sorted_words[:5]]

    def _process_attachments(self, content: str, draft_path: Path, title: str) -> tuple:
        """Process and move attachments."""
        attachments = {}

        # Pattern for embedded images: ![alt](path)
        image_pattern = r'!\[([^\]]*)\]\(([^)]+)\)'

        def replace_image(match):
            alt_text = match.group(1)
            old_path_str = match.group(2)

            # Resolve relative path
            old_path = draft_path.parent / old_path_str
            if not old_path.exists():
                # Try absolute path or different location
                old_path = Path(old_path_str)

            if old_path.exists():
                # Create new filename
                safe_title = re.sub(r'[^\w\u4e00-\u9fff-]', '', title.replace(' ', '-'))
                safe_name = re.sub(r'[^\w\u4e00-\u9fff-]', '', old_path.stem.replace(' ', '-'))
                new_filename = f"{safe_title}-{safe_name}{old_path.suffix}"
                new_path = self.attachments_dir / new_filename

                # Store mapping
                attachments[old_path] = new_path

                # Return updated markdown
                return f'![{alt_text}](Attachments/{new_filename})'

            return match.group(0)  # Return original if not found

        # Replace all image references
        processed_content = re.sub(image_pattern, replace_image, content)

        return processed_content, attachments

    def _generate_frontmatter(self, title: str, topics: list, aliases: list) -> str:
        """Generate YAML frontmatter."""
        today = datetime.now().strftime('%Y-%m-%d')
        date_link = f'[[{today}]]'

        lines = [
            f'created: {today}',
            f"created_at: '{date_link}'",
            'topics:'
        ]

        for topic in topics:
            lines.append(f'  - "{topic}"')

        if aliases:
            lines.append('aliases:')
            for alias in aliases:
                lines.append(f'  - {alias}')

        return '\n'.join(lines)

    def _assemble_note(self, frontmatter: str, content: str) -> str:
        """Assemble final note content."""
        # Assemble note
        note_parts = [
            '---',
            frontmatter.strip(),
            '---',
            '',
            content.strip(),
            '',
            '![[Backlinks.base]]'
        ]

        return '\n'.join(note_parts)

    def _get_output_path(self, title: str) -> Path:
        """Generate output path for note."""
        # Sanitize title for filename
        safe_title = re.sub(r'[^\w\u4e00-\u9fff\s-]', '', title)
        safe_title = safe_title.strip().replace(' ', '-')
        return self.references_dir / f"{safe_title}.md"

    def _resolve_conflict(self, path: Path) -> Path:
        """Resolve filename conflicts."""
        counter = 1
        while path.exists():
            name = path.stem
            suffix = path.suffix
            # Try adding counter
            new_name = f"{name}-{counter}{suffix}"
            path = path.parent / new_name
            counter += 1
        return path

    def process_all(self) -> list:
        """Process all files in Drafts directory."""
        results = []

        if not self.drafts_dir.exists():
            return [{"success": False, "error": "Drafts directory not found"}]

        # Get all markdown files
        draft_files = list(self.drafts_dir.glob("*.md"))
        draft_files.extend(self.drafts_dir.glob("*.txt"))

        if not draft_files:
            return [{"success": False, "error": "No draft files found"}]

        for draft_path in draft_files:
            result = self.process_file(draft_path)
            results.append(result)

        return results


def main():
    parser = argparse.ArgumentParser(description='Process draft files into formatted notes')
    parser.add_argument('--file', help='Process specific file')
    parser.add_argument('--all', action='store_true', help='Process all files in Drafts/')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--keep-original', action='store_true', help='Keep original draft files')
    parser.add_argument('--vault', default='.', help='Vault root directory')

    args = parser.parse_args()

    # Validate arguments
    if not args.file and not args.all:
        print("Error: Must specify --file or --all")
        sys.exit(1)

    # Initialize processor
    vault_root = Path(args.vault).resolve()
    processor = DraftProcessor(vault_root, args.dry_run, args.keep_original)

    # Process files
    if args.dry_run:
        print("🔍 DRY RUN MODE - No changes will be made\n")

    if args.file:
        file_path = Path(args.file)
        if not file_path.is_absolute():
            file_path = vault_root / "Drafts" / args.file

        result = processor.process_file(file_path)
        results = [result]
    else:
        results = processor.process_all()

    # Report results
    success_count = sum(1 for r in results if r.get('success'))
    total_count = len(results)

    print(f"\n📊 Processing Complete: {success_count}/{total_count} successful\n")

    for result in results:
        if result['success']:
            print(f"✅ {result['title']}")
            if result['topics']:
                print(f"   Topics: {', '.join(result['topics'])}")
            if result['attachments'] > 0:
                print(f"   Attachments: {result['attachments']}")
            print(f"   → {result['output']}")
        else:
            print(f"❌ {result.get('file', 'Unknown')}: {result['error']}")
        print()

    if args.dry_run:
        print("💡 Run without --dry-run to apply changes")

    return 0 if success_count == total_count else 1


if __name__ == '__main__':
    sys.exit(main())