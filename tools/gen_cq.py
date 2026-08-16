#!/usr/bin/env python3
"""Creative (CQ) question PDF generator — subject-generalized.

One CQ PDF per chapter = 2 creative passages, each:
  উদ্দীপক (stimulus box) + ক/খ/গ/ঘ sub-questions with marks.
"""
import json, os, html, importlib
from weasyprint import HTML, CSS
import subj_config

FONT_R = "/home/user/.fonts/NotoSansBengali-Regular.ttf"
FONT_B = "/home/user/.fonts/NotoSansBengali-Bold.ttf"
REPO = "/home/user/ssc-easy-exam"

BN = "০১২৩৪৫৬৭৮৯"
def bn(n): return "".join(BN[int(c)] if c.isdigit() else c for c in str(n))

CSS_TEXT = f"""
@font-face {{ font-family:"BN"; src:url("file://{FONT_R}"); font-weight:400; font-style:normal; }}
@font-face {{ font-family:"BN"; src:url("file://{FONT_B}"); font-weight:700; font-style:normal; }}
@page {{ size:A4; margin:10mm 11mm 10mm 11mm; }}
html, body {{ font-family:"BN",sans-serif; font-size:11pt; line-height:1.6; color:#111; }}
.topbar {{ background:#7a1a1a; color:#fff; padding:6px 12px; font-size:9.5pt;
  display:flex; justify-content:space-between; border-radius:4px; }}
.title {{ text-align:center; margin:10px 0 4px; }}
.title h1 {{ font-size:16pt; margin:0; color:#7a1a1a; }}
.rule {{ border-bottom:1.5px solid #7a1a1a; margin:6px 0 10px; }}
.cq {{ break-inside:avoid; margin-bottom:18px; }}
.cq .qhead {{ font-size:12pt; font-weight:700; color:#7a1a1a; margin-bottom:6px; }}
.stim {{ background:#fdf3f3; border:1.4px solid #7a1a1a; border-radius:5px; padding:9px 12px; margin-bottom:8px; }}
.stim .lbl {{ font-weight:700; display:block; margin-bottom:3px; }}
.sub {{ margin:4px 0 0 4px; }}
.sub .tag {{ font-weight:700; }}
.sub .mk {{ color:#666; font-size:9.5pt; }}
"""

def build(subj, chapter_no):
    cfg = subj_config.SUBJECTS[subj]
    nn = f"{chapter_no:02d}"
    mod = importlib.import_module(f"q_{subj}{nn}_cq")
    passages = mod.PASSAGES  # list of (stimulus, [(sub_q, mark), ...])
    parts = []
    for pi, (stim, subs) in enumerate(passages, 1):
        tags = ["ক", "খ", "গ", "ঘ"]
        sub_html = "".join(
            f'<div class="sub"><span class="tag">({tags[j]})</span> {html.escape(q)} <span class="mk">[{m}]</span></div>'
            for j, (q, m) in enumerate(subs)
        )
        parts.append(
            f'<div class="cq"><div class="qhead">সৃজনশীল প্রশ্ন {bn(pi)}</div>'
            f'<div class="stim"><span class="lbl">উদ্দীপক :</span>{html.escape(stim)}</div>'
            f'{sub_html}</div>'
        )
    doc = f"""<!DOCTYPE html>
<html lang="bn"><head><meta charset="utf-8"><title>CQ</title></head>
<body>
<div class="topbar"><span>{html.escape(cfg['bn'])} — সৃজনশীল প্রশ্ন (CQ)</span><span>পূর্ণমান : ২০</span></div>
<div class="title"><h1>সৃজনশীল প্রশ্ন</h1></div>
<div class="rule"></div>
{''.join(parts)}
</body></html>"""
    out_dir = os.path.join(REPO, "files", cfg["code"], f"Chapter_{nn}", "cq")
    os.makedirs(out_dir, exist_ok=True)
    path = os.path.join(out_dir, f"{cfg['code']}_Ch{nn}_CQ_01.pdf")
    HTML(string=doc, base_url="/").write_pdf(path, stylesheets=[CSS(string=CSS_TEXT)])
    print(f"[OK] {cfg['code']} ch{nn}: CQ PDF ({len(passages)} passages)")
    return path

if __name__ == "__main__":
    import sys
    build(sys.argv[1], int(sys.argv[2]))
