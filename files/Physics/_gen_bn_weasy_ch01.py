#!/usr/bin/env python3
"""Bengali MCQ PDFs via WeasyPrint + HarfBuzz + embedded Noto Sans Bengali."""
import json, os, html
from weasyprint import HTML, CSS

FONT = "/home/user/.fonts/NotoSansBengali-Regular.ttf"
SRC = "/home/user/ssc-easy-exam/files/Physics/ch01-ভৌত-রাশি-ও-পরিমাপ.json"
OUT = "/home/user/ssc-easy-exam/files/Physics/Chapter_01/mcq"
os.makedirs(OUT, exist_ok=True)

BN = "০১২৩৪৫৬৭৮৯"
def bn(n):
    return "".join(BN[int(c)] if c.isdigit() else c for c in str(n))

MAP = {"A": "ক", "B": "খ", "C": "গ", "D": "ঘ"}
SETS = "কখগঘঙচছজ"

PREFLIGHT = [
    "পদার্থবিজ্ঞান", "অধ্যায়", "ভৌত রাশি ও পরিমাপ", "বহুনির্বাচনি",
    "তড়িৎ প্রবাহ", "কিলোগ্রাম", "অ্যাম্পিয়ার",
    "সঠিক উত্তরের বৃত্তটি কলম দিয়ে সম্পূর্ণ ভরাট কর",
]

data = json.load(open(SRC, encoding="utf-8"))
qs = data["questions"]
n_sets = len(qs) // 25

CSS_TEXT = f"""
@font-face {{
  font-family: "NotoSansBengali";
  src: url("file://{FONT}") format("truetype");
  font-weight: 400;
  font-style: normal;
}}
@page {{
  size: A4;
  margin: 12mm 11mm 12mm 11mm;
}}
html, body {{
  font-family: "NotoSansBengali", sans-serif;
  font-size: 10.2pt;
  line-height: 1.45;
  color: #111;
}}
.topbar {{
  background: #1a3a6b;
  color: #fff;
  padding: 5px 8px;
  font-size: 8.5pt;
  display: flex;
  justify-content: space-between;
}}
.head {{
  display: flex;
  justify-content: space-between;
  align-items: flex-start;
  margin-top: 8px;
  border-bottom: 1.5px solid #1a3a6b;
  padding-bottom: 6px;
}}
.hleft h1 {{ font-size: 15pt; margin: 0; }}
.hleft p {{ margin: 2px 0; font-size: 9.5pt; }}
.codebox {{
  border: 1.4px solid #1a3a6b;
  padding: 4px 6px;
  text-align: center;
  font-size: 8.5pt;
}}
.digits {{ display: flex; gap: 3px; justify-content: center; margin-top: 3px; }}
.digits span {{
  border: 1px solid #1a3a6b;
  width: 18px; height: 18px;
  display: inline-flex; align-items: center; justify-content: center;
  font-size: 11pt;
}}
.note {{
  background: #fff8dc;
  border: 1px solid #1a3a6b;
  padding: 4px 7px;
  font-size: 8pt;
  margin: 7px 0 8px;
}}
.cols {{
  column-count: 2;
  column-gap: 14px;
}}
.q {{
  break-inside: avoid;
  margin: 0 0 8px;
}}
.q .stem {{ font-size: 10pt; }}
.opt {{ margin: 1px 0 0 10px; font-size: 9.4pt; }}
.abox {{
  border: 1.6px solid #1a3a6b;
  margin-top: 10px;
}}
.abox h2 {{
  background: #1a3a6b;
  color: #fff;
  margin: 0;
  padding: 6px;
  font-size: 12pt;
  text-align: center;
}}
.agrid {{
  display: grid;
  grid-template-columns: repeat(5, 1fr);
}}
.acell {{
  border: 0.5px solid #1a3a6b;
  padding: 10px 4px;
  text-align: center;
  font-size: 10.5pt;
}}
.preflight {{
  page-break-after: always;
  padding: 20px;
}}
"""

def q_html(i, it):
    stem = html.escape(f"{bn(i)}। {it['question']}")
    opts = "".join(
        f'<div class="opt">({MAP[k]}) {html.escape(it["options"][k])}</div>'
        for k in "ABCD"
    )
    return f'<div class="q"><div class="stem">{stem}</div>{opts}</div>'

def page_header(set_no):
    return f"""
    <div class="topbar">
      <span>মাধ্যমিক সমাপনী পরীক্ষা | পদার্থবিজ্ঞান | বহুনির্বাচনি</span>
      <span>সময়: ২৫ মিনিট &nbsp; পূর্ণমান: ২৫</span>
    </div>
    <div class="head">
      <div class="hleft">
        <h1>পদার্থবিজ্ঞান</h1>
        <p>অধ্যায় ০১ : ভৌত রাশি ও পরিমাপ</p>
        <p>এমসিকিউ সেট {bn(set_no):0>2} &nbsp;|&nbsp; সেট : {SETS[(set_no-1)%8]}</p>
      </div>
      <div class="codebox">
        বিষয় কোড
        <div class="digits"><span>১</span><span>৩</span><span>৬</span></div>
      </div>
    </div>
    <div class="note">বিশেষ দ্রষ্টব্য : সঠিক উত্তরের বৃত্তটি কলম দিয়ে সম্পূর্ণ ভরাট কর। প্রতিটি প্রশ্নের মান ১।</div>
    """

def make_set(set_no, items):
    answers = [MAP[it["correctAnswer"]] for it in items]
    body = "".join(q_html(i, it) for i, it in enumerate(items, 1))
    cells = "".join(
        f'<div class="acell">{bn(i)} → {a}</div>'
        for i, a in enumerate(answers, 1)
    )
    doc = f"""<!DOCTYPE html>
<html lang="bn"><head><meta charset="utf-8"><title>সেট {set_no}</title></head>
<body>
{page_header(set_no)}
<div class="cols">{body}</div>
<div class="abox">
  <h2>উত্তরমালা (ANSWER BOX) — ১ থেকে ২৫</h2>
  <div class="agrid">{cells}</div>
</div>
</body></html>"""
    path = os.path.join(OUT, f"Physics_Ch01_MCQ_Set_{set_no:02d}.pdf")
    HTML(string=doc, base_url="/").write_pdf(
        path, stylesheets=[CSS(string=CSS_TEXT)]
    )
    return path

# Preflight strip
pf = f"""<!DOCTYPE html><html lang="bn"><meta charset="utf-8">
<body>
<h2>বাংলা প্রি-ফ্লাইট</h2>
{"<br>".join(html.escape(w) for w in PREFLIGHT)}
<p>তড়িৎ প্রবাহ (Electric current) — কিলোগ্রাম — অ্যাম্পিয়ার</p>
<p>১। পদার্থবিজ্ঞানীরা বিশ্বব্রহ্মাণ্ডের দৃশ্যমান গ্রহ</p>
</body></html>"""
HTML(string=pf, base_url="/").write_pdf(
    "/tmp/bn_preflight.pdf", stylesheets=[CSS(string=CSS_TEXT)]
)

files = []
for s in range(n_sets):
    chunk = qs[s * 25:(s + 1) * 25]
    assert len(chunk) == 25
    files.append(make_set(s + 1, chunk))
print("OK", n_sets)
for f in files:
    print(os.path.basename(f), os.path.getsize(f))
