#!/usr/bin/env python3
"""
每日计划生成器
根据周计划和前一天完成情况生成每日计划
"""

import re
import datetime
from pathlib import Path
from typing import List, Dict, Any, Optional


class DailyPlanGenerator:
    def __init__(self, base_path: str = "."):
        self.base_path = Path(base_path)
        self.daily_dir = self.base_path / "Daily"
        self.templates_dir = self.base_path / "Templates"

    def get_week_file(self, date: datetime.date) -> Optional[Path]:
        """获取周计划文件路径 (2025-W52 或 2025-12-22)"""
        week_num = date.isocalendar().week
        year = date.year

        # 尝试 2025-W52 格式
        week_file = self.daily_dir / f"{year}-W{week_num:02d}.md"
        if week_file.exists():
            return week_file

        # 尝试周一开始的日期格式
        monday = date - datetime.timedelta(days=date.weekday())
        alt_file = self.daily_dir / f"{monday.strftime('%Y-%m-%d')}.md"
        if alt_file.exists():
            return alt_file

        return week_file

    def get_yesterday_file(self, date: datetime.date) -> Optional[Path]:
        """获取昨天日志文件路径"""
        yesterday = date - datetime.timedelta(days=1)
        yesterday_file = self.daily_dir / f"{yesterday.strftime('%Y-%m-%d')}.md"
        return yesterday_file if yesterday_file.exists() else None

    def parse_week_plan(self, week_file: Path) -> List[str]:
        """解析周计划，提取未完成任务"""
        if not week_file.exists():
            return []

        content = week_file.read_text(encoding='utf-8')
        # 匹配 - [ ] 格式的任务
        pattern = r'-\s*\[\s*\]\s*(.+)'
        return [m.strip() for m in re.findall(pattern, content, re.MULTILINE) if m.strip()]

    def parse_daily_plan_tasks(self) -> List[Dict[str, Any]]:
        """解析 Daily Plan 中的任务（包括每周重复）"""
        daily_plan_file = self.daily_dir / "Daily Plan.md"
        if not daily_plan_file.exists():
            return []

        content = daily_plan_file.read_text(encoding='utf-8')
        # 跳过 frontmatter
        if "---" in content:
            parts = content.split("---")
            content = parts[2] if len(parts) >= 3 else parts[-1]

        tasks = []
        pattern = r'-\s*\[\s*\]\s*(.+)'
        for match in re.findall(pattern, content, re.MULTILINE):
            task_text = match.strip()
            if not task_text:
                continue

            # 检测每周重复任务
            weekly_match = re.search(r'每周\s*(\d+)\s*次|一周\s*(\d+)\s*次|(\d+)\s*次/周', task_text)
            if weekly_match:
                times = int(weekly_match.group(1) or weekly_match.group(2) or weekly_match.group(3))
                # 清理任务名称
                task_name = re.sub(r'[（\(].*?周.*?次.*?[）\)]', '', task_text).strip()
                tasks.append({
                    "name": task_name,
                    "type": "weekly_recurring",
                    "times": times
                })
            else:
                tasks.append({
                    "name": task_text,
                    "type": "daily",
                    "times": 1
                })

        return tasks

    def analyze_yesterday(self, yesterday_file: Path) -> Dict[str, Any]:
        """分析昨天日志，提取任务状态"""
        if not yesterday_file.exists():
            return {"completed": [], "in_progress": [], "not_completed": []}

        content = yesterday_file.read_text(encoding='utf-8')
        if "## 今日任务" in content:
            task_section = content.split("## 今日任务")[1]
            if "##" in task_section:
                task_section = task_section.split("##")[0]
        else:
            task_section = content

        completed, in_progress, not_completed = [], [], []

        for line in task_section.split('\n'):
            line = line.strip()
            if not line or not line.startswith('-'):
                continue

            # 清理任务名称
            def clean_task(text):
                text = re.sub(r'-\s*\[\s*[xX]?\s*\]', '', text)
                text = re.sub(r'[✅🔄🔴🟡⚪]', '', text)
                text = re.sub(r'\([^)]*\)|（[^）]*）', '', text)
                text = re.sub(r'\*\*', '', text)
                return re.sub(r'\s+', ' ', text).strip()

            if re.search(r'-\s*\[\s*x\s*\]', line, re.IGNORECASE):
                task_name = clean_task(line)
                if task_name:
                    completed.append(task_name)
            elif '🔄' in line:
                progress_match = re.search(r'(\d+)%', line)
                progress = int(progress_match.group(1)) if progress_match else 50
                task_name = clean_task(line)
                if task_name:
                    in_progress.append({"name": task_name, "progress": progress})
            elif '❌' in line:
                reason_match = re.search(r'原因：([^）]+)', line)
                reason = reason_match.group(1).strip() if reason_match else ""
                task_name = clean_task(line)
                if task_name:
                    not_completed.append({"name": task_name, "reason": reason})

        return {"completed": completed, "in_progress": in_progress, "not_completed": not_completed}

    def count_weekly_executions(self, week_file: Path, task_name: str) -> int:
        """统计本周任务执行次数"""
        if not week_file.exists():
            return 0

        week_num = int(week_file.stem.split('-W')[1])
        year = int(week_file.stem.split('-')[0])

        count = 0
        for daily_file in self.daily_dir.glob(f"{year}-*.md"):
            # 检查是否属于本周
            try:
                file_date = datetime.datetime.strptime(daily_file.stem, '%Y-%m-%d').date()
                if file_date.isocalendar().week != week_num or file_date.year != year:
                    continue
            except:
                continue

            content = daily_file.read_text(encoding='utf-8')
            if "## 今日任务" in content:
                task_section = content.split("## 今日任务")[1]
                if "##" in task_section:
                    task_section = task_section.split("##")[0]

                for line in task_section.split('\n'):
                    if task_name in line and re.search(r'-\s*\[\s*x\s*\]', line, re.IGNORECASE):
                        count += 1
                        break

        return count

    def generate_today_tasks(self, week_tasks: List[str], yesterday_status: Dict[str, Any], date: datetime.date) -> List[Dict[str, str]]:
        """生成今日任务列表"""
        today_tasks = []
        week_file = self.get_week_file(date)
        completed_tasks = [t.strip() for t in yesterday_status["completed"]]

        # 1. 昨日未完成（高优先级）
        for task in yesterday_status["not_completed"]:
            task_name = task["name"].strip()
            if not any(t["name"] == task_name for t in today_tasks):
                note = "昨日未完成"
                if task["reason"]:
                    note += f"（{task['reason']}）"
                today_tasks.append({
                    "name": task_name,
                    "priority": "high",
                    "note": note,
                    "emoji": "🔴"
                })

        # 2. 昨日进行中（中优先级）
        for task in yesterday_status["in_progress"]:
            task_name = task["name"].strip()
            if not any(t["name"] == task_name for t in today_tasks):
                today_tasks.append({
                    "name": task_name,
                    "priority": "medium",
                    "note": f"昨日 {task['progress']}%",
                    "emoji": "🟡"
                })

        # 3. 周计划任务
        for task in week_tasks:
            task_clean = task.strip()
            task_compare = re.sub(r'[（\(].*?周.*?次.*?[）\)]', '', task_clean).strip()

            if task_compare in completed_tasks or any(t["name"] == task_compare for t in today_tasks):
                continue

            # 每周重复任务
            if "每周" in task or "一周" in task or "次/周" in task:
                executed_count = self.count_weekly_executions(week_file, task_compare) if week_file else 0
                if executed_count < 3:  # 默认每周3次
                    today_tasks.append({
                        "name": task_compare,
                        "priority": "medium",
                        "note": f"本周第 {executed_count + 1}/3 次",
                        "emoji": "📅"
                    })
            else:
                # 普通任务
                today_tasks.append({
                    "name": task_compare,
                    "priority": "low",
                    "note": "",
                    "emoji": "⚪"
                })

        # 4. Daily Plan 任务
        daily_plan_tasks = self.parse_daily_plan_tasks()
        for task in daily_plan_tasks:
            task_name = task["name"]

            if any(t["name"] == task_name for t in today_tasks) or task_name in completed_tasks:
                continue

            if task["type"] == "weekly_recurring":
                executed_count = self.count_weekly_executions(week_file, task_name) if week_file else 0
                if executed_count < task["times"]:
                    today_tasks.append({
                        "name": task_name,
                        "priority": "medium",
                        "note": f"本周第 {executed_count + 1}/{task['times']} 次",
                        "emoji": "📅"
                    })
            else:
                today_tasks.append({
                    "name": task_name,
                    "priority": "low",
                    "note": "",
                    "emoji": "⚪"
                })

        return today_tasks

    def get_template(self) -> Optional[str]:
        """获取每日模板"""
        template_file = self.templates_dir / "Daily Note Template.md"
        return template_file.read_text(encoding='utf-8') if template_file.exists() else None

    def apply_template(self, template: str, date: datetime.date, tasks: List[Dict[str, str]]) -> str:
        """应用模板"""
        yesterday = date - datetime.timedelta(days=1)
        tomorrow = date + datetime.timedelta(days=1)
        week_str = f"{date.year}-W{date.isocalendar().week:02d}"

        # 生成任务列表
        task_lines = []
        for task in tasks:
            if task["priority"] == "high":
                task_lines.append(f"- [ ] **{task['name']}** - {task['emoji']} 优先（{task['note']}）")
            elif task["priority"] == "medium":
                task_lines.append(f"- [ ] **{task['name']}** - {task['emoji']} {task['note']}")
            else:
                task_lines.append(f"- [ ] {task['name']}")

        tasks_text = "\n".join(task_lines) if task_lines else "- [ ] "

        # 替换模板变量
        content = template

        # Frontmatter
        content = re.sub(r'created:\s*\d{4}-\d{2}-\d{2}', f'created: {date.strftime("%Y-%m-%d")}', content)
        content = re.sub(r'created_at:\s*"\[\[\d{4}-\d{2}-\d{2}\]\]"', f'created_at: "[[{date.strftime("%Y-%m-%d")}]]"', content)
        content = re.sub(r'aliases:\s*\n\s*-.*', f'aliases:\n  - {date.strftime("%B %d, %Y")}', content)
        content = re.sub(r'previous:\s*"\[\[.*?\]\]"', f'previous: "[[{yesterday.strftime("%Y-%m-%d")}]]"', content)
        content = re.sub(r'next:\s*"\[\[.*?\]\]"', f'next: "[[{tomorrow.strftime("%Y-%m-%d")}]]"', content)
        content = re.sub(r'week:\s*"\[\[.*?\]\]"', f'week: "[[{week_str}]]"', content)

        # 内容变量
        content = content.replace("{{DATE}}", date.strftime("%Y-%m-%d"))
        content = content.replace("{{YESTERDAY}}", yesterday.strftime("%Y-%m-%d"))
        content = content.replace("{{WEEK_PLAN}}", week_str)
        content = content.replace("{{TASKS}}", tasks_text)

        # Moment.js 语法
        content = re.sub(r'<%.*?moment\(\)\.format\(\'YYYY-MM-DD \(ddd\)\'\).*?%>', f'{date.strftime("%Y-%m-%d (%a)")}', content)
        content = re.sub(r'<%.*?moment\(\)\.format\(\'YYYY-\[W\]WW\'\).*?%>', week_str, content)

        # 嵌入 Daily Plan
        daily_plan_content = self.get_daily_plan_content()
        if daily_plan_content and "## 📊 进度追踪" in content:
            content = content.replace("## 📊 进度追踪", f"## 📊 进度追踪\n\n{daily_plan_content}")

        return content

    def get_daily_plan_content(self) -> str:
        """获取 Daily Plan 引用"""
        daily_plan_file = self.daily_dir / "Daily Plan.md"
        if not daily_plan_file.exists():
            return ""

        content = daily_plan_file.read_text(encoding='utf-8')
        if "---" in content:
            parts = content.split("---")
            content = parts[2] if len(parts) >= 3 else parts[-1]

        return "![[Daily Plan]]" if content.strip() else ""

    def create_daily_note(self, date: datetime.date) -> str:
        """主函数：创建每日笔记"""
        # 1. 检查周计划
        week_file = self.get_week_file(date)
        if not week_file.exists():
            return f"❌ 错误：未找到周计划文件\n请先创建：{week_file}"

        # 2. 读取任务
        week_tasks = self.parse_week_plan(week_file)
        if not week_tasks:
            return f"⚠️ 警告：周计划 {week_file.name} 为空"

        # 3. 分析昨天
        yesterday_file = self.get_yesterday_file(date)
        yesterday_status = self.analyze_yesterday(yesterday_file) if yesterday_file else {"completed": [], "in_progress": [], "not_completed": []}

        # 4. 生成今日任务
        today_tasks = self.generate_today_tasks(week_tasks, yesterday_status, date)

        # 5. 获取模板
        template = self.get_template()
        if not template:
            return "❌ 错误：未找到模板 /Templates/Daily Note Template.md"

        # 6. 应用模板
        content = self.apply_template(template, date, today_tasks)

        # 7. 保存文件
        daily_file = self.daily_dir / f"{date.strftime('%Y-%m-%d')}.md"
        daily_file.parent.mkdir(parents=True, exist_ok=True)
        daily_file.write_text(content, encoding='utf-8')

        # 8. 返回结果
        result = f"✅ 成功创建每日计划\n📁 文件：{daily_file}\n📊 任务数：{len(today_tasks)} 个\n📅 日期：{date.strftime('%Y-%m-%d')} ({date.strftime('%A')})\n"
        if yesterday_status["not_completed"]:
            result += f"🔴 优先任务：{len(yesterday_status['not_completed'])} 个（昨日未完成）\n"
        if yesterday_status["in_progress"]:
            result += f"🟡 继续任务：{len(yesterday_status['in_progress'])} 个（昨日进行中）\n"
        return result


def main():
    """命令行入口"""
    import sys

    if len(sys.argv) > 1:
        try:
            date = datetime.datetime.strptime(sys.argv[1], '%Y-%m-%d').date()
        except:
            print("❌ 日期格式错误，请使用 YYYY-MM-DD 格式")
            return
    else:
        date = datetime.date.today()

    generator = DailyPlanGenerator()
    print(generator.create_daily_note(date))


if __name__ == "__main__":
    main()