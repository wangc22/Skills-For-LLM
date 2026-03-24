---
name: paper-reader
description: 论文深度解读 Skill，专为计算机科学 / AI 领域设计。当用户上传或提到一篇论文，并希望理解、分析、整理其内容时，必须使用此 Skill。触发词包括：解读论文、帮我看这篇论文、分析这篇 paper、读一下这篇文章、论文笔记、summarize this paper、explain this paper。即使用户只说"帮我看看这个 PDF"而附件是学术论文，也应触发此 Skill。输出为结构化 Markdown 以及 Word 文档（.docx），Word 文档中包含论文框架图，涵盖数学背景、研究问题、方法论、实验结果、优缺点五大模块。
---

# Paper Reader — 论文深度解读

## 定位

面向 CS / AI 研究者，将一篇学术论文整理成：
1. **对话中的结构化 Markdown**（快速浏览）
2. **可下载的 Word 文档 (.docx)**（包含论文框架图，适合存档和汇报）

---

## 工作流程（按顺序执行）

### Step 1：解读论文内容
按照 `references/output-structure.md` 定义的六个模块，在对话中输出完整的 Markdown 解读。

### Step 2：生成论文框架图
运行脚本生成论文结构可视化图：

```bash
pip install matplotlib --break-system-packages -q
python /home/claude/paper-reader/scripts/framework_diagram.py \
  --title "论文标题" \
  --problem "研究问题一句话" \
  --method "核心方法一句话" \
  --contribution "主要贡献1|主要贡献2|主要贡献3" \
  --output /home/claude/framework.png
```

### Step 3：生成 Word 文档
安装依赖并运行脚本：

```bash
npm install -g docx 2>/dev/null
node /home/claude/paper-reader/scripts/generate_docx.js \
  --content "/home/claude/paper_content.json" \
  --diagram "/home/claude/framework.png" \
  --output "/home/claude/paper_report.docx"
```

### Step 4：输出文件
将 Word 文档复制到 `/mnt/user-data/outputs/`，用 `present_files` 呈现给用户。

---

## 行为规范

1. **忠实原文**：不捏造实验数据或结论，不确定时注明「论文未明确说明」。
2. **公式必须解释**：出现数学符号时，必须在公式下方用中文白话解释。
3. **中英文术语并列**：第一次出现专业术语时，格式为 `中文名（English Name）`。
4. **长度控制**：Markdown 解读总输出建议 800-2000 字；Word 文档结构与 Markdown 一致。
5. **语言**：默认中文；若用户要求英文则全程英文。
6. **框架图提取原则**：框架图只呈现论文的骨架（问题→方法→贡献），不堆砌细节。
