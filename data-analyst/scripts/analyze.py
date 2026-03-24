#!/usr/bin/env python3
"""
data-analyst/scripts/analyze.py

自动读取 CSV / Excel 文件，输出：
- summary.json：数据统计摘要
- 若干 .png 图表文件

用法：
    python analyze.py --file <路径> --output <输出目录>
"""

import argparse
import json
import os
import warnings
import sys

warnings.filterwarnings("ignore")

import pandas as pd
import matplotlib
matplotlib.use("Agg")  # 无显示器环境
import matplotlib.pyplot as plt
import matplotlib.font_manager as fm
import seaborn as sns

# ── 字体配置（兼容无中文字体环境） ──────────────────────────────
def setup_font():
    """尝试使用中文字体，失败则回退到英文。"""
    candidates = ["SimHei", "PingFang SC", "Noto Sans CJK SC", "DejaVu Sans"]
    available = {f.name for f in fm.fontManager.ttflist}
    for font in candidates:
        if font in available:
            plt.rcParams["font.family"] = font
            plt.rcParams["axes.unicode_minus"] = False
            return font
    plt.rcParams["font.family"] = "DejaVu Sans"
    return "DejaVu Sans"

FONT = setup_font()
sns.set_theme(style="whitegrid", palette="muted")


# ── 工具函数 ──────────────────────────────────────────────────────
def load_file(path: str) -> pd.DataFrame:
    ext = os.path.splitext(path)[1].lower()
    if ext == ".csv":
        # 尝试常见编码
        for enc in ["utf-8", "gbk", "latin-1"]:
            try:
                return pd.read_csv(path, encoding=enc)
            except UnicodeDecodeError:
                continue
        raise ValueError(f"无法解析文件编码：{path}")
    elif ext in [".xlsx", ".xls"]:
        return pd.read_excel(path)
    else:
        raise ValueError(f"不支持的文件类型：{ext}，请上传 CSV 或 Excel 文件。")


def detect_datetime_cols(df: pd.DataFrame) -> list[str]:
    """检测可能是时间列的列名。"""
    time_keywords = ["date", "time", "year", "month", "日期", "时间", "年", "月"]
    candidates = []
    for col in df.columns:
        if df[col].dtype == "object":
            if any(kw in col.lower() for kw in time_keywords):
                try:
                    df[col] = pd.to_datetime(df[col])
                    candidates.append(col)
                except Exception:
                    pass
        elif pd.api.types.is_datetime64_any_dtype(df[col]):
            candidates.append(col)
    return candidates


def compute_summary(df: pd.DataFrame, datetime_cols: list[str]) -> dict:
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    missing = {}
    for col in df.columns:
        n = int(df[col].isna().sum())
        missing[col] = {"count": n, "rate": round(n / len(df), 4)}

    stats = {}
    for col in num_cols:
        s = df[col].describe()
        stats[col] = {k: round(float(v), 4) for k, v in s.items()}

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "numeric_cols": num_cols,
        "categorical_cols": cat_cols,
        "datetime_cols": datetime_cols,
        "missing": missing,
        "numeric_stats": stats,
    }


# ── 图表生成函数 ──────────────────────────────────────────────────

