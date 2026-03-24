---
name: data-analyst
description: 数据分析 Skill。当用户上传 CSV 或 Excel 文件，并希望分析数据、出图表、生成解读报告时，必须使用此 Skill。触发词包括：分析这份数据、帮我看看这个 CSV、画个图、数据可视化、出报告、数据趋势、相关性分析。即使用户只说"帮我看看这个文件"而附件是表格数据，也应触发此 Skill。会自动运行 Python 脚本生成图表，并输出结构化 Markdown 分析报告。
---

# Data Analyst — 数据分析与可视化

## 定位

接收用户上传的 CSV / Excel 文件，自动完成：数据概览 → 图表生成 → Markdown 解读报告。

---

## 工作流程（按顺序执行）

### Step 1：读取数据文件
- 用户上传的文件位于 `/mnt/user-data/uploads/`
- 将文件复制到 `/home/claude/` 后再操作，不要直接在 uploads 目录操作

### Step 2：运行分析脚本
执行 `scripts/analyze.py`，传入文件路径：

```bash
pip install pandas matplotlib seaborn openpyxl --break-system-packages -q
python /home/claude/data-analyst/scripts/analyze.py --file <文件路径> --output /home/claude/output/
```

脚本会输出：
- `summary.json`：数据统计摘要（行数、列数、各列类型、基础统计量、缺失值）
- 若干 `.png` 图表文件

### Step 3：读取图表选择规范
阅读 `references/chart-guide.md`，根据数据特征确认脚本选择的图表是否合理，必要时补充说明。

### Step 4：撰写分析报告
阅读 `references/interpretation-template.md`，按模板结构用中文撰写 Markdown 报告，将图表用 `![](路径)` 嵌入对应章节。

### Step 5：输出文件
将报告保存为 `/mnt/user-data/outputs/report.md`，图表复制到 `/mnt/user-data/outputs/`，用 `present_files` 工具呈现给用户。

---

## 行为规范

- **不捏造数据**：所有数字必须来自 `summary.json`，不得凭空估计。
- **图表与文字对应**：每张图表下方必须有 2-3 句解读，不能只贴图不说话。
- **处理缺失值**：若某列缺失率 > 30%，在报告中标注并建议用户核查。
- **列名用原始名称**：报告中出现列名时保留原始英文/中文，不要自行翻译。
- **语言**：默认中文；用户若用英文提问则切换为英文。
