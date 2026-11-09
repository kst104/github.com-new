#!/usr/bin/env python3
"""7070 의학서적 위키 → 근거 검색 색인

localhost:7070(나의 위키)의 '의학서적' 카테고리 목차와 본문 페이지를 읽어
이 기기에만 저장되는 검색 색인(hub/.medref.sqlite, 깃허브에 안 올라감)을 만듭니다.
7070 자체 검색(/api/search)이 고장 나 있어도 쓸 수 있게 따로 색인합니다.

CLI:
  python3 hub/medref.py index                      # 색인 만들기/다시 만들기
  python3 hub/medref.py search "diabetic ketoacidosis" [--book tintinalli] [--limit 5]
  python3 hub/medref.py status
"""
import html as htmlmod
import json
import os
import re
import sqlite3
import sys
import threading
import time
import urllib.parse
import urllib.request
from pathlib import Path

HUB = Path(__file__).resolve().parent
DB_PATH = HUB / ".medref.sqlite"


def base_url():
    env = os.environ.get("MEDWIKI_URL")
    if not env:
        p = HUB.parent / ".env"
        if p.exists():
            for line in p.read_text(encoding="utf-8").splitlines():
                if line.strip().startswith("MEDWIKI_URL="):
                    env = line.split("=", 1)[1].strip().strip('"\'')
    return (env or "http://localhost:7070").rstrip("/")


# 7070 위키 index에 적힌 정보 그대로 (출판사·연도는 위키에 적힌 것만)
BOOK_NOTES = {
    "harrisons": "McGraw-Hill Professional, 2008",
}


def fetch(url, timeout=30):
    req = urllib.request.Request(url, headers={"User-Agent": "content-hub-medref/1.0"})
    with urllib.request.urlopen(req, timeout=timeout) as r:
        raw = r.read()
        charset = r.headers.get_content_charset() or "utf-8"
    return raw.decode(charset, errors="replace")


TAG_BREAK = re.compile(r"<\s*(br|/p|/div|/li|/tr|/h\d|/table|p|li|tr|h\d)\b[^>]*>", re.I)


def html_to_text(src):
    s = re.sub(r"<!--.*?-->", " ", src, flags=re.S)
    s = re.sub(r"<(script|style|noscript)\b.*?</\1\s*>", " ", s, flags=re.S | re.I)
    s = TAG_BREAK.sub("\n", s)
    s = re.sub(r"<[^>]+>", " ", s)
    s = htmlmod.unescape(s).replace("\xa0", " ")
    s = re.sub(r"[ \t\r\f\v]+", " ", s)
    s = re.sub(r"\n\s*\n+", "\n", s)
    # 인쇄용 페이지 머리말 제거
    s = re.sub(r"^.*?(Note: Large images and tables on this page may necessitate printing in landscape mode\.)", "", s, count=1, flags=re.S)
    s = re.sub(r"Copyright\s*(©|\(c\))[^\n]*", " ", s, flags=re.I)
    s = re.sub(r"^[\s|]+", "", s)
    return s.strip()


def discover_books(base):
    """의학서적 index에서 *_toc 링크와 책 제목을 찾음"""
    idx = fetch(base + "/medwiki/index")
    books = []
    seen = set()
    for m in re.finditer(r'<a href="/medwiki/(\w+)_toc">([^<]+)</a>', idx):
        key, title = m.group(1), htmlmod.unescape(m.group(2)).strip()
        if key in seen or title.endswith(".md"):
            continue
        seen.add(key)
        books.append({"key": key, "title": title, "note": BOOK_NOTES.get(key, "")})
    return books


CHAPTER_RE = re.compile(r"^(CHAPTER\s+\d+|Chapter\s+\d+|\d+\.\s)", re.I)


def parse_toc(base, key):
    toc = fetch(f"{base}/medwiki/{key}_toc")
    entries, chapter = [], ""
    for m in re.finditer(r'<a[^>]*href="(/doc/[^"#]+)"[^>]*>(.*?)</a>', toc, flags=re.S):
        href, label = m.group(1), htmlmod.unescape(re.sub(r"<[^>]+>", "", m.group(2))).strip()
        if not href.lower().endswith((".htm", ".html")):
            continue
        if CHAPTER_RE.match(label):
            chapter = label
        part = ""
        segs = [urllib.parse.unquote(x) for x in href.split("/")[4:-1]]  # /doc/medical/<book>/<...>/file
        if segs and segs != ["HTML"]:
            part = " › ".join(segs)
        entries.append({"href": href, "section": label, "chapter": chapter or label, "part": part})
    return entries


def connect():
    con = sqlite3.connect(DB_PATH, check_same_thread=False)
    con.execute("PRAGMA journal_mode=WAL")
    return con


def has_fts(con):
    r = con.execute("SELECT name FROM sqlite_master WHERE name='docs_fts'").fetchone()
    return bool(r)


