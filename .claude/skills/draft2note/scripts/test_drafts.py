#!/usr/bin/env python3
"""
Test script for draft2note skill
Creates sample draft files and tests the processing
"""

import sys
from pathlib import Path

# Add parent directory to path to import process_drafts
sys.path.insert(0, str(Path(__file__).parent))

from process_drafts import DraftProcessor


def create_test_drafts():
    """Create sample draft files for testing."""
    # Use the actual vault root, not the skill directory
    vault_root = Path("/Users/xiong/Documents/GitHub/notes")
    drafts_dir = vault_root / "Drafts"
    drafts_dir.mkdir(exist_ok=True)
    print(f"Vault root: {vault_root}")
    print(f"Drafts dir: {drafts_dir}")

    # Sample draft 1: Simple text
    draft1 = drafts_dir / "健身计划.md"
    draft1.write_text("""# 新手健身注意事项

## 主题: [[Health]], [[Exercise]]

下面给你一个简单但够用的判断标准，把“正常反应 vs 警告信号”分清楚。

🟢 正常情况（不用担心）
- 肌肉酸胀、灼热感
- 轻微乏力、疲劳
- 心率上升、出汗

🔴 不正常情况（需要警惕）
- 刺痛、锐痛
- 关节卡顿、弹响伴疼
- 呼吸困难、头晕

## 注意事项
1. 重量不要追求爽，要追求稳定控制
2. 动作标准比重量重要
3. 呼吸节奏：发力呼气，回程吸气

![[训练计划.png]]
""", encoding='utf-8')

    # Sample draft 2: With attachments
    draft2 = drafts_dir / "project-ideas.md"
    draft2.write_text("""# AI 项目想法

## Topics: [[AI]], [[Projects]]

最近在思考的一些方向：

1. **智能笔记整理** - 自动分类和链接
2. **语音转文字** - 边缘计算版本
3. **知识图谱** - 个人知识管理

## 相关资源
- ![架构图](architecture.png)
- ![界面草图](ui-sketch.jpg)

别名: AI Ideas, 人工智能项目
""", encoding='utf-8')

    # Sample draft 3: Simple meeting notes
    draft3 = drafts_dir / "meeting-notes.md"
    draft3.write_text("""## 2025-12-27 项目会议

### Attendees
- Alice, Bob, Charlie

### Topics Discussed
- Q1 roadmap
- Budget allocation
- Team expansion

### Action Items
- [ ] Alice: Draft roadmap
- [ ] Bob: Budget analysis
- [ ] Charlie: Team requirements

## 分类: [[Work]], [[Meetings]]
""", encoding='utf-8')

    print(f"✅ Created test drafts in {drafts_dir}")
    return drafts_dir


def test_processing():
    """Test the draft processing functionality."""
    print("🧪 Testing draft2note skill...")

    # Create test drafts
    vault_root = Path(__file__).parent.parent.parent.parent
    create_test_drafts()

    # Test dry run first
    print("\n1. Testing dry run mode:")
    processor = DraftProcessor(vault_root, dry_run=True, keep_original=True)
    results = processor.process_all()

    for result in results:
        if result['success']:
            print(f"   ✅ {result['title']} → {result['output']}")
        else:
            print(f"   ❌ {result.get('file', 'Unknown')}: {result['error']}")

    # Test actual processing
    print("\n2. Testing actual processing:")
    processor = DraftProcessor(vault_root, dry_run=False, keep_original=False)
    results = processor.process_all()

    success_count = sum(1 for r in results if r.get('success'))
    print(f"   📊 Processed: {success_count}/{len(results)} successful")

    # Verify results
    print("\n3. Verifying results:")
    references_dir = vault_root / "References"
    attachments_dir = vault_root / "Attachments"

    if references_dir.exists():
        notes = list(references_dir.glob("*.md"))
        print(f"   📝 Notes created: {len(notes)}")
        for note in notes:
            print(f"      - {note.name}")

    if attachments_dir.exists():
        attachments = list(attachments_dir.glob("*"))
        print(f"   📎 Attachments: {len(attachments)}")
        for attachment in attachments:
            print(f"      - {attachment.name}")

    # Show sample note content
    if notes:
        sample_note = notes[0]
        print(f"\n4. Sample note content ({sample_note.name}):")
        print("   " + "="*50)
        content = sample_note.read_text(encoding='utf-8')
        for line in content.split('\n')[:15]:  # First 15 lines
            print(f"   {line}")
        print("   " + "="*50)

    print("\n✅ Test completed!")
    return success_count == len(results)


if __name__ == "__main__":
    success = test_processing()
    sys.exit(0 if success else 1)