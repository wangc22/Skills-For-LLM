# Claude Skills Assignment

本仓库包含两个自定义 Claude Skill：paper-reader used to analyze the CS/AI background & data-analyst used to analyze the data and present graph

## Skill 列表

### 1. `paper-reader` — 论文深度解读
- **功能**：将 CS/AI 学术论文整理为结构化 Markdown 笔记，并生成可下载的 Word 文档（含论文框架图）
- **输出模块**：数学背景、研究问题、方法论、实验结果、优缺点
- **框架图**：自动生成「研究问题 → 核心方法 → 主要贡献」可视化流程图，嵌入 Word 文档
- **组件**：SKILL.md + references（输出结构规范）+ scripts（框架图生成 + Word 文档生成）

### 2. `data-analyst` — 数据分析与可视化
- **功能**：上传 CSV/Excel 自动生成图表 + Markdown 分析报告
- **图表类型**：柱状图、折线图、散点图、相关性热力图
- **组件**：SKILL.md + references（图表选择规范 + 报告写作模板）+ scripts（数据处理与出图）

---

## 文件结构

```
.
├── README.md
├── paper-reader/
│   ├── SKILL.md                        # 主指令与工作流
│   ├── references/
│   │   └── output-structure.md         # 六模块输出结构规范
│   └── scripts/
│       ├── framework_diagram.py        # 生成论文框架图 (PNG)
│       └── generate_docx.js            # 生成 Word 文档 (.docx)
└── data-analyst/
    ├── SKILL.md                        # 主指令与工作流
    ├── references/
    │   ├── chart-guide.md              # 图表选择规范
    │   └── interpretation-template.md  # 报告写作模板
    └── scripts/
        └── analyze.py                  # 数据处理与图表生成
```

---

## 安装方式

1. 下载对应 `.skill` 文件（见 Releases）
2. 打开 [claude.ai](https://claude.ai) → Settings → Skills → Install Skill
3. 上传 `.skill` 文件即可使用

## 依赖环境

**paper-reader**
- Python: `matplotlib`
- Node.js: `npm install -g docx`

**data-analyst**
- Python: `pandas matplotlib seaborn openpyxl`
