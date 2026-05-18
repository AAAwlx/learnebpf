#!/usr/bin/env python3
# -*- coding: utf-8 -*-
import html
import re
import zipfile
from pathlib import Path

BASE = Path(__file__).resolve().parent
MD = BASE / "基于eBPF的Linux内核防火墙故障诊断系统毕业论文.md"
OUT = BASE / "基于eBPF的Linux内核防火墙故障诊断系统毕业论文_西邮模板版.docx"
TITLE = "基于 eBPF 的 Linux 内核防火墙故障诊断系统的设计与实现"


def esc(s: str) -> str:
    return html.escape(s, quote=False)


def clean_inline(s: str) -> str:
    s = re.sub(r"\*\*(.*?)\*\*", r"\1", s)
    s = re.sub(r"`([^`]*)`", r"\1", s)
    return s


def r(text, bold=False, size="24", east="宋体", ascii_font="Times New Roman"):
    b = "<w:b/>" if bold else ""
    return (
        f"<w:r><w:rPr><w:rFonts w:ascii=\"{ascii_font}\" w:hAnsi=\"{ascii_font}\" "
        f"w:eastAsia=\"{east}\"/>{b}<w:sz w:val=\"{size}\"/><w:szCs w:val=\"{size}\"/>"
        f"</w:rPr><w:t xml:space=\"preserve\">{esc(text)}</w:t></w:r>"
    )


def p(text="", style=None, align=None, indent=False, bold=False, size="24", east="宋体", ascii_font="Times New Roman", before=None, after=None, line="400", keep=False):
    ppr = []
    if style:
        ppr.append(f'<w:pStyle w:val="{style}"/>')
    if align:
        ppr.append(f'<w:jc w:val="{align}"/>')
    if indent:
        ppr.append('<w:ind w:firstLine="480"/>')
    if before is not None or after is not None or line is not None:
        attrs = []
        if before is not None:
            attrs.append(f'w:before="{before}"')
        if after is not None:
            attrs.append(f'w:after="{after}"')
        if line is not None:
            attrs.append(f'w:line="{line}" w:lineRule="exact"')
        ppr.append(f"<w:spacing {' '.join(attrs)}/>")
    if keep:
        ppr.append("<w:keepNext/>")
    return f"<w:p><w:pPr>{''.join(ppr)}</w:pPr>{r(clean_inline(text), bold, size, east, ascii_font)}</w:p>"


def page_break():
    return '<w:p><w:pPr><w:pageBreakBefore/></w:pPr></w:p>'


def table(rows):
    if not rows:
        return ""
    cols = max(len(x) for x in rows)
    width = max(900, int(9360 / cols))
    grid = "".join(f'<w:gridCol w:w="{width}"/>' for _ in range(cols))
    trs = []
    for i, row in enumerate(rows):
        row = row + [""] * (cols - len(row))
        cells = []
        for cell in row:
            shade = '<w:shd w:fill="D9EAF7"/>' if i == 0 else ""
            tcpr = f'<w:tcW w:w="{width}" w:type="dxa"/>{shade}<w:vAlign w:val="center"/>'
            cells.append(f"<w:tc><w:tcPr>{tcpr}</w:tcPr>{p(cell, align='center' if i == 0 else None, size='22', line='240', before='60', after='60')}</w:tc>")
        trs.append(f"<w:tr>{''.join(cells)}</w:tr>")
    borders = (
        '<w:tblBorders>'
        '<w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        '<w:insideH w:val="single" w:sz="6" w:space="0" w:color="999999"/>'
        '</w:tblBorders>'
    )
    return f'<w:tbl><w:tblPr><w:tblW w:w="9360" w:type="dxa"/>{borders}</w:tblPr><w:tblGrid>{grid}</w:tblGrid>{"".join(trs)}</w:tbl>'