class Indexer:
    def __init__(self):
        self.lock = threading.Lock()
        self.state = {"state": "idle", "done": 0, "total": 0, "error": None, "started": None, "finished": None}

    def status(self):
        st = dict(self.state)
        st["base_url"] = base_url()
        st["db"] = DB_PATH.exists()
        if DB_PATH.exists() and st["state"] != "running":
            try:
                con = connect()
                st["books"] = json.loads(con.execute("SELECT v FROM meta WHERE k='books'").fetchone()[0])
                st["pages"] = con.execute("SELECT COUNT(*) FROM docs").fetchone()[0]
                st["built"] = con.execute("SELECT v FROM meta WHERE k='built'").fetchone()[0]
                st["fts"] = has_fts(con)
                con.close()
            except Exception as e:  # noqa
                st["db_error"] = str(e)
        return st

    def start(self):
        if self.state["state"] == "running":
            return False
        threading.Thread(target=self.build, daemon=True).start()
        return True

    def build(self):
        with self.lock:
            self.state.update(state="running", done=0, total=0, error=None,
                              started=time.strftime("%Y-%m-%dT%H:%M:%S"), finished=None)
            tmp = DB_PATH.with_suffix(".tmp")
            try:
                base = base_url()
                books = discover_books(base)
                if not books:
                    raise RuntimeError("7070 의학서적 목록에서 책을 찾지 못했어요 (/medwiki/index)")
                plan = []
                for b in books:
                    for e in parse_toc(base, b["key"]):
                        plan.append((b, e))
                self.state["total"] = len(plan)
                if tmp.exists():
                    tmp.unlink()
                con = sqlite3.connect(tmp)
                con.execute("CREATE TABLE meta (k TEXT PRIMARY KEY, v TEXT)")
                con.execute("""CREATE TABLE docs (id INTEGER PRIMARY KEY, book TEXT, book_title TEXT,
                               chapter TEXT, section TEXT, part TEXT, url TEXT, body TEXT)""")
                fts = True
                try:
                    con.execute("""CREATE VIRTUAL TABLE docs_fts USING fts5(section, body,
                                   content='docs', content_rowid='id', tokenize='porter unicode61')""")
                except sqlite3.OperationalError:
                    fts = False
                failed = 0
                for i, (b, e) in enumerate(plan, 1):
                    try:
                        body = html_to_text(fetch(base + e["href"]))
                    except Exception:
                        failed += 1
                        body = ""
                    if body:
                        cur = con.execute("INSERT INTO docs (book, book_title, chapter, section, part, url, body) VALUES (?,?,?,?,?,?,?)",
                                          (b["key"], b["title"], e["chapter"], e["section"], e["part"], e["href"], body))
                        if fts:
                            con.execute("INSERT INTO docs_fts (rowid, section, body) VALUES (?,?,?)",
                                        (cur.lastrowid, e["section"], body))
                    self.state["done"] = i
                    if i % 50 == 0:
                        con.commit()
                con.execute("INSERT INTO meta VALUES ('books', ?)", (json.dumps(books, ensure_ascii=False),))
                con.execute("INSERT INTO meta VALUES ('built', ?)", (time.strftime("%Y-%m-%d %H:%M"),))
                con.execute("INSERT INTO meta VALUES ('base', ?)", (base,))
                con.commit()
                con.close()
                os.replace(tmp, DB_PATH)
                for ext in ("-wal", "-shm"):
                    p = Path(str(DB_PATH) + ext)
                    if p.exists():
                        p.unlink()
                self.state.update(state="done", finished=time.strftime("%Y-%m-%dT%H:%M:%S"),
                                  error=(f"{failed}쪽은 읽지 못했어요" if failed else None))
            except Exception as ex:
                self.state.update(state="error", error=f"{type(ex).__name__}: {ex}")
                if tmp.exists():
                    try:
                        tmp.unlink()
                    except Exception:
                        pass


HANGUL = re.compile(r"[가-힣]")


def fts_query(q):
    q = q.strip()
    if re.search(r'"|\bOR\b|\bNEAR\b', q):
        return q
    toks = re.findall(r"[A-Za-z0-9][A-Za-z0-9\-']*\*?", q)
    return " ".join('"%s"%s' % (t.rstrip("*"), "*" if t.endswith("*") else "") for t in toks)


def make_link(base, href, snippet):
    """원문 링크 + 텍스트 조각(#:~:text=) — 누르면 7070 페이지에서 그 단어 위치로 이동"""
    frag = ""
    i = snippet.find("[[")
    tail = snippet[i:] if i >= 0 else snippet
    toks = []
    for t in tail.replace("[[", "").replace("]]", "").split():
        if re.fullmatch(r"[A-Za-z0-9][A-Za-z0-9\-]*", t):
            toks.append(t)
            if len(toks) == 5:
                break
        else:
            break
    if len(toks) >= 2:
        frag = "#:~:text=" + urllib.parse.quote(" ".join(toks)).replace("-", "%2D")
    elif toks and len(toks[0]) >= 5:
        frag = "#:~:text=" + urllib.parse.quote(toks[0]).replace("-", "%2D")
    return base + href + frag


