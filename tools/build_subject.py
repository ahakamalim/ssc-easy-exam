#!/usr/bin/env python3
"""Generalized chapter builder for any subject (chem/bio/phy)."""
import json, os, random, importlib, sys
from collections import defaultdict, Counter
import gen_pdfs
import subj_config

REPO = "/home/user/ssc-easy-exam"

def load_questions(subj, nn):
    parts = []
    for suffix in ("a", "b", "c", "d", "e", "f"):
        try:
            m = importlib.import_module(f"q_{subj}{nn}_{suffix}")
            for attr in ("QUESTIONS_A", "QUESTIONS_B", "QUESTIONS_C", "QUESTIONS_D", "QUESTIONS_D_EXTRA", "QUESTIONS_D_EXTRA2", "QUESTIONS_E", "QUESTIONS_E_EXTRA", "QUESTIONS_F"):
                if hasattr(m, attr):
                    parts.extend(getattr(m, attr))
        except ImportError:
            continue
    return parts

def build(subj, chapter_no, n_pdfs=15):
    cfg = subj_config.SUBJECTS[subj]
    nn = f"{chapter_no:02d}"
    raw = load_questions(subj, nn)
    seen = set(); uniq = []
    for q in raw:
        stem = q[0].strip()
        if stem in seen: continue
        seen.add(stem); uniq.append(q)

    rng = random.Random(12345 + chapter_no * 7)
    def mk(q):
        stem, opts, ans, topic, kind = q
        idx = [0,1,2,3]; rng.shuffle(idx)
        new_opts = [opts[i] for i in idx]
        new_ans = idx.index(ans)
        return {
            "question": stem,
            "options": {"A": new_opts[0], "B": new_opts[1], "C": new_opts[2], "D": new_opts[3]},
            "correctAnswer": "ABCD"[new_ans],
            "topic": topic, "kind": kind,
            "source": "board-standard", "board": "", "year": None,
            "reference": "", "verificationStatus": "board-standard",
        }
    qs = [mk(q) for q in uniq]

    by_topic = defaultdict(list)
    for q in qs:
        by_topic[q["topic"]].append(q)
    rnd = random.Random(42)
    for t in by_topic:
        rnd.shuffle(by_topic[t])
    topics = list(by_topic.keys())
    idx = {t:0 for t in topics}
    interleaved = []
    remaining = set(topics)
    while remaining:
        for t in list(topics):
            if idx[t] < len(by_topic[t]):
                interleaved.append(by_topic[t][idx[t]]); idx[t] += 1
            else:
                remaining.discard(t)

    target = n_pdfs * 25
    if len(interleaved) < target:
        print(f"[WARN] only {len(interleaved)} unique questions (need {target})")
    interleaved = interleaved[:target]
    for i, q in enumerate(interleaved, 1):
        q["serial"] = i
    answer_box = {str(q["serial"]): q["correctAnswer"] for q in interleaved}

    data = {
        "subject": cfg["bn"], "chapterNo": chapter_no,
        "chapter": cfg["short"][chapter_no],
        "questions": interleaved, "answerBox": answer_box,
    }
    canon = cfg["short"][chapter_no].replace(",", "").replace(" ", "-")
    bank_path = os.path.join(REPO, "files", cfg["code"], f"ch{nn}-{canon}.json")
    os.makedirs(os.path.dirname(bank_path), exist_ok=True)
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    out_dir = os.path.join(REPO, "files", cfg["code"], f"Chapter_{nn}", "mcq")
    files = gen_pdfs.main(cfg["bn"], cfg["code"], chapter_no, bank_path, out_dir, n_pdfs=n_pdfs)

    dist = Counter(q["topic"] for q in interleaved)
    print(f"[DIST] {cfg['bn']} ch{nn} ({len(interleaved)}): " + "; ".join(f"{t}:{n}" for t,n in sorted(dist.items())))
    return files

if __name__ == "__main__":
    build(sys.argv[1], int(sys.argv[2]))