def parse_md():
    lines = MD.read_text(encoding="utf-8").splitlines()
    tokens = []
    i = 0
    in_code = False
    code_lang = ""
    code_lines = []
    para_lines = []

    def flush_para():
        nonlocal para_lines
        if para_lines:
            tokens.append(("p", " ".join(x.strip() for x in para_lines).strip()))
            para_lines = []

    while i < len(lines):
        line = lines[i]
        if line.startswith("```"):
            if not in_code:
                flush_para()
                in_code = True
                code_lang = line[3:].strip()
                code_lines = []
            else:
                tokens.append(("code", code_lang, "\n".join(code_lines)))
                in_code = False
            i += 1
            continue
        if in_code:
            code_lines.append(line)
            i += 1
            continue
        if not line.strip():
            flush_para()
            i += 1
            continue
        m = re.match(r"^(#{1,6})\s+(.*)$", line)
        if m:
            flush_para()
            tokens.append(("h", len(m.group(1)), m.group(2).strip()))
            i += 1
            continue
        if line.strip().startswith("|") and "|" in line.strip()[1:]:
            flush_para()
            rows = []
            while i < len(lines) and lines[i].strip().startswith("|"):
                raw = lines[i].strip()
                cells = [c.strip() for c in raw.strip("|").split("|")]
                if not all(re.fullmatch(r":?-{3,}:?", c or "") for c in cells):
                    rows.append([clean_inline(c) for c in cells])
                i += 1
            tokens.append(("table", rows))
            continue
        if re.match(r"^\d+\.\s+", line.strip()) or line.strip().startswith("- "):
            flush_para()
            tokens.append(("li", re.sub(r"^(\d+\.\s+|- )", "", line.strip())))
            i += 1
            continue
        para_lines.append(line)
        i += 1
    flush_para()
    return tokens


def build_body(tokens):
    body = []
    body.append(p("毕业设计（论文）", style="Title", align="center", bold=True, size="36", east="黑体", before="800", after="400"))
    body.append(p(f"题    目：{TITLE}", align="center", bold=False, size="28", before="240", after="120"))
    for label in ["学    院：", "专    业：", "班    级：", "学    号：", "学生姓名：", "导师姓名：               职称：", "起止时间：                 至"]:
        body.append(p(label + "                                    ", align="center", size="24", before="0", after="0"))
    body.append(p("2026 年 5 月 18 日", align="center", size="24", before="360", after="0"))
    body.append(page_break())

    headings = [t for t in tokens if t[0] == "h" and t[1] in (2, 3)]
    body.append(p("目  录", style="Heading1", align="center", bold=True, size="30", east="黑体", before="800", after="400"))
    for _, level, text in headings:
        if text in ("大纲规划", "正文"):
            continue
        prefix = "" if level == 2 else "    "
        body.append(p(prefix + text, size="24", before="120" if level == 2 else "0", after="0", indent=False))
    body.append(page_break())

    skip_until_body = True
    in_refs = False
    for token in tokens:
        if token[0] == "h":
            level, text = token[1], token[2]
            if level == 1:
                continue
            if text == "正文":
                skip_until_body = False
                continue
            if skip_until_body:
                continue
            in_refs = text == "参考文献"
            if level == 2:
                body.append(page_break() if text in ("摘要", "Abstract", "第1章 绪论", "参考文献", "致谢", "附录A 论文大纲") else "")
                east = "黑体" if text != "Abstract" else "Arial"
                body.append(p(text, style="Heading1", align="center", bold=True, size="30", east=east, ascii_font="Arial" if text == "Abstract" else "Times New Roman", before="800", after="400"))
            elif level == 3:
                body.append(p(text, style="Heading2", bold=True, size="28", east="黑体", before="480", after="120", keep=True))
            elif level >= 4:
                body.append(p(text, style="Heading3", bold=True, size="24", east="黑体", before="240", after="120", keep=True))
        elif skip_until_body:
            continue
        elif token[0] == "p":
            text = token[1]
            if not text:
                continue
            if text.startswith("关键词") or text.startswith("Key words"):
                body.append(p(text, indent=False, size="24", before="160", after="0", bold=False))
            elif re.match(r"^图\d", text):
                body.append(p(text, align="center", indent=False, size="22", before="120", after="240"))
            elif re.match(r"^表\d", text):
                body.append(p(text, align="center", indent=False, bold=True, size="22", east="黑体", before="160", after="80"))
            else:
                body.append(p(text, indent=not in_refs, size="21" if in_refs else "24", line="320" if in_refs else "400", before="60" if in_refs else "0", after="0"))
        elif token[0] == "li":
            body.append(p(token[1], indent=True, size="24", before="0", after="0"))
        elif token[0] == "table":
            body.append(table(token[1]))
        elif token[0] == "code":
            lang, text = token[1], token[2]
            label = "Mermaid 图源码" if lang == "mermaid" else f"代码（{lang}）" if lang else "代码"
            body.append(p(label, indent=False, bold=True, size="22", east="黑体", before="160", after="80"))
            for line in text.splitlines():
                body.append(p(line, indent=False, size="18", east="Courier New", ascii_font="Courier New", line="260", before="0", after="0"))
    sect = (
        '<w:sectPr><w:pgSz w:w="11906" w:h="16838"/>'
        '<w:pgMar w:top="1440" w:right="1440" w:bottom="1440" w:left="1440" w:header="720" w:footer="720" w:gutter="0"/>'
        '<w:cols w:space="720"/><w:docGrid w:linePitch="312"/></w:sectPr>'
    )
    return "".join(str(x) for x in body if x) + sect


