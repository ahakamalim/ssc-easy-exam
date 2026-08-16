#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Upload all 195 Physics MCQ PDF entries to Firestore (concurrent)."""
import urllib.request, json, time
from concurrent.futures import ThreadPoolExecutor, as_completed

APIKEY = "AIzaSyDgZ6oG1khblwfYpfhPWkwctbyQ2EjaSYk"
PROJECT = "ssc-easy-exam-for-tutor"
BASE = f"https://firestore.googleapis.com/v1/projects/{PROJECT}/databases/(default)/documents"
SUBJECT = "পদার্থ বিজ্ঞান"
GH = "https://cdn.jsdelivr.net/gh/ahakamalim/ssc-easy-exam@main/files/Physics"

BN = "০১২৩৪৫৬৭৮৯"
def bn(n): return "".join(BN[int(c)] for c in str(n))

FULL = {1:"ভৌত রাশি ও পরিমাপ",2:"গতি",3:"বল",4:"কাজ, ক্ষমতা ও শক্তি",5:"পদার্থের অবস্থা ও চাপ",
        6:"বস্তুর উপর তাপের প্রভাব",7:"তরঙ্গ ও শব্দ",8:"আলোর প্রতিফলন",9:"আলোর প্রতিসরণ",
        10:"স্থির তড়িৎ",11:"চল তড়িৎ",12:"চুম্বকত্ব",13:"আধুনিক পদার্থবিজ্ঞান ও ইলেকট্রনিক্স"}

def req(method, path, body=None):
    url = f"{BASE}/{path}?key={APIKEY}"
    data = json.dumps(body).encode() if body is not None else None
    r = urllib.request.Request(url, data=data, method=method,
        headers={"Content-Type":"application/json","User-Agent":"curl/8"})
    try:
        with urllib.request.urlopen(r, timeout=25) as resp:
            return resp.status, resp.read().decode()
    except urllib.error.HTTPError as e:
        return e.code, e.read().decode()
    except Exception as e:
        return -1, repr(e)

def get_all(path):
    status, body = req("GET", path)
    if status != 200:
        return []
    return json.loads(body).get("documents", [])

def bn_to_int(s):
    return int("".join(str(BN.index(c)) for c in s))

# map chapter number -> exact string
chap_map = {}
for d in get_all("chapters"):
    f = d["fields"]
    if f.get("subject",{}).get("stringValue","") != SUBJECT: continue
    ch = f.get("chapter",{}).get("stringValue","")
    toks = ch.split()
    if len(toks) >= 2:
        try: chap_map[bn_to_int(toks[1])] = ch
        except: pass
print("chapter map keys:", sorted(chap_map))

# collect old docs
old_docs = []
for d in get_all("files"):
    f = d["fields"]
    if f.get("subject",{}).get("stringValue","") != SUBJECT: continue
    if f.get("type",{}).get("stringValue","") != "MCQ": continue
    ch = f.get("chapter",{}).get("stringValue","")
    toks = ch.split(); n=None
    if len(toks) >= 2:
        try: n = bn_to_int(toks[1])
        except: n=None
    if n is not None and 1 <= n <= 13:
        old_docs.append(d)
print("old docs to delete:", len(old_docs))

now = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
tasks = []
for n in range(1,14):
    ch_str = chap_map.get(n)
    if not ch_str: continue
    for s in range(1,16):
        fn = f"Physics_Ch{n:02d}_MCQ_Set_{s:02d}.pdf"
        doc_id = f"phymcq_{n:02d}_{s:02d}"
        url = f"{GH}/Chapter_{n:02d}/mcq/{fn}"
        title = f"এমসিকিউ সেট {bn(s)} — {FULL[n]}"
        body = {"fields":{
            "subject":{"stringValue":SUBJECT},
            "chapter":{"stringValue":ch_str},
            "type":{"stringValue":"MCQ"},
            "title":{"stringValue":title},
            "fileName":{"stringValue":fn},
            "url":{"stringValue":url},
            "createdAt":{"timestampValue":now},
        }}
        tasks.append(("PATCH", f"files/{doc_id}", body))

ok = 0; fail = []
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = {ex.submit(req, m, p, b): p for m,p,b in tasks}
    for i, fu in enumerate(as_completed(futs), 1):
        st, resp = fu.result()
        if st == 200: ok += 1
        else: fail.append((futs[fu], st, resp[:150]))
        if i % 25 == 0 or i == len(tasks):
            print(f"  wrote {i}/{len(tasks)} (ok={ok})")
print("CREATED:", ok, "/", len(tasks))
for f in fail[:10]: print("FAIL:", f)

# delete old docs (concurrent)
del_ok = 0; del_fail = []
del_tasks = [d["name"].split("/documents/")[1] for d in old_docs]
with ThreadPoolExecutor(max_workers=16) as ex:
    futs = {ex.submit(req, "DELETE", p): p for p in del_tasks}
    for fu in as_completed(futs):
        st, resp = fu.result()
        if st == 200: del_ok += 1
        else: del_fail.append((futs[fu], st, resp[:150]))
print("DELETED:", del_ok, "/", len(del_tasks))
for f in del_fail[:10]: print("DELFAIL:", f)
print("DONE")