def plot_bar(df: pd.DataFrame, col: str, out_dir: str):
    """类别列 → 柱状图（Top 10）。"""
    vc = df[col].value_counts().head(10)
    fig, ax = plt.subplots(figsize=(8, 5))
    vc.plot(kind="bar", ax=ax, color=sns.color_palette("muted", len(vc)))
    ax.set_title(f"{col} — Top 10 分布", fontsize=13)
    ax.set_xlabel(col)
    ax.set_ylabel("频次")
    ax.tick_params(axis="x", rotation=30)
    plt.tight_layout()
    path = os.path.join(out_dir, f"bar_{col}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_line(df: pd.DataFrame, time_col: str, num_cols: list[str], out_dir: str):
    """时间列 + 数值列 → 折线图（最多 5 条线）。"""
    targets = num_cols[:5]
    fig, ax = plt.subplots(figsize=(10, 5))
    tmp = df[[time_col] + targets].dropna().sort_values(time_col)
    for col in targets:
        ax.plot(tmp[time_col], tmp[col], label=col, linewidth=1.5)
    ax.set_title(f"时序趋势（基于 {time_col}）", fontsize=13)
    ax.set_xlabel(time_col)
    ax.set_ylabel("值")
    ax.legend()
    plt.tight_layout()
    path = os.path.join(out_dir, f"line_{time_col}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_scatter(df: pd.DataFrame, col_x: str, col_y: str, out_dir: str):
    """两个数值列 → 散点图（最多抽样 2000 点）。"""
    sample = df[[col_x, col_y]].dropna()
    if len(sample) > 2000:
        sample = sample.sample(2000, random_state=42)
    r = sample[col_x].corr(sample[col_y])
    fig, ax = plt.subplots(figsize=(6, 5))
    ax.scatter(sample[col_x], sample[col_y], alpha=0.5, s=15, color="#4C72B0")
    ax.set_title(f"{col_x} vs {col_y}  (r={r:.2f})", fontsize=12)
    ax.set_xlabel(col_x)
    ax.set_ylabel(col_y)
    plt.tight_layout()
    safe_x = col_x.replace("/", "_").replace(" ", "_")
    safe_y = col_y.replace("/", "_").replace(" ", "_")
    path = os.path.join(out_dir, f"scatter_{safe_x}_{safe_y}.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


def plot_heatmap(df: pd.DataFrame, num_cols: list[str], out_dir: str):
    """相关性热力图。"""
    corr = df[num_cols].corr()
    size = max(6, len(num_cols))
    fig, ax = plt.subplots(figsize=(size, size - 1))
    sns.heatmap(
        corr, annot=True, fmt=".2f", cmap="coolwarm",
        center=0, square=True, ax=ax,
        linewidths=0.5, annot_kws={"size": 9}
    )
    ax.set_title("数值变量相关性矩阵", fontsize=13)
    plt.tight_layout()
    path = os.path.join(out_dir, "heatmap.png")
    fig.savefig(path, dpi=120)
    plt.close(fig)
    return path


# ── 主流程 ────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(description="自动数据分析脚本")
    parser.add_argument("--file", required=True, help="CSV 或 Excel 文件路径")
    parser.add_argument("--output", required=True, help="图表和摘要的输出目录")
    args = parser.parse_args()

    os.makedirs(args.output, exist_ok=True)
    print(f"📂 读取文件：{args.file}")

    # 1. 加载数据
    df = load_file(args.file)
    print(f"✅ 数据加载成功：{len(df)} 行 × {len(df.columns)} 列")

    # 2. 检测时间列
    datetime_cols = detect_datetime_cols(df)
    num_cols = df.select_dtypes(include="number").columns.tolist()
    cat_cols = df.select_dtypes(include=["object", "category"]).columns.tolist()

    # 3. 生成统计摘要
    summary = compute_summary(df, datetime_cols)
    summary_path = os.path.join(args.output, "summary.json")
    with open(summary_path, "w", encoding="utf-8") as f:
        json.dump(summary, f, ensure_ascii=False, indent=2)
    print(f"📊 统计摘要已保存：{summary_path}")

    generated = []

    # 4. 柱状图（类别列，≤20 唯一值）
    for col in cat_cols:
        if col in datetime_cols:
            continue
        if df[col].nunique() <= 20:
            p = plot_bar(df, col, args.output)
            generated.append(p)
            print(f"  🖼  柱状图：{p}")

    # 5. 折线图（时间列 + 数值列）
    if datetime_cols and num_cols:
        p = plot_line(df, datetime_cols[0], num_cols, args.output)
        generated.append(p)
        print(f"  🖼  折线图：{p}")

    # 6. 散点图（前两个数值列）
    if len(num_cols) >= 2:
        p = plot_scatter(df, num_cols[0], num_cols[1], args.output)
        generated.append(p)
        print(f"  🖼  散点图：{p}")

    # 7. 相关性热力图（数值列 ≥ 3）
    if len(num_cols) >= 3:
        p = plot_heatmap(df, num_cols, args.output)
        generated.append(p)
        print(f"  🖼  热力图：{p}")

    print(f"\n✅ 完成！共生成 {len(generated)} 张图表，保存至 {args.output}")


if __name__ == "__main__":
    main()
