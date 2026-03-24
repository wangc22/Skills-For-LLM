#!/usr/bin/env node
/**
 * paper-reader/scripts/generate_docx.js
 *
 * 读取论文解读内容 JSON + 框架图 PNG，生成格式化 Word 文档
 *
 * 用法：
 *   node generate_docx.js \
 *     --content paper_content.json \
 *     --diagram framework.png \
 *     --output paper_report.docx
 */

const {
  Document, Packer, Paragraph, TextRun, ImageRun,
  HeadingLevel, AlignmentType, LevelFormat,
  BorderStyle, WidthType, Table, TableRow, TableCell,
  ShadingType, PageBreak
} = require("docx");
const fs   = require("fs");
const path = require("path");

// ── CLI 参数解析 ──────────────────────────────────────────────────
function parseArgs() {
  const args = {};
  process.argv.slice(2).forEach((val, i, arr) => {
    if (val.startsWith("--")) args[val.slice(2)] = arr[i + 1];
  });
  return args;
}

// ── 样式定义 ──────────────────────────────────────────────────────
const STYLES = {
  default: {
    document: { run: { font: "Arial", size: 24 } }   // 12pt
  },
  paragraphStyles: [
    {
      id: "Heading1", name: "Heading 1",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 36, bold: true, font: "Arial", color: "FFFFFF" },
      paragraph: {
        spacing: { before: 240, after: 120 },
        outlineLevel: 0,
        shading: { fill: "37474F", type: ShadingType.CLEAR }
      }
    },
    {
      id: "Heading2", name: "Heading 2",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 28, bold: true, font: "Arial", color: "1565C0" },
      paragraph: { spacing: { before: 200, after: 100 }, outlineLevel: 1 }
    },
    {
      id: "Heading3", name: "Heading 3",
      basedOn: "Normal", next: "Normal", quickFormat: true,
      run: { size: 24, bold: true, font: "Arial", color: "37474F" },
      paragraph: { spacing: { before: 160, after: 80 }, outlineLevel: 2 }
    },
  ]
};

// ── 工具函数 ──────────────────────────────────────────────────────
function para(text, opts = {}) {
  return new Paragraph({
    children: [new TextRun({ text, font: "Arial", size: 24, ...opts })],
    spacing: { after: 120 }
  });
}

function heading(text, level) {
  return new Paragraph({
    heading: level,
    children: [new TextRun({ text, font: "Arial" })]
  });
}

function divider() {
  return new Paragraph({
    border: { bottom: { style: BorderStyle.SINGLE, size: 6, color: "BDBDBD", space: 1 } },
    spacing: { after: 160 }
  });
}

function bulletItem(text) {
  return new Paragraph({
    numbering: { reference: "bullets", level: 0 },
    children: [new TextRun({ text, font: "Arial", size: 24 })],
    spacing: { after: 80 }
  });
}

function buildTableRow(cells, isHeader = false) {
  const border = { style: BorderStyle.SINGLE, size: 1, color: "CCCCCC" };
  const borders = { top: border, bottom: border, left: border, right: border };
  const colW = 4680;
  return new TableRow({
    children: cells.map(text =>
      new TableCell({
        borders,
        width: { size: colW, type: WidthType.DXA },
        shading: {
          fill: isHeader ? "37474F" : "F5F5F5",
          type: ShadingType.CLEAR
        },
        margins: { top: 80, bottom: 80, left: 120, right: 120 },
        children: [new Paragraph({
          children: [new TextRun({
            text, font: "Arial", size: 22,
            bold: isHeader, color: isHeader ? "FFFFFF" : "212121"
          })]
        })]
      })
    )
  });
}

// ── 主文档构建 ────────────────────────────────────────────────────
function buildDocument(content, diagramPath) {
  const children = [];

  // 封面
  children.push(
    new Paragraph({ spacing: { before: 2000, after: 400 } }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text: content.title || "论文解读报告",
        font: "Arial", size: 52, bold: true, color: "37474F"
      })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      spacing: { before: 200, after: 200 },
      children: [new TextRun({
        text: content.authors || "",
        font: "Arial", size: 28, color: "757575"
      })]
    }),
    new Paragraph({
      alignment: AlignmentType.CENTER,
      children: [new TextRun({
        text: content.venue || "",
        font: "Arial", size: 24, italics: true, color: "9E9E9E"
      })]
    }),
    new Paragraph({ spacing: { before: 400, after: 0 } }),
  );

  // 框架图
  if (diagramPath && fs.existsSync(diagramPath)) {
    const imgBuffer = fs.readFileSync(diagramPath);
    children.push(
      heading("论文框架图", HeadingLevel.HEADING_1),
      new Paragraph({
        alignment: AlignmentType.CENTER,
        spacing: { before: 200, after: 200 },
        children: [new ImageRun({
          data: imgBuffer,
          transformation: { width: 620, height: 286 },  // 约 A4 内容宽
          type: "png"
        })]
      }),
      divider(),
      new Paragraph({ children: [new PageBreak()] })
    );
  }

  // 各模块
  const sections = content.sections || [];
  for (const section of sections) {
    children.push(heading(section.title, HeadingLevel.HEADING_1));

    for (const block of (section.blocks || [])) {
      if (block.type === "heading2") {
        children.push(heading(block.text, HeadingLevel.HEADING_2));
      } else if (block.type === "heading3") {
        children.push(heading(block.text, HeadingLevel.HEADING_3));
      } else if (block.type === "text") {
        children.push(para(block.text));
      } else if (block.type === "bullet") {
        for (const item of block.items) children.push(bulletItem(item));
      } else if (block.type === "table") {
        const rows = [buildTableRow(block.headers, true),
                      ...block.rows.map(r => buildTableRow(r))];
        children.push(new Table({
          width: { size: 9360, type: WidthType.DXA },
          columnWidths: Array(block.headers.length).fill(
            Math.floor(9360 / block.headers.length)
          ),
          rows
        }));
        children.push(new Paragraph({ spacing: { after: 120 } }));
      }
    }
    children.push(divider());
  }

  return new Document({
    numbering: {
      config: [{
        reference: "bullets",
        levels: [{
          level: 0, format: LevelFormat.BULLET, text: "•",
          alignment: AlignmentType.LEFT,
          style: { paragraph: { indent: { left: 720, hanging: 360 } } }
        }]
      }]
    },
    styles: STYLES,
    sections: [{
      properties: {
        page: {
          size: { width: 12240, height: 15840 },
          margin: { top: 1440, right: 1440, bottom: 1440, left: 1440 }
        }
      },
      children
    }]
  });
}

// ── 入口 ──────────────────────────────────────────────────────────
async function main() {
  const args = parseArgs();

  if (!args.content || !args.output) {
    console.error("用法: node generate_docx.js --content <json> --diagram <png> --output <docx>");
    process.exit(1);
  }

  const content = JSON.parse(fs.readFileSync(args.content, "utf-8"));
  const doc     = buildDocument(content, args.diagram);
  const buffer  = await Packer.toBuffer(doc);

  fs.writeFileSync(args.output, buffer);
  console.log(`✅ Word 文档已生成：${args.output}`);
}

main().catch(err => { console.error(err); process.exit(1); });
