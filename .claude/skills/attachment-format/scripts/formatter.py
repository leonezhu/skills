#!/usr/bin/env python3
"""
附件格式化工具
自动整理附件命名，根据引用上下文重命名，清理未使用的附件
"""

import os
import re
import shutil
from pathlib import Path
from typing import List, Dict, Tuple, Optional


class AttachmentFormatter:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.attachments_dir = self.base_path / "Attachments"
        self.notes_dirs = ["References", "Categories", "Daily", "Templates"]

    def scan_attachments(self) -> List[Path]:
        """扫描附件目录，返回所有文件"""
        if not self.attachments_dir.exists():
            print(f"❌ 附件目录不存在: {self.attachments_dir}")
            return []

        files = []
        for file in self.attachments_dir.iterdir():
            if file.is_file():
                files.append(file)
        return files

    def is_valid_filename(self, filename: str) -> bool:
        """检查文件名是否规范"""
        # 规范的文件名：中文+描述+扩展名
        # 不规范：纯数字、纯英文、随机字符、截图工具默认命名

        # 排除常见不规范模式
        patterns = [
            r'^\d+\.png$',  # 8020.png
            r'^Pasted image \d+\.png$',  # Pasted image 20251208212204.png
            r'^\d{8}\d+\.png$',  # 20251208212204.png
            r'^[a-zA-Z0-9_]+\.md$',  # 纯英文文件名
        ]

        for pattern in patterns:
            if re.match(pattern, filename):
                return False

        # 包含中文或明确主题的视为规范
        if re.search(r'[\u4e00-\u9fff]', filename):
            return True

        return True

    def find_references(self, filename: str) -> List[Tuple[Path, int, str]]:
        """查找文件在哪些笔记中被引用"""
        references = []
        search_patterns = [
            f"![[{filename}]]",
            f"![[{filename}|",
            f"[[{filename}]]",
        ]

        for note_dir in self.notes_dirs:
            dir_path = self.base_path / note_dir
            if not dir_path.exists():
                continue

            for note_file in dir_path.glob("*.md"):
                try:
                    content = note_file.read_text(encoding='utf-8')
                    for line_num, line in enumerate(content.split('\n'), 1):
                        if any(pattern in line for pattern in search_patterns):
                            references.append((note_file, line_num, line.strip()))
                except Exception as e:
                    print(f"⚠️ 无法读取 {note_file}: {e}")

        return references

    def extract_context(self, note_file: Path, line_num: int, line: str) -> Dict[str, str]:
        """从引用位置提取上下文信息"""
        context = {
            "note_name": note_file.stem,
            "line_content": line,
            "surrounding_text": "",
            "keywords": [],
            "description": ""
        }

        try:
            content = note_file.read_text(encoding='utf-8')
            lines = content.split('\n')

            # 获取前后几行作为上下文
            start = max(0, line_num - 3)
            end = min(len(lines), line_num + 2)
            surrounding = lines[start:end]
            context["surrounding_text"] = "\n".join(surrounding)

            # 停用词
            stop_words = {"的", "了", "和", "与", "在", "是", "就", "都", "而", "及", "or", "and", "the", "a", "an", "this", "that", "with", "for"}

            # 1. 从笔记名提取主题（优先使用中文）
            note_name = note_file.stem
            # 移除英文和数字，保留中文
            chinese_only = re.sub(r'[a-zA-Z0-9\s]', '', note_name).strip()
            if chinese_only:
                context["keywords"].append(chinese_only)
            else:
                # 如果没有中文，使用整个笔记名
                context["keywords"].append(note_name)

            # 2. 从引用行提取描述
            # 移除 ![[...]] 部分
            line_clean = re.sub(r'!?\[\[.*?\]\]', '', line)
            # 提取关键词
            words = re.findall(r'[\u4e00-\u9fff]+|[a-zA-Z]{3,}', line_clean)
            for w in words:
                if w not in stop_words and len(w) > 1:
                    context["keywords"].append(w)

            # 3. 从周围文本提取关键描述词
            for text in surrounding:
                # 查找图片前后的描述性文字
                if "截图" in text or "示例" in text or "图" in text or "图片" in text:
                    # 提取这些词
                    desc_words = re.findall(r'[\u4e00-\u9fff]{2,}', text)
                    for w in desc_words:
                        if w not in stop_words:
                            context["keywords"].append(w)

            # 去重并保留前3个
            context["keywords"] = list(set(context["keywords"]))[:3]

            # 生成描述
            if "截图" in context["surrounding_text"]:
                context["description"] = "截图"
            elif "示例" in context["surrounding_text"]:
                context["description"] = "示例"
            elif "图" in context["surrounding_text"] or "图片" in context["surrounding_text"]:
                context["description"] = "图"

        except Exception as e:
            print(f"⚠️ 提取上下文失败: {e}")

        return context

    def generate_new_filename(self, old_filename: str, context: Dict[str, str]) -> str:
        """根据上下文生成新文件名"""
        ext = Path(old_filename).suffix

        # 提取核心关键词
        keywords = context["keywords"]

        if not keywords:
            # 如果没有提取到关键词，使用笔记名
            keywords = [context["note_name"]]

        # 组合新文件名
        # 优先级：主题-描述-类型
        parts = []

        # 第一部分：主题（笔记名）
        if keywords:
            parts.append(keywords[0])

        # 第二部分：描述（如果有）
        if len(keywords) > 1:
            parts.append(keywords[1])
        elif context["description"]:
            parts.append(context["description"])

        # 组合
        new_name = "-".join(parts) + ext

        # 清理特殊字符（保留中文、字母、数字、短横线、点）
        new_name = re.sub(r'[^\w\u4e00-\u9fff\-\.]', '_', new_name)

        # 避免过长
        if len(new_name) > 50:
            new_name = new_name[:40] + ext

        return new_name

    def check_name_conflict(self, new_filename: str) -> bool:
        """检查新文件名是否已存在"""
        return (self.attachments_dir / new_filename).exists()

    def rename_and_update(self, old_filename: str, new_filename: str, references: List[Tuple[Path, int, str]]):
        """重命名文件并更新所有引用"""
        old_path = self.attachments_dir / old_filename
        new_path = self.attachments_dir / new_filename

        print(f"\n📁 重命名: {old_filename} → {new_filename}")

        # 1. 重命名文件
        try:
            shutil.move(str(old_path), str(new_path))
            print(f"  ✅ 文件已重命名")
        except Exception as e:
            print(f"  ❌ 重命名失败: {e}")
            return

        # 2. 更新引用
        updated_files = set()
        for note_file, line_num, line in references:
            try:
                content = note_file.read_text(encoding='utf-8')

                # 替换所有引用格式
                new_content = content.replace(
                    f"![[{old_filename}]]",
                    f"![[{new_filename}]]"
                )
                new_content = new_content.replace(
                    f"![[{old_filename}|",
                    f"![[{new_filename}|"
                )
                new_content = new_content.replace(
                    f"[[{old_filename}]]",
                    f"[[{new_filename}]]"
                )

                if new_content != content:
                    note_file.write_text(new_content, encoding='utf-8')
                    updated_files.add(note_file)
                    print(f"  ✅ 更新引用: {note_file.name}")
            except Exception as e:
                print(f"  ❌ 更新失败 {note_file.name}: {e}")

        if not updated_files:
            print(f"  ⚠️ 未找到需要更新的引用")

    def find_unused_attachments(self) -> List[str]:
        """查找未被引用的附件"""
        all_attachments = [f.name for f in self.scan_attachments()]
        used_attachments = set()

        # 扫描所有笔记，提取引用
        for note_dir in self.notes_dirs:
            dir_path = self.base_path / note_dir
            if not dir_path.exists():
                continue

            for note_file in dir_path.glob("*.md"):
                try:
                    content = note_file.read_text(encoding='utf-8')
                    # 匹配 ![[filename]] 或 [[filename]]
                    matches = re.findall(r'!?\[\[([^\]]+)\]\]', content)
                    used_attachments.update(matches)
                except Exception as e:
                    print(f"⚠️ 无法读取 {note_file}: {e}")

        # 找出未使用的
        unused = [f for f in all_attachments if f not in used_attachments]
        return unused

    def process_all(self, dry_run: bool = True):
        """处理所有附件"""
        print("=" * 60)
        print("附件格式化工具")
        print("=" * 60)

        # 1. 扫描附件
        files = self.scan_attachments()
        if not files:
            print("未找到附件")
            return

        print(f"\n📊 扫描到 {len(files)} 个附件")

        # 2. 分析每个文件
        to_rename = []
        for file in files:
            filename = file.name

            # 检查是否需要重命名
            if self.is_valid_filename(filename):
                continue

            # 查找引用
            references = self.find_references(filename)

            if not references:
                print(f"\n⚠️  {filename} - 未被引用")
                continue

            # 提取上下文
            context = self.extract_context(references[0][0], references[0][1], references[0][2])

            # 生成新名称
            new_filename = self.generate_new_filename(filename, context)

            # 检查冲突
            if self.check_name_conflict(new_filename):
                print(f"\n⚠️  {filename} → {new_filename} (名称冲突，跳过)")
                continue

            to_rename.append((filename, new_filename, references))

            print(f"\n📝 {filename}")
            print(f"   → {new_filename}")
            print(f"   引用自: {', '.join([r[0].name for r in references])}")
            print(f"   上下文: {context['keywords']}")

        # 3. 执行重命名
        if to_rename:
            print(f"\n" + "=" * 60)
            print(f"准备重命名 {len(to_rename)} 个文件")
            print("=" * 60)

            if dry_run:
                print("\n🔍 预览模式（未实际执行）")
                print("使用 --execute 参数执行实际重命名")
            else:
                for old, new, refs in to_rename:
                    self.rename_and_update(old, new, refs)

        # 4. 检查未使用附件
        print("\n" + "=" * 60)
        print("检查未使用的附件")
        print("=" * 60)

        unused = self.find_unused_attachments()
        if unused:
            print(f"\n发现 {len(unused)} 个未使用的附件:")
            for f in unused:
                print(f"  - {f}")

            if not dry_run:
                response = input("\n是否删除这些文件？(y/n): ")
                if response.lower() == 'y':
                    for f in unused:
                        path = self.attachments_dir / f
                        try:
                            path.unlink()
                            print(f"已删除: {f}")
                        except Exception as e:
                            print(f"删除失败 {f}: {e}")
        else:
            print("\n✅ 未发现未使用的附件")

        print("\n" + "=" * 60)
        print("完成")
        print("=" * 60)


def main():
    import sys

    formatter = AttachmentFormatter()

    # 检查参数
    dry_run = "--execute" not in sys.argv

    if "--help" in sys.argv or "-h" in sys.argv:
        print("""
附件格式化工具

用法:
  python formatter.py           # 预览模式
  python formatter.py --execute # 执行重命名和删除

功能:
  1. 扫描 Attachments/ 目录
  2. 识别不规范的文件名
  3. 根据引用上下文生成新名称
  4. 重命名文件并更新引用
  5. 检测并提示删除未使用的附件

示例:
  8020.png → 8020-销售法则.png
  Pasted image 20251208212204.png → Sublime-空行清理示例.png
        """)
        return

    formatter.process_all(dry_run=dry_run)


if __name__ == "__main__":
    main()
