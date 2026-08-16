#!/usr/bin/env python3
"""
SSC MCQ PDF generator — clean student-facing format (subject-generalized).

FINAL LAYOUT: exactly 2 pages = 25 MCQs + compact answer key at bottom of page 2.

- Reads a chapter question bank (JSON)
- Produces N PDFs of exactly 25 MCQs each
- Clean paper: NO board / year / chapter / source / coaching labels
- Bengali Noto Sans font embedded
"""
import json, os, html
from weasyprint import HTML, CSS

FONT_R = "/home/user/.fonts/NotoSansBengali-Regular.ttf"
FONT_B = "/home/user/.fonts/NotoSansBengali-Bold.ttf"

BN = "০১২৩৪৫৬৭৮৯"
def bn(n):
    return "".join(BN[int(c)] if c.isdigit() else c for c in str(n))

MAP = {"A": "ক", "B": "খ", "C": "গ", "D": "ঘ"}

CSS_TEXT = f"""
@font-face {{ font-family:"BN"; src:url("file://{FONT_R}"); font-weight:400; font-style:normal; }}
@font-face {{ font-family:"BN"; src:url("file://{FONT_B}"); font-weight:700; font-style:normal; }}
@page {{ size:A4; margin:6mm 7mm 6mm 7mm; }}
html, body {{ font-family:"BN",sans-serif; font-size:9.3pt; line-height:1.3; color:#111; }}
.topbar {{
  background:#1a3a6b; color:#fff; padding:4px 9px; font-size:8.4pt;
  display:flex; justify-content:space-between; border-radius:3px;
}}
.title {{ text-align:center; margin:4px 0 2px; }}
.title h1 {{ font-size:13pt; margin:0; color:#1a3a6b; }}
.rule {{ border-bottom:1.2px solid #1a3a6b; margin:3px 0 3px; }}
.note {{
  background:#f4f6fb; border:1px solid #c7d2e6; border-radius:3px;
  padding:2px 8px; font-size:7.8pt; margin:2px 0 3px; color:#333;
}}
.q {{ break-inside:avoid; margin:0 0 4px; }}
.q .stem {{ font-size:9.5pt; font-weight:700; }}
.opts {{ display:grid; grid-template-columns:1fr 1fr; column-gap:10px; }}
.opt {{ font-size:9.2pt; margin-top:0.5px; }}
.abox {{ border:1.4px solid #1a3a6b; margin-top:8px; border-radius:3px; overflow:hidden; break-inside:avoid; }}
.abox h2 {{
  background:#1a3a6b; color:#fff; margin:0; padding:3px; font-size:10pt; text-align:center;
}}
.agrid {{ display:grid; grid-template-columns:repeat(5,1fr); }}
.acell {{ border:0.5px solid #1a3a6b; padding:3px 2px; text-align:center; font-size:8.6pt; }}
"""

def q_html(i, it):
    stem = html.escape(f"{bn(i)}। {it['question']}")
    opts = "".join(
        f'<div class="opt">({MAP[k]}) {html.escape(it["options"][k])}</div>'
        for k in "ABCD"
    )
    return f'<div class="q"><div class="stem">{stem}</div><div class="opts">{opts}</div></div>'

def page_header(subject_bn):
    return f"""
    <div class="topbar">
      <span>{html.escape(subject_bn)} — বহুনির্বাচনি প্রশ্নপত্র</span>
      <span>সময় : ২৫ মিনিট &nbsp;|&nbsp; পূর্ণমান : ২৫</span>
    </div>
    <div class="title"><h1>বহুনির্বাচনি প্রশ্ন (MCQ)</h1></div>
    <div class="rule"></div>
    <div class="note">নির্দেশনা : প্রতিটি প্রশ্নের মান ১। সঠিক উত্তরের বৃত্তটি কলম দিয়ে সম্পূর্ণ ভরাট কর।</div>
    """

def make_set(subject_bn, items):
    body = "".join(q_html(i, it) for i, it in enumerate(items, 1))
    answers = [MAP[it["correctAnswer"]] for it in items]
    cells = "".join(f'<div class="acell">{bn(i)}→{a}</div>' for i, a in enumerate(answers, 1))
    return f"""<!DOCTYPE html>
<html lang="bn"><head><meta charset="utf-8"><title>MCQ</title></head>
<body>
{page_header(subject_bn)}
{body}
<div class="abox"><h2>উত্তরমালা (ANSWER KEY)</h2><div class="agrid">{cells}</div></div>
</body></html>"""

def norm(s):
    return " ".join(s.split()).strip()

def validate(sets):
    seen = {}
    errors = []
    for si, items in enumerate(sets, 1):
        if len(items) != 25:
            errors.append(f"set {si}: {len(items)} questions")
        local = set()
        for it in items:
            q = norm(it["question"])
            if q in local:
                errors.append(f"set {si}: dup -> {q[:40]}")
            local.add(q)
            if sorted(it["options"].keys()) != ["A", "B", "C", "D"]:
                errors.append(f"set {si}: bad options -> {q[:40]}")
            if it["correctAnswer"] not in "ABCD":
                errors.append(f"set {si}: bad answer -> {q[:40]}")
            if q in seen:
                errors.append(f"set {si}: cross-set dup -> {q[:40]}")
            else:
                seen[q] = si
    return errors

def main(subject_bn, prefix, chapter_no, bank_path, out_dir, n_pdfs=15):
    data = json.load(open(bank_path, encoding="utf-8"))
    qs = data["questions"]
    per = 25
    sets = [qs[i*per:(i+1)*per] for i in range(len(qs)//per)]
    sets = sets[:n_pdfs]
    errs = validate(sets)
    if errs:
        print("[QA FAIL]")
        for e in errs:
            print("  -", e)
        return None
    os.makedirs(out_dir, exist_ok=True)
    written = []
    for si, items in enumerate(sets, 1):
        doc = make_set(subject_bn, items)
        path = os.path.join(out_dir, f"{prefix}_Ch{chapter_no:02d}_MCQ_Set_{si:02d}.pdf")
        HTML(string=doc, base_url="/").write_pdf(path, stylesheets=[CSS(string=CSS_TEXT)])
        written.append(path)
    print(f"[OK] {prefix} ch{chapter_no}: {len(written)} PDFs, QA passed")
    return written
