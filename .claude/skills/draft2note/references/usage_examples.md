# Draft2Note 使用示例

## 基础场景

### 场景 1：处理单个草稿

**用户请求：**
```
"Convert draft 'project-ideas.md' to a note"
```

**处理过程：**
1. 读取 `Drafts/project-ideas.md`
2. 分析内容提取主题
3. 生成 `References/Project-Ideas.md`
4. 移动附件（如有）
5. 删除原始草稿

**结果：**
```
✅ Project-Ideas.md created
   Topics: [[Projects]], [[Ideas]]
   Attachments: 2
```

---

### 场景 2：批量处理所有草稿

**用户请求：**
```
"Process all my drafts into notes"
```

**处理过程：**
1. 扫描 `Drafts/` 所有 `.md` 和 `.txt` 文件
2. 逐个处理每个文件
3. 生成报告

**结果：**
```
📊 Processing Complete: 5/5 successful

✅ Meeting Notes
   Topics: [[Work]], [[Meetings]]
   → References/Meeting-Notes.md

✅ Workout Plan
   Topics: [[Health]], [[Exercise]]
   Attachments: 1
   → References/Workout-Plan.md

✅ Project Ideas
   Topics: [[Projects]]
   → References/Project-Ideas.md
```

---

### 场景 3：指定主题处理

**用户请求：**
```
"Convert 'brainstorm.md' with topics [[AI]] and [[Research]]"
```

**处理过程：**
1. 读取草稿文件
2. 使用指定主题
3. 补充自动提取的主题
4. 创建格式化笔记

**结果：**
```yaml
---
created: 2025-12-27
created_at: '[[2025-12-27]]'
topics:
  - "[[AI]]"
  - "[[Research]]"
  - "[[Innovation]]"  # 自动提取
---
```

---

## 高级场景

### 场景 4：带附件的笔记

**输入草稿：**
```markdown
# 用户调研报告

## 主题: [[Research]], [[User]]

### 核心发现
1. 用户需要更简单的界面
2. 性能是关键需求

### 数据图表
![用户满意度](survey-results.png)
![使用趋势](trend-chart.png)

别名: 调研报告, 用户研究
```

**处理结果：**

**笔记文件：**
```markdown
---
created: 2025-12-27
created_at: '[[2025-12-27]]'
topics:
  - "[[Research]]"
  - "[[User]]"
aliases:
  - 调研报告
  - 用户研究
---

# 用户调研报告

## 主题: [[Research]], [[User]]

### 核心发现
1. 用户需要更简单的界面
2. 性能是关键需求

### 数据图表
![用户满意度](Attachments/用户调研报告-survey-results.png)
![使用趋势](Attachments/用户调研报告-trend-chart.png)

别名: 调研报告, 用户研究

![[Backlinks.base]]
```

**移动的附件：**
- `Drafts/survey-results.png` → `Attachments/用户调研报告-survey-results.png`
- `Drafts/trend-chart.png` → `Attachments/用户调研报告-trend-chart.png`

---

### 场景 5：会议记录处理

**输入草稿：**
```markdown
## 2025-12-27 产品评审会议

### Attendees
- Alice (PM)
- Bob (Dev)
- Carol (Design)

### Decisions
1. ✅ Approve Q1 roadmap
2. ✅ Budget increase for design tools
3. ⏸️ Delay feature X to Q2

### Action Items
- [ ] Alice: Update roadmap doc
- [ ] Bob: Prototype new API
- [ ] Carol: Create mockups

## 分类: [[Work]], [[Meetings]], [[2025-Q4]]
```

**处理结果：**
- 自动提取会议主题
- 生成任务列表
- 正确分类
- 便于后续追踪

---

### 场景 6：知识碎片整理

**输入草稿：**
```markdown
# 英语学习笔记

## 主题: [[English]], [[Learning]]

### 词汇
- **Proactive** - 主动的
- **Leverage** - 利用

### 语法点
- Get + 动词分词 = 陷入某种状态
- As...As 结构

### 资源
- ![语法图](grammar-chart.jpg)
- [练习文档](worksheet.pdf)

别名: 英语笔记, English Notes
```

**处理结果：**
- 生成结构化笔记
- 附件正确归档
- 主题关联建立
- 便于复习回顾

---

## 命令行使用示例

### 基础命令

```bash
# 处理所有草稿
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --vault .

# 预览模式（不实际修改）
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --dry-run --vault .

# 处理单个文件
python3 .claude/skills/draft2note/scripts/process_drafts.py --file "my-draft.md" --vault .

# 保留原始文件
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --keep-original --vault .
```

