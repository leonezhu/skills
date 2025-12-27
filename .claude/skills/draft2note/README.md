# Draft2Note Skill

一个用于将草稿文件转换为格式化 Obsidian 笔记的 Claude Skill。遵循 Zettelkasten 方法和你的知识管理规范。

## 功能特性

### ✅ 核心功能
- **批量处理** - 一次处理多个草稿文件
- **智能分析** - 自动提取主题、别名和关键词
- **附件管理** - 自动重命名和移动附件
- **格式化输出** - 使用 Base template 生成标准笔记
- **安全操作** - 原子操作，错误恢复

### 📁 目录结构
```
notes/
├── Drafts/              # 输入：原始草稿文件
├── References/          # 输出：格式化笔记
└── Attachments/         # 附件：重命名后的文件
```

## 快速开始

### 基本用法

**处理所有草稿：**
```
Process all drafts into notes
Convert my drafts to notes
```

**处理单个文件：**
```
Convert draft 'project-ideas.md' to a note
Process 'meeting-notes.md'
```

**批量处理：**
```
Convert these drafts: file1.md, file2.md
Process all files in Drafts/
```

### 高级用法

**保留原始文件：**
```bash
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --keep-original
```

**预览模式（不实际修改）：**
```bash
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --dry-run
```

**处理特定文件：**
```bash
python3 .claude/skills/draft2note/scripts/process_drafts.py --file "my-draft.md" --vault .
```

## 处理流程

### 1. 输入检测
- 扫描 `Drafts/` 目录
- 支持 `.md` 和 `.txt` 文件
- 可指定单个或多个文件

### 2. 内容分析
```markdown
# 标题提取优先级
1. 第一个 # 标题
2. 文件名（转换为标题）
3. 自动生成

# 主题提取
- 显式标记：## 主题: [[Topic1]], [[Topic2]]
- 关键词分析：自动识别主要内容
- 用户指定：通过对话提供

# 别名提取
- 别名: Alternative Name
- aliases: Alt1, Alt2
```

### 3. 附件处理
**检测模式：**
```markdown
![描述](路径/文件.png)
[文件名](附件.pdf)
```

**重命名规则：**
- 格式：`{笔记标题}-{原文件名}.{扩展名}`
- 示例：`AI-项目想法-architecture.png`
- 移动到：`Attachments/` 目录
- 路径更新：在笔记中自动更新

### 4. 输出格式
```yaml
---
created: 2025-12-27
created_at: '[[2025-12-27]]'
topics:
  - "[[AI]]"
  - "[[Projects]]"
aliases:
  - AI Ideas
---

# 笔记内容...

![[Backlinks.base]]
```

## 示例

### 输入：草稿文件
```markdown
# AI 项目想法

## 主题: [[AI]], [[Projects]]

最近在思考的一些方向：
1. 智能笔记整理
2. 语音转文字

## 相关资源
- ![架构图](architecture.png)

别名: AI Ideas, 人工智能项目
```

### 输出：格式化笔记
```markdown
---
created: 2025-12-27
created_at: '[[2025-12-27]]'
topics:
  - "[[AI]]"
  - "[[Projects]]"
aliases:
  - AI Ideas
  - 人工智能项目
---

# AI 项目想法

## 主题: [[AI]], [[Projects]]

最近在思考的一些方向：
1. 智能笔记整理
2. 语音转文字

## 相关资源
- ![架构图](Attachments/AI-项目想法-architecture.png)

别名: AI Ideas, 人工智能项目

![[Backlinks.base]]
```

### 附件移动
- `Drafts/architecture.png` → `Attachments/AI-项目想法-architecture.png`

## 命令行选项

| 选项 | 说明 | 示例 |
|------|------|------|
| `--all` | 处理所有草稿 | `--all` |
| `--file <path>` | 处理指定文件 | `--file "draft.md"` |
| `--dry-run` | 预览不修改 | `--dry-run` |
| `--keep-original` | 保留原始文件 | `--keep-original` |
| `--vault <path>` | 指定 vault 路径 | `--vault .` |

## 错误处理

### 常见问题

**❌ Drafts 目录不存在**
- 自动创建目录
- 提示添加文件

**❌ 模板文件缺失**
- 使用基本格式
- 警告但继续处理

**❌ 附件文件丢失**
- 跳过该附件
- 记录警告信息
- 继续处理其他文件

**❌ 文件名冲突**
- 自动添加编号
- 示例：`Title-1.md`, `Title-2.md`

### 安全特性
- ✅ 原子文件操作
- ✅ 错误时保留原始文件
- ✅ 详细错误报告
- ✅ 支持回滚操作

## 最佳实践

### 草稿准备
1. **组织内容** - 相关内容放一起
2. **清晰命名** - 使用描述性文件名
3. **标记主题** - 使用 `## 主题:` 标记
4. **检查附件** - 确保文件路径正确

### 处理后检查
1. **验证主题** - 确认提取准确
2. **测试链接** - 点击内部链接
3. **检查附件** - 确认文件可访问
4. **添加连接** - 建立更多双向链接

### 维护建议
- 定期清理 Drafts 目录
- 监控 Attachments 大小
- 更新主题提取规则
- 备份重要笔记

## 技术细节

### 脚本文件
- `process_drafts.py` - 主处理脚本
- `test_drafts.py` - 测试脚本

### 参考文档
- `references/processing_patterns.md` - 处理模式详细说明

### 依赖
- Python 3.6+
- 标准库：re, sys, shutil, argparse, pathlib, datetime

## 扩展功能

### 自定义模板
当前使用基本格式，可扩展为：
- 读取 `Templates/Base template.md`
- 插入动态内容
- 支持复杂模板变量

### 主题分析增强
- 连接现有笔记主题
- 使用 Smart Connections
- 基于内容相似度分组

### 批量优化
- 并行处理大量文件
- 进度条显示
- 批量报告生成

## 故障排除

### 问题：没有生成笔记
**检查：**
1. Drafts 目录是否存在
2. 文件是否有 `.md` 或 `.txt` 扩展名
3. 文件权限是否正确

### 问题：附件未移动
**检查：**
1. 附件路径是否正确
2. 附件文件是否存在
3. Attachments 目录权限

### 问题：主题提取错误
**解决：**
1. 使用 `## 主题:` 明确标记
2. 或手动指定主题
3. 检查关键词分析逻辑

## 获取帮助

### 调试模式
```bash
# 查看详细处理过程
python3 .claude/skills/draft2note/scripts/process_drafts.py --all --dry-run
```

### 查看日志
- 检查命令行输出
- 查看生成的笔记内容
- 验证附件位置

### 报告问题
- 提供原始草稿文件
- 说明预期结果
- 分享错误信息

---

*此 skill 遵循你的 Obsidian 笔记系统规范，支持 Zettelkasten 方法和双向链接最佳实践。*