def styles_xml():
    return '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:styles xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main">
<w:style w:type="paragraph" w:default="1" w:styleId="Normal"><w:name w:val="Normal"/><w:pPr><w:spacing w:line="400" w:lineRule="exact" w:before="0" w:after="0"/><w:jc w:val="both"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="宋体"/><w:sz w:val="24"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Title"><w:name w:val="Title"/><w:pPr><w:spacing w:before="800" w:after="400" w:line="400" w:lineRule="exact"/><w:jc w:val="center"/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="36"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading1"><w:name w:val="heading 1"/><w:pPr><w:spacing w:before="800" w:after="400" w:line="400" w:lineRule="exact"/><w:jc w:val="center"/><w:keepNext/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="30"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading2"><w:name w:val="heading 2"/><w:pPr><w:spacing w:before="480" w:after="120" w:line="400" w:lineRule="exact"/><w:keepNext/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="28"/></w:rPr></w:style>
<w:style w:type="paragraph" w:styleId="Heading3"><w:name w:val="heading 3"/><w:pPr><w:spacing w:before="240" w:after="120" w:line="400" w:lineRule="exact"/><w:keepNext/></w:pPr><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman" w:eastAsia="黑体"/><w:b/><w:sz w:val="24"/></w:rPr></w:style>
</w:styles>'''


def write_docx():
    tokens = parse_md()
    document = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<w:document xmlns:w="http://schemas.openxmlformats.org/wordprocessingml/2006/main"><w:body>{build_body(tokens)}</w:body></w:document>'''
    content_types = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>
<Default Extension="xml" ContentType="application/xml"/>
<Override PartName="/word/document.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.document.main+xml"/>
<Override PartName="/word/styles.xml" ContentType="application/vnd.openxmlformats-officedocument.wordprocessingml.styles+xml"/>
<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>
<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>
</Types>'''
    rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"><Relationship Id="rId1" Type="http://schemas.openxmlformats.org/officeDocument/2006/relationships/officeDocument" Target="word/document.xml"/></Relationships>'''
    doc_rels = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships"/>'''
    core = f'''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" xmlns:dc="http://purl.org/dc/elements/1.1/"><dc:title>{esc(TITLE)}</dc:title><dc:creator>Codex</dc:creator></cp:coreProperties>'''
    app = '''<?xml version="1.0" encoding="UTF-8" standalone="yes"?><Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties"><Application>Codex</Application></Properties>'''
    with zipfile.ZipFile(OUT, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", content_types)
        z.writestr("_rels/.rels", rels)
        z.writestr("word/_rels/document.xml.rels", doc_rels)
        z.writestr("word/document.xml", document)
        z.writestr("word/styles.xml", styles_xml())
        z.writestr("docProps/core.xml", core)
        z.writestr("docProps/app.xml", app)
    print(OUT)


if __name__ == "__main__":
    write_docx()