def search(q, book=None, limit=8):
    if not DB_PATH.exists():
        return {"ok": False, "error": "아직 색인이 없어요. '색인 만들기'를 먼저 눌러 주세요.", "results": []}
    if HANGUL.search(q) and not re.search(r"[A-Za-z]{3,}", q):
        return {"ok": False, "error": "7070 의학서적은 영어 원서예요. 영어 검색어로 찾아 주세요 (예: 당뇨 → diabetes, 케톤산증 → ketoacidosis).", "results": []}
    con = connect()
    base = con.execute("SELECT v FROM meta WHERE k='base'").fetchone()[0]
    rows = []
    limit = max(1, min(int(limit or 8), 30))
    if has_fts(con):
        fq = fts_query(q)
        if not fq:
            return {"ok": False, "error": "검색어가 비어 있어요", "results": []}
        sql = """SELECT d.book, d.book_title, d.chapter, d.section, d.part, d.url,
                        snippet(docs_fts, 1, '[[', ']]', ' … ', 32), bm25(docs_fts, 4.0, 1.0)
                 FROM docs_fts JOIN docs d ON d.id = docs_fts.rowid
                 WHERE docs_fts MATCH ? {book} ORDER BY bm25(docs_fts, 4.0, 1.0) LIMIT ?"""
        args = [fq]
        sql = sql.format(book="AND d.book = ?" if book else "")
        if book:
            args.append(book)
        args.append(limit)
        try:
            rows = con.execute(sql, args).fetchall()
        except sqlite3.OperationalError:
            fq = fts_query(re.sub(r'["()]', " ", q).replace(" OR ", " ").replace(" NEAR ", " "))
            args[0] = fq
            rows = con.execute(sql, args).fetchall()
    else:  # FTS5가 없는 파이썬일 때: 단순 검색
        terms = re.findall(r"[A-Za-z0-9\-]+", q)
        if not terms:
            return {"ok": False, "error": "검색어가 비어 있어요", "results": []}
        where = " AND ".join(["body LIKE ?"] * len(terms)) + (" AND book = ?" if book else "")
        args = [f"%{t}%" for t in terms] + ([book] if book else []) + [limit]
        for r in con.execute(f"SELECT book, book_title, chapter, section, part, url, body FROM docs WHERE {where} LIMIT ?", args):
            body = r[6]
            i = body.lower().find(terms[0].lower())
            snip = body[max(0, i - 160): i + 200].replace(body[i:i + len(terms[0])], "[[" + body[i:i + len(terms[0])] + "]]", 1)
            rows.append((*r[:6], " … " + snip + " … ", 0))
    con.close()
    out = []
    for book_key, title, chapter, section, part, url, snip, score in rows:
        snip = re.sub(r"\s+", " ", snip).strip()
        plain = snip.replace("[[", "").replace("]]", "")
        out.append({
            "book": book_key, "book_title": title, "chapter": chapter, "section": section, "part": part,
            "url": make_link(base, url, snip), "page_url": base + url,
            "snippet": snip, "excerpt": plain, "score": round(score, 3),
        })
    return {"ok": True, "query": q, "results": out}


def footnote(r, n):
    loc = r["chapter"] if r["section"] == r["chapter"] else f"{r['chapter']} › {r['section']}"
    ex = r["excerpt"].strip(" …")
    if len(ex) > 220:
        ex = ex[:220].rsplit(" ", 1)[0] + " …"
    return f'[^m{n}]: **{r["book_title"]}** — {loc} · 7070 원문: <{r["url"]}> · 발췌: "{ex}"'


INDEXER = Indexer()

if __name__ == "__main__":
    import argparse
    ap = argparse.ArgumentParser()
    ap.add_argument("cmd", choices=["index", "search", "status"])
    ap.add_argument("query", nargs="?")
    ap.add_argument("--book")
    ap.add_argument("--limit", type=int, default=5)
    a = ap.parse_args()
    if a.cmd == "index":
        print(f"색인 중… ({base_url()})")
        t = threading.Thread(target=INDEXER.build)
        t.start()
        while t.is_alive():
            time.sleep(2)
            s = INDEXER.state
            print(f"\r  {s['done']}/{s['total']}", end="", flush=True)
        print()
        print(json.dumps(INDEXER.status(), ensure_ascii=False, indent=2))
    elif a.cmd == "status":
        print(json.dumps(INDEXER.status(), ensure_ascii=False, indent=2))
    else:
        res = search(a.query or "", a.book, a.limit)
        if not res["ok"]:
            print(res["error"])
            sys.exit(1)
        if not res["results"]:
            print(f"7070 의학서적에 없음: '{a.query}' → 본문에 쓰면 ⚠️[7070 없음] 표시")
        for i, r in enumerate(res["results"], 1):
            loc = r["chapter"] if r["section"] == r["chapter"] else f"{r['chapter']} › {r['section']}"
            print(f"\n({i}) {r['book_title']} — {loc}")
            print(f"    {r['snippet']}")
            print(f"    {r['url']}")
            print("    " + footnote(r, i))