### 组合使用

```bash
# 预览 + 保留原始
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --dry-run --keep-original --vault .

# 处理特定文件 + 保留
python3 .claude/skills/draft2note/scripts/process_drafts.py --file "meeting.md" --keep-original --vault .
```

---

## 与 Claude 对话示例

### 示例 1：简单请求
**User:** "Convert my drafts to notes"

**Claude:** "I'll process all files in your Drafts directory. Let me show you what will be processed..."

### 示例 2：指定文件
**User:** "Process 'project-ideas.md' and 'meeting-notes.md'"

**Claude:** "I'll convert these two files. Here's the plan..."

### 示例 3：带参数
**User:** "Convert all drafts but keep the originals"

**Claude:** "I'll process all drafts with --keep-original flag..."

### 示例 4：问题解决
**User:** "The draft2note skill isn't finding my files"

**Claude:** "Let me check:
1. Drafts directory exists: ✅
2. File permissions: ✅
3. File extensions: ...

Try running with --dry-run to see what's detected."

---

## 错误处理示例

### 场景：附件丢失

**输入：**
```markdown
# 报告

![图表](missing-image.png)
```

**处理结果：**
```
⚠️  Warning: Attachment not found: missing-image.png
✅  Note created: References/报告.md
💡  Please check attachment path
```

**笔记内容：**
```markdown
# 报告

![图表](missing-image.png)  # 路径未更新
```

---

### 场景：文件名冲突

**已存在：** `References/Project-Ideas.md`

**新文件：** `Drafts/project-ideas.md`

**处理结果：**
```
✅ Created: References/Project-Ideas-1.md
```

---

### 场景：无效内容

**输入：** 空文件或无法解析

**处理结果：**
```
❌ Error: project-ideas.md - Content parse error
💡 Suggestion: Check file encoding and format
```

---

## 性能优化

### 大量文件处理

**建议：**
1. 分批处理（10-20个文件/次）
2. 使用 --dry-run 先预览
3. 检查结果后再批量处理

**示例：**
```bash
# 先预览
python3 process_drafts.py --all --dry-run

# 确认无误后处理
python3 process_drafts.py --all
```

### 大文件处理

**建议：**
- 分割大文件为多个小文件
- 检查附件大小
- 确保有足够磁盘空间

---

## 与其他工具配合

### 与 Smart Connections
```markdown
# 处理后的笔记
---
topics:
  - "[[AI]]"
  - "[[Projects]]"
---

# 内容...

![[Backlinks.base]]
```

Smart Connections 可以：
- 发现相关笔记
- 建议新链接
- 优化知识网络

### 与 Dataview
```markdown
---
created: 2025-12-27
topics:
  - "[[Health]]"
  - "[[Exercise]]"
---

# 内容...
```

Dataview 查询：
```dataview
TABLE created, topics
FROM "References"
WHERE contains(topics, "[[Health]]")
```

### 与 Tasks
```markdown
# 会议记录

### Action Items
- [ ] Alice: Update roadmap
- [ ] Bob: Prototype API
```

Tasks 插件可追踪这些待办。

---

## 最佳实践总结

### ✅ 推荐做法
1. **预览模式** - 先用 --dry-run 测试
2. **备份** - 重要文件先备份
3. **检查** - 处理后验证结果
4. **清理** - 定期清理 Drafts

### ❌ 避免做法
1. 不要处理重要文件的唯一副本
2. 不要在磁盘空间不足时批量处理
3. 不要忽略错误信息
4. 不要忘记检查附件完整性

### 🔄 工作流程
```
1. 收集想法 → Drafts/
2. 组织内容 → 添加主题标记
3. 预览处理 → --dry-run
4. 执行转换 → 处理所有
5. 检查结果 → 验证笔记
6. 建立连接 → 添加链接
7. 清理草稿 → 删除已处理
```

---

## 扩展使用

### 自动化脚本

创建 `process-all.sh`：
```bash
#!/bin/bash
cd /path/to/vault
python3 .claude/skills/draft2note/scripts/process_drafts.py --all
echo "Processing complete!"
```

### 定时任务

使用 cron 定期处理：
```bash
# 每天晚上处理草稿
0 22 * * * cd /path/to/vault && python3 .claude/skills/draft2note/scripts/process_drafts.py --all
```

### 与其他技能配合

**组合使用：**
1. draft2note - 转换草稿
2. theme-factory - 美化笔记
3. word-lookup - 学习词汇

---

*这些示例展示了 draft2note skill 在各种场景下的实际应用。根据你的具体需求调整使用方式。*