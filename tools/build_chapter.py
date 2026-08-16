#!/usr/bin/env python3
"""
Build a chapter's question-bank JSON + generate its MCQ PDFs.

Usage:
  python3 build_chapter.py <chapterNo> "<chapterName>"

It imports QUESTIONS_A/B/C from q_ch<NN>_a/b/c.py in the same dir,
dedupes by exact stem, interleaves topics round-robin (shuffled within
topic) for balanced topic mixing, keeps 375 questions (15 sets x 25),
writes files/Physics/chNN-*.json and calls gen_pdfs.main().
"""
import json, os, sys, random, importlib
from collections import defaultdict, Counter

import gen_pdfs

REPO = "/home/user/ssc-easy-exam"

def load_questions(nn):
    parts = []
    for suffix in ("a", "b", "c", "d", "e", "f"):
        try:
            m = importlib.import_module(f"q_ch{nn}_{suffix}")
            for attr in ("QUESTIONS_A", "QUESTIONS_B", "QUESTIONS_C", "QUESTIONS_D", "QUESTIONS_D_EXTRA", "QUESTIONS_E", "QUESTIONS_F"):
                if hasattr(m, attr):
                    parts.extend(getattr(m, attr))
        except ImportError:
            continue
    return parts

def build(chapter_no, chapter_name):
    nn = f"{chapter_no:02d}"
    raw = load_questions(nn)
    # dedupe by exact stem (first occurrence kept)
    seen = set()
    uniq = []
    for q in raw:
        stem = q[0].strip()
        if stem in seen:
            continue
        seen.add(stem)
        uniq.append(q)

    # Deterministic option shuffler so correct answers are evenly spread
    # across ক/খ/গ/ঘ (a real exam never has all answers in one position).
    opt_rng = random.Random(12345 + chapter_no)

    def mk(q):
        stem, opts, ans, topic, kind = q
        idx = [0, 1, 2, 3]
        opt_rng.shuffle(idx)
        new_opts = [opts[i] for i in idx]
        new_ans = idx.index(ans)
        return {
            "question": stem,
            "options": {"A": new_opts[0], "B": new_opts[1],
                        "C": new_opts[2], "D": new_opts[3]},
            "correctAnswer": "ABCD"[new_ans],
            "topic": topic,
            "kind": kind,
            "source": "board-standard",
            "board": "",
            "year": None,
            "reference": "",
            "verificationStatus": "board-standard",
        }

    qs = [mk(q) for q in uniq]

    # group by topic, shuffle within topic (deterministic seed)
    by_topic = defaultdict(list)
    for q in qs:
        by_topic[q["topic"]].append(q)
    random.seed(42)
    for t in by_topic:
        random.shuffle(by_topic[t])

    # round-robin interleave topics -> balanced mixing
    topics = list(by_topic.keys())
    idx = {t: 0 for t in topics}
    interleaved = []
    remaining = set(topics)
    while remaining:
        for t in list(topics):
            if idx[t] < len(by_topic[t]):
                interleaved.append(by_topic[t][idx[t]])
                idx[t] += 1
            else:
                remaining.discard(t)

    target = 375
    if len(interleaved) < target:
        print(f"[WARN] only {len(interleaved)} unique questions (need {target})")
    interleaved = interleaved[:target]

    for i, q in enumerate(interleaved, 1):
        q["serial"] = i

    answer_box = {str(q["serial"]): q["correctAnswer"] for q in interleaved}

    data = {
        "subject": "পদার্থবিজ্ঞান",
        "chapterNo": chapter_no,
        "chapter": chapter_name,
        "questions": interleaved,
        "answerBox": answer_box,
    }

    # match original repo convention: commas removed, spaces -> dashes
    canon_name = chapter_name.replace(",", "").replace(" ", "-")
    bank_path = os.path.join(REPO, "files", "Physics", f"ch{nn}-{canon_name}.json")
    with open(bank_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=1)

    out_dir = os.path.join(REPO, "files", "Physics", f"Chapter_{nn}", "mcq")
    files = gen_pdfs.main(chapter_no, chapter_name, bank_path, out_dir, n_pdfs=15)

    # topic distribution report
    dist = Counter(q["topic"] for q in interleaved)
    print(f"[DIST] {chapter_name} (total {len(interleaved)}):")
    for t, n in sorted(dist.items()):
        print(f"    {t}: {n}")

    return files

if __name__ == "__main__":
    build(int(sys.argv[1]), sys.argv[2])
