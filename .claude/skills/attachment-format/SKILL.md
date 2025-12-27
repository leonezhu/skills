---
name: attachment-format
description: 整理附件命名，根据引用上下文重命名，清理未使用的附件
---

# Attachment Format Skill

## 功能
自动整理 `/Attachments/` 目录中的文件：
1. 识别不规范的命名（包含英文连字符、随机字符等）
2. 根据引用上下文智能重命名
3. 检测未被引用的附件并提示删除

## 使用方法

### 基本命令
```
"整理附件"
"清理附件目录"
"重命名附件"
"检查未使用的附件"
```

## 工作流程

### 步骤 1: 扫描附件目录
```bash
ls Attachments/
```

### 步骤 2: 识别不规范命名
**不规范的命名示例：**
- `8020.png` - 过于简单，无上下文
- `Pasted image 20251208212204.png` - 截图工具默认命名
- `Claude_Skills_模型接受程度及中国模型适配研究.md` - 过长，可简化
- `外链.png` - 描述模糊
- `训练计划.png` - 描述模糊

**规范的命名示例：**
- `8020-销售法则.png` - 包含主题和用途
- `Sublime-空行清理示例.png` - 具体功能
- `大模型江湖-架构图.png` - 来源+内容
- `运动计划-深蹲姿势.png` - 主题+内容

### 步骤 3: 查找引用位置
对于每个不规范的附件，搜索所有笔记：
```python
# 搜索引用
引用位置 = grep("![[文件名]]", "References/*.md")
引用位置 += grep("![[文件名]]", "Categories/*.md")
引用位置 += grep("![[文件名]]", "Daily/*.md")
```

### 步骤 4: 分析上下文并生成新名称

#### 规则 1: 从引用所在笔记提取主题
```python
# 示例：8020.png 在 "8020 Sales and Marketing.md" 中被引用
# 新名称：8020-销售法则.png

# 示例：Pasted image 20251208212204.png 在 "Sublime 怎么清除空行.md" 中被引用
# 新名称：Sublime-空行清理示例.png
```

#### 规则 2: 从周围文本提取描述
```python
# 如果附件前后有文字描述，提取关键词
# 例如：
# "这是深蹲的正确姿势：![[训练计划.png]]"
# → 运动计划-深蹲姿势.png
```

#### 规则 3: 多个引用的处理
```python
# 如果同一附件在多个地方被引用，确保新名称通用
# 例如：外链.png 在 "External Link & backlink.md" 中
# → 外链-链接示例.png
```

### 步骤 5: 执行重命名

**操作流程：**
1. 生成新文件名
2. 检查是否冲突（新文件名是否已存在）
3. 重命名文件：`mv Attachments/旧文件名 Attachments/新文件名`
4. 更新所有引用：替换 `![[旧文件名]]` 为 `![[新文件名]]`

### 步骤 6: 检测未使用附件

**未使用附件判断：**
```python
所有附件 = os.listdir("Attachments/")
所有引用 = grep_all_notes("![[")  # 提取所有引用的文件名

未使用 = [f for f in 所有附件 if f not in 所有引用]

if 未使用:
    print("发现未使用的附件：")
    for f in 未使用:
        print(f"  - {f}")
    print("\n是否删除？(y/n)")
```

## 示例场景

### 场景 1: 整理截图文件
```
输入：
  Attachments/Pasted image 20251208212204.png
  被引用于：References/Sublime 怎么清除空行.md

处理：
  1. 读取笔记内容
  2. 发现这是 Sublime Text 的空行清理示例
  3. 生成新名：Sublime-空行清理示例.png
  4. 重命名并更新引用
```

### 场景 2: 检测未使用文件
```
输入：
  Attachments/8020.png
  Attachments/未使用的图片.png

处理：
  1. 扫描所有笔记
  2. 发现 8020.png 被引用
  3. 发现 未使用的图片.png 未被引用
  4. 提示：是否删除 未使用的图片.png？
```

### 场景 3: 多引用处理
```
输入：
  Attachments/训练计划.png
  被引用于：References/运动计划.md (多次)

处理：
  1. 分析上下文：深蹲、卧推、硬拉等
  2. 如果是通用训练图 → 运动计划-训练姿势.png
  3. 如果是特定动作 → 运动计划-深蹲姿势.png
```

## 命名规范

### 推荐格式
```
{主题}-{描述}.{扩展名}
```

**示例：**
- `8020-销售法则.png`
- `Sublime-空行清理.png`
- `大模型江湖-架构图.png`
- `运动计划-深蹲姿势.png`

### 命名规则
1. **使用中文** - 便于搜索和识别
2. **短横线连接** - `{主题}-{描述}`
3. **描述具体** - 避免模糊词汇（如"截图"、"图片"）
4. **保留扩展名** - `.png`, `.md`, `.pdf` 等
5. **避免特殊字符** - 除了 `-` 和 `.`

## 最佳实践

### ✅ 推荐
1. **先分析后执行** - 预览重命名计划
2. **保留原文件** - 重命名前备份
3. **批量处理** - 一次处理多个文件
4. **验证引用** - 确保所有引用都已更新

### ❌ 避免
1. 直接删除文件（先检查引用）
2. 使用过于简单的名称（如 `1.png`）
3. 包含空格或特殊字符
4. 长文件名（超过 50 字符）

## 实现建议

### Python 脚本结构
```python
class AttachmentFormatter:
    def scan_attachments(self):
        """扫描附件目录"""

    def find_references(self, filename):
        """查找文件引用位置"""

    def analyze_context(self, filepath, references):
        """分析上下文生成新名称"""

    def rename_file(self, old, new):
        """重命名文件并更新引用"""

    def find_unused(self):
        """查找未使用附件"""
```

### 调用方式
```bash
# 通过 skill 调用
Bash("python .claude/skills/attachment-format/scripts/formatter.py")
```

---

**注意：** 通过 `Bash("openskills read attachment-format")` 调用