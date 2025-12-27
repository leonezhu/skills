#!/usr/bin/env python3
"""
Validate draft2note skill structure
"""

import sys
import os
from pathlib import Path


def validate_skill_structure(skill_dir: Path) -> bool:
    """Validate that the skill has all required components."""

    print(f"🔍 Validating skill structure: {skill_dir}")

    # Check required files
    required_files = {
        'SKILL.md': 'Skill definition file',
        'scripts/process_drafts.py': 'Main processing script',
    }

    optional_files = {
        'scripts/test_drafts.py': 'Test script',
        'scripts/validate_skill.py': 'This validation script',
        'references/processing_patterns.md': 'Processing patterns reference',
        'references/usage_examples.md': 'Usage examples',
        'README.md': 'User documentation',
    }

    all_good = True

    # Check required files
    print("\n📋 Required files:")
    for file_path, description in required_files.items():
        full_path = skill_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path} - {description}")
        else:
            print(f"   ❌ {file_path} - {description} - MISSING")
            all_good = False

    # Check optional files
    print("\n📋 Optional files:")
    for file_path, description in optional_files.items():
        full_path = skill_dir / file_path
        if full_path.exists():
            print(f"   ✅ {file_path} - {description}")
        else:
            print(f"   ⚠️  {file_path} - {description} - Optional")

    # Check SKILL.md content
    print("\n📋 SKILL.md validation:")
    skill_md = skill_dir / "SKILL.md"
    if skill_md.exists():
        content = skill_md.read_text()

        # Check frontmatter
        if content.startswith('---'):
            print("   ✅ Frontmatter present")
        else:
            print("   ❌ Frontmatter missing")
            all_good = False

        # Check required fields
        if 'name: draft2note' in content:
            print("   ✅ Name field correct")
        else:
            print("   ❌ Name field incorrect")
            all_good = False

        if 'description:' in content:
            print("   ✅ Description present")
        else:
            print("   ❌ Description missing")
            all_good = False

        # Check body sections
        required_sections = ['# Draft2note', '## Overview', '## Quick Start', '## Core Workflow']
        for section in required_sections:
            if section in content:
                print(f"   ✅ Section: {section}")
            else:
                print(f"   ❌ Section: {section} - Missing")
                all_good = False

    # Check script executability
    print("\n📋 Script permissions:")
    process_script = skill_dir / "scripts/process_drafts.py"
    if process_script.exists():
        is_executable = os.access(process_script, os.X_OK)
        if is_executable:
            print("   ✅ process_drafts.py is executable")
        else:
            print("   ⚠️  process_drafts.py not executable (chmod +x recommended)")

    # Check imports
    print("\n📋 Python script validation:")
    try:
        sys.path.insert(0, str(skill_dir / "scripts"))
        from process_drafts import DraftProcessor
        print("   ✅ process_drafts.py imports successfully")

        # Test basic functionality
        from pathlib import Path
        processor = DraftProcessor(Path("/tmp"), dry_run=True)
        print("   ✅ DraftProcessor can be instantiated")

    except Exception as e:
        print(f"   ❌ Script import error: {e}")
        all_good = False

    return all_good


def main():
    """Main validation function."""

    # Find skill directory
    skill_dir = Path(__file__).parent.parent
    print(f"Skill directory: {skill_dir}\n")

    # Validate
    is_valid = validate_skill_structure(skill_dir)

    # Summary
    print("\n" + "="*50)
    if is_valid:
        print("✅ Skill validation PASSED")
        print("   The draft2note skill is properly structured and ready to use.")
        return 0
    else:
        print("❌ Skill validation FAILED")
        print("   Please fix the issues above.")
        return 1


if __name__ == "__main__":
    sys.exit(main())