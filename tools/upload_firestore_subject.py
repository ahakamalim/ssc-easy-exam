#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload one subject chapter's MCQ + CQ PDF entries to Firestore."""
import urllib.request, json, time, sys
from concurrent.futures import ThreadPoolExecutor, as_completed
import subj_config

APIKEY = "AIzaSyDgZ6oG1khblwfYpfhPWkwctbyQ2EjaSYk"
PROJECT = "ssc-easy-exam-for-tutor"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
GH = "https://cdn.jsdelivr.net/gh/ahakamalim/ssc-easy-exam@main/files"
BN = "০১২৩৪৫৬৭৮৯"
def bn(n): return "".join(BN[int(c)] for c in str(n))

def req(method, path, body=None):
    url = f"{BASE}/{path}?key={APIKEY}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"Content-Type":"application/json","User-Agent":"curl/8"})
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.status
    except urllib.error.HTTPError as e:
        return e.code
    except Exception:
        return -1

def upload(subj, chapter_no, n_mcq=15, n_cq=1):
    cfg = subj_config.SUBJECTS[subj]
    code = cfg["code"]; nn = f"{chapter_no:02d}"
    fs_subject = cfg["firestore_subject"]
    chapter_str = cfg["chapters"][chapter_no]
    short = cfg["short"][chapter_no]
    now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    tasks = []
    for s in range(1, n_mcq+1):
        fn = f"{code}_Ch{nn}_MCQ_Set_{s:02d}.pdf"
        doc_id = f"{subj}mcq_{nn}_{s:02d}"
        url = f"{GH}/{code}/Chapter_{nn}/mcq/{fn}"
        title = f"এমসিকিউ সেট {bn(s)} — {short}"
        tasks.append((doc_id, {"fields":{
            "subject":{"stringValue":fs_subject},
            "chapter":{"stringValue":chapter_str},
            "type":{"stringValue":"MCQ"},
            "title":{"stringValue":title},
            "fileName":{"stringValue":fn},
            "url":{"stringValue":url},
            "createdAt":{"timestampValue":now},
        }}))
    for s in range(1, n_cq+1):
        fn = f"{code}_Ch{nn}_CQ_{s:02d}.pdf"
        doc_id = f"{subj}cq_{nn}_{s:02d}"
        url = f"{GH}/{code}/Chapter_{nn}/cq/{fn}"
        title = f"সৃজনশীল প্রশ্ন — {short}"
        tasks.append((doc_id, {"fields":{
            "subject":{"stringValue":fs_subject},
            "chapter":{"stringValue":chapter_str},
            "type":{"stringValue":"CQ"},
            "title":{"stringValue":title},
            "fileName":{"stringValue":fn},
            "url":{"stringValue":url},
            "createdAt":{"timestampValue":now},
        }}))

    ok = 0; fail = []
    with ThreadPoolExecutor(max_workers=12) as ex:
        futs = {ex.submit(req, "PATCH", f"files/{di}", b): di for di, b in tasks}
        for fu in as_completed(futs):
            st = fu.result()
            if st == 200: ok += 1
            else: fail.append((futs[fu], st))
    print(f"[FIRESTORE] {code} ch{nn}: {ok}/{len(tasks)} docs written")
    for f in fail: print("  FAIL:", f)

if __name__ == "__main__":
    upload(sys.argv[1], int(sys.argv[2]))
