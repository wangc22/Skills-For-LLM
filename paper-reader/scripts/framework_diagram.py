#!/usr/bin/env python3
"""
paper-reader/scripts/framework_diagram.py

生成论文框架图：问题 → 方法 → 贡献 的可视化流程图
输出为 PNG 文件，嵌入 Word 文档使用

用法：
    python framework_diagram.py \
        --title "LoRA: Low-Rank Adaptation of LLMs" \
        --problem "全量微调大模型成本过高" \
        --method "冻结原始权重，注入可训练低秩矩阵 ΔW=BA" \
        --contribution "参数减少10000倍|零推理延迟|持平全量微调效果" \
        --output framework.png
"""

import argparse
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.patches as mpatches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import textwrap

# ── 颜色方案 ──────────────────────────────────────────────────────
COLORS = {
    "problem":      "#E8F4FD",   # 浅蓝 - 问题框
    "problem_bd":   "#2196F3",   # 蓝色边框
    "method":       "#FFF8E1",   # 浅黄 - 方法框
    "method_bd":    "#FF9800",   # 橙色边框
    "contrib":      "#F1F8E9",   # 浅绿 - 贡献框
    "contrib_bd":   "#4CAF50",   # 绿色边框
    "arrow":        "#546E7A",   # 箭头颜色
    "title_bg":     "#37474F",   # 标题背景
    "title_fg":     "#FFFFFF",   # 标题文字
    "label":        "#546E7A",   # 标签颜色
}


def wrap_text(text: str, width: int = 28) -> str:
    """自动换行。"""
    return "\n".join(textwrap.wrap(text, width=width))


def draw_rounded_box(ax, x, y, w, h, text, label,
                     facecolor, edgecolor, fontsize=10):
    """绘制圆角矩形 + 标签 + 文字。"""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02",
        facecolor=facecolor, edgecolor=edgecolor, linewidth=2.5,
        transform=ax.transData, zorder=3
    )
    ax.add_patch(box)

    # 标签（小字，上方）
    ax.text(x, y + h / 2 + 0.04, label,
            ha="center", va="bottom",
            fontsize=8, color=edgecolor, fontweight="bold",
            transform=ax.transData, zorder=4)

    # 正文
    ax.text(x, y, wrap_text(text),
            ha="center", va="center",
            fontsize=fontsize, color="#212121",
            transform=ax.transData, zorder=4,
            linespacing=1.4)


def draw_arrow(ax, x1, x2, y):
    """绘制水平箭头。"""
    ax.annotate(
        "", xy=(x2 - 0.02, y), xytext=(x1 + 0.02, y),
        arrowprops=dict(
            arrowstyle="-|>",
            color=COLORS["arrow"],
            lw=2,
            mutation_scale=18,
        ),
        zorder=5
    )


def draw_contribution_list(ax, x, y, w, h, items, edgecolor):
    """贡献框：多条目版本。"""
    box = FancyBboxPatch(
        (x - w / 2, y - h / 2), w, h,
        boxstyle="round,pad=0.02",
        facecolor=COLORS["contrib"], edgecolor=edgecolor, linewidth=2.5,
        transform=ax.transData, zorder=3
    )
    ax.add_patch(box)

    ax.text(x, y + h / 2 + 0.04, "主要贡献",
            ha="center", va="bottom",
            fontsize=8, color=edgecolor, fontweight="bold",
            transform=ax.transData, zorder=4)

    # 分行显示每条贡献
    step = h / (len(items) + 1)
    for i, item in enumerate(items):
        ypos = y + h / 2 - step * (i + 1)
        ax.text(x - w / 2 + 0.06, ypos,
                f"- {wrap_text(item, 22)}",
                ha="left", va="center",
                fontsize=9, color="#212121",
                transform=ax.transData, zorder=4,
                linespacing=1.3)


def generate_diagram(title: str, problem: str, method: str,
                     contributions: list[str], output: str):
    fig_w, fig_h = 13, 6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h))
    ax.set_xlim(0, 1)
    ax.set_ylim(0, 1)
    ax.axis("off")

    # ── 标题栏 ────────────────────────────────────────────────────
    title_box = FancyBboxPatch(
        (0.01, 0.82), 0.98, 0.14,
        boxstyle="round,pad=0.01",
        facecolor=COLORS["title_bg"], edgecolor="none",
        transform=ax.transData, zorder=2
    )
    ax.add_patch(title_box)
    ax.text(0.5, 0.89, wrap_text(title, 80),
            ha="center", va="center",
            fontsize=11, color=COLORS["title_fg"], fontweight="bold",
            transform=ax.transData, zorder=3, linespacing=1.3)

    # ── 三列布局：问题 → 方法 → 贡献 ─────────────────────────────
    box_y   = 0.42
    box_h   = 0.55
    box_w   = 0.27

    x_prob  = 0.155
    x_meth  = 0.500
    x_cont  = 0.845

    draw_rounded_box(ax, x_prob, box_y, box_w, box_h,
                     problem, "研究问题",
                     COLORS["problem"], COLORS["problem_bd"], fontsize=10)

    draw_rounded_box(ax, x_meth, box_y, box_w, box_h,
                     method, "核心方法",
                     COLORS["method"], COLORS["method_bd"], fontsize=10)

    draw_contribution_list(ax, x_cont, box_y, box_w, box_h,
                           contributions, COLORS["contrib_bd"])

    # ── 箭头 ──────────────────────────────────────────────────────
    draw_arrow(ax, x_prob + box_w / 2, x_meth - box_w / 2, box_y)
    draw_arrow(ax, x_meth + box_w / 2, x_cont - box_w / 2, box_y)

    # ── 底部说明 ──────────────────────────────────────────────────
    ax.text(0.5, 0.03,
            "论文框架图  ·  Paper Framework Diagram",
            ha="center", va="bottom",
            fontsize=7.5, color="#90A4AE",
            transform=ax.transData)

    plt.tight_layout(pad=0.3)
    fig.savefig(output, dpi=150, bbox_inches="tight",
                facecolor="white", edgecolor="none")
    plt.close(fig)
    print(f"✅ 框架图已生成：{output}")


def main():
    parser = argparse.ArgumentParser(description="生成论文框架图")
    parser.add_argument("--title",        required=True, help="论文标题")
    parser.add_argument("--problem",      required=True, help="研究问题（一句话）")
    parser.add_argument("--method",       required=True, help="核心方法（一句话）")
    parser.add_argument("--contribution", required=True,
                        help="主要贡献，用 | 分隔多条，如 '贡献1|贡献2|贡献3'")
    parser.add_argument("--output",       required=True, help="输出 PNG 路径")
    args = parser.parse_args()

    contributions = [c.strip() for c in args.contribution.split("|") if c.strip()]
    generate_diagram(args.title, args.problem, args.method, contributions, args.output)


if __name__ == "__main__":
    main()
