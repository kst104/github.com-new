#!/usr/bin/env python3
"""블로그·마케팅·쇼츠 작업 허브 (로컬호스트)

- 표준 라이브러리만 사용 (Python 3.8+), 설치할 것 없음
- 127.0.0.1 에만 열림. 다른 기기에서는 각자 이 저장소를 받아 각자 실행
- 자동 깃허브 동기화: 주기적으로 pull(rebase) → 변경 있으면 commit → push
- 노션 동기화(선택): .env 에 NOTION_TOKEN, NOTION_DATABASE_ID 가 있으면 콘텐츠 상태를 노션 보드로 보냄

실행:  python3 hub/server.py --open
"""
import argparse
import datetime as dt
import json
import os
import re
import socket
import subprocess
import sys
import threading
import time
import urllib.error
import urllib.request
import webbrowser
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import parse_qs, urlparse

ROOT = Path(__file__).resolve().parent.parent
HUB = ROOT / "hub"
CONTENT = ROOT / "content"
TEMPLATES = ROOT / "templates"
STATIC = HUB / "static"

STATUSES = ["아이디어", "생성요청", "작성중", "검토", "발행완료"]
CHANNELS = ["블로그", "인스타", "페이스북", "파워링크", "쇼츠"]
CATEGORIES = ["의학/건강", "재테크/투자", "문화/공연", "IT/생산성", "생활/리뷰"]
ENGINES = ["Claude", "OpenAI"]
TEXT_EXT = {".md", ".txt", ".json", ".csv", ".html"}
MAX_GIT_FILE = 50 * 1024 * 1024  # 50MB 넘는 파일은 깃허브 동기화에서 제외
KST = dt.timezone(dt.timedelta(hours=9))


def now_iso():
    return dt.datetime.now(KST).replace(microsecond=0).isoformat()


# ---------------------------------------------------------------- 설정 (.env)
def load_env():
    env = {}
    p = ROOT / ".env"
    if p.exists():
        for line in p.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            k, v = line.split("=", 1)
            env[k.strip()] = v.strip().strip('"').strip("'")
    if env.get("NOTION_API_KEY") and not env.get("NOTION_TOKEN"):
        env["NOTION_TOKEN"] = env["NOTION_API_KEY"]
    for k in ("NOTION_TOKEN", "NOTION_API_KEY", "NOTION_DATABASE_ID", "SYNC_INTERVAL", "HUB_PORT",
              "NOTION_BOARD_URL", "CLAUDE_PROJECT_URL", "GITHUB_URL"):
        if os.environ.get(k):
            env[k] = os.environ[k]
    if env.get("NOTION_API_KEY") and not env.get("NOTION_TOKEN"):
        env["NOTION_TOKEN"] = env["NOTION_API_KEY"]
    return env


def public_config():
    cfg = json.loads((HUB / "config.json").read_text(encoding="utf-8")) if (HUB / "config.json").exists() else {}
    env = load_env()
    for k_env, k_cfg in (("NOTION_BOARD_URL", "notion_board_url"),
                         ("CLAUDE_PROJECT_URL", "claude_project_url"),
                         ("GITHUB_URL", "github_url")):
        if env.get(k_env):
            cfg[k_cfg] = env[k_env]
    cfg["notion_api"] = bool(env.get("NOTION_TOKEN") and env.get("NOTION_DATABASE_ID"))
    cfg["statuses"] = STATUSES
    cfg["channels"] = CHANNELS
    cfg["categories"] = CATEGORIES
    cfg["engines"] = ENGINES
    cfg["host"] = socket.gethostname()
    return cfg


# ---------------------------------------------------------------- 콘텐츠
def safe_path(rel):
    """content/ 안쪽 경로만 허용"""
    p = (ROOT / rel).resolve()
    if CONTENT.resolve() not in p.parents and p != CONTENT.resolve():
        raise ValueError("허용되지 않은 경로")
    return p


def read_meta(folder):
    m = folder / "meta.json"
    meta = {}
    if m.exists():
        try:
            meta = json.loads(m.read_text(encoding="utf-8"))
        except Exception:
            meta = {"_error": "meta.json 을 읽지 못했어요"}
    meta.setdefault("id", folder.name)
    meta.setdefault("title", folder.name)
    meta.setdefault("status", "아이디어")
    meta.setdefault("keyword", "")
    meta.setdefault("channels", [])
    return meta


def write_meta(folder, meta):
    meta["updated"] = now_iso()
    (folder / "meta.json").write_text(json.dumps(meta, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def list_items():
    CONTENT.mkdir(exist_ok=True)
    items = []
    for f in sorted(CONTENT.iterdir(), reverse=True):
        if not f.is_dir() or f.name.startswith("."):
            continue
        meta = read_meta(f)
        files = []
        for x in sorted(f.rglob("*")):
            if x.is_file() and x.name != "meta.json" and not x.name.startswith("."):
                files.append({
                    "path": str(x.relative_to(ROOT)),
                    "name": str(x.relative_to(f)),
                    "size": x.stat().st_size,
                    "text": x.suffix.lower() in TEXT_EXT,
                })
        meta["files"] = files
        meta["folder"] = str(f.relative_to(ROOT))
        items.append(meta)
    return items


def new_item(title, keyword, channels, category="", audience="", engine="Claude"):
    CONTENT.mkdir(exist_ok=True)
    day = dt.datetime.now(KST).strftime("%Y-%m-%d")
    n = 1
    while (CONTENT / f"{day}-{n:02d}").exists():
        n += 1
    folder = CONTENT / f"{day}-{n:02d}"
    folder.mkdir()
    subs = {"{{title}}": title, "{{keyword}}": keyword, "{{date}}": day}
    for tpl in sorted(TEMPLATES.glob("*.md")):
        text = tpl.read_text(encoding="utf-8")
        for k, v in subs.items():
            text = text.replace(k, v)
        (folder / tpl.name).write_text(text, encoding="utf-8")
    meta = {"id": folder.name, "title": title, "keyword": keyword,
            "channels": [c for c in channels if c in CHANNELS],
            "status": "아이디어", "created": now_iso(),
            "category": category if category in CATEGORIES else "", "audience": audience,
            "engine": engine if engine in ENGINES else "Claude"}
    write_meta(folder, meta)
    return meta


# ---------------------------------------------------------------- Git 자동 동기화
class GitSync:
    def __init__(self, interval):
        self.interval = max(30, int(interval))
        self.auto = True
        self.lock = threading.Lock()
        self.last_sync = None
        self.last_result = "아직 동기화하지 않음"
        self.last_error = None
        self.excluded = []
        self.log = []

    def git(self, *args, check=True, timeout=60):
        env = dict(os.environ, GIT_TERMINAL_PROMPT="0", LC_ALL="C")
        r = subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True,
                           timeout=timeout, env=env)
        if check and r.returncode != 0:
            raise RuntimeError((r.stderr or r.stdout).strip() or f"git {' '.join(args)} 실패")
        return r.stdout.strip()

    def is_repo(self):
        try:
            return self.git("rev-parse", "--is-inside-work-tree", check=False) == "true"
        except Exception:
            return False

    def has_remote(self):
        return bool(self.git("remote", check=False))

    def status(self):
        st = {"repo": self.is_repo(), "auto": self.auto, "interval": self.interval,
              "last_sync": self.last_sync, "last_result": self.last_result,
              "last_error": self.last_error, "excluded": self.excluded, "log": self.log[-15:]}
        if not st["repo"]:
            return st
        try:
            st["branch"] = self.git("rev-parse", "--abbrev-ref", "HEAD", check=False)
            st["remote"] = self.git("remote", "get-url", "origin", check=False)
            porcelain = self.git("status", "--porcelain", check=False)
            st["changes"] = [l[3:] for l in porcelain.splitlines() if l.strip()]
            ab = self.git("rev-list", "--left-right", "--count", "HEAD...@{u}", check=False)
            if ab and "\t" in ab:
                a, b = ab.split("\t")
                st["ahead"], st["behind"] = int(a), int(b)
            st["conflict"] = (ROOT / ".git" / "rebase-merge").exists() or (ROOT / ".git" / "rebase-apply").exists()
        except Exception as e:  # noqa
            st["last_error"] = str(e)
        return st

    def _exclude_large(self):
        """50MB 넘는 새 파일은 이 기기에서만 동기화 제외 (.git/info/exclude)"""
        out = self.git("ls-files", "--others", "--exclude-standard", "-z", check=False)
        big = []
        for rel in [x for x in out.split("\0") if x]:
            p = ROOT / rel
            if p.is_file() and p.stat().st_size > MAX_GIT_FILE:
                big.append(rel)
        if big:
            ex = ROOT / ".git" / "info" / "exclude"
            ex.parent.mkdir(parents=True, exist_ok=True)
            cur = ex.read_text(encoding="utf-8") if ex.exists() else ""
            with ex.open("a", encoding="utf-8") as fh:
                for rel in big:
                    line = "/" + rel.replace("\\", "/")
                    if line not in cur:
                        fh.write(line + "\n")
            self.excluded = sorted(set(self.excluded + big))

    def _note(self, msg):
        self.log.append(f"{dt.datetime.now(KST).strftime('%m-%d %H:%M:%S')} {msg}")
        self.log = self.log[-50:]

    def sync(self, reason="자동"):
        if not self.lock.acquire(blocking=False):
            return {"ok": False, "message": "이미 동기화 중이에요"}
        try:
            if not self.is_repo():
                raise RuntimeError("아직 깃 저장소가 아니에요. start.command 를 먼저 실행해 주세요.")
            if (ROOT / ".git" / "rebase-merge").exists() or (ROOT / ".git" / "rebase-apply").exists():
                raise RuntimeError("이전 동기화에서 충돌이 남아 있어요. README의 '충돌 해결'을 봐 주세요.")
            self._exclude_large()
            committed = False
            if self.git("status", "--porcelain", check=False):
                self.git("add", "-A")
                host = socket.gethostname().split(".")[0]
                self.git("commit", "-q", "-m", f"{reason} 동기화 · {host} · {dt.datetime.now(KST).strftime('%Y-%m-%d %H:%M')}")
                committed = True
            pulled = False
            if self.has_remote():
                self.git("fetch", "-q", "origin", timeout=90)
                upstream = self.git("rev-parse", "--abbrev-ref", "@{u}", check=False)
                if not upstream or upstream.startswith("fatal") or "@{u}" in upstream:
                    br = self.git("rev-parse", "--abbrev-ref", "HEAD")
                    if self.git("ls-remote", "--heads", "origin", br, check=False):
                        self.git("branch", "-u", f"origin/{br}")
                        upstream = f"origin/{br}"
                    else:
                        upstream = ""
                if upstream:
                    behind = int(self.git("rev-list", "--count", "HEAD..@{u}", check=False) or 0)
                    if behind:
                        r = subprocess.run(["git", "rebase", "-q", "@{u}"], cwd=ROOT, capture_output=True, text=True,
                                           env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_EDITOR="true"))
                        if r.returncode != 0:
                            subprocess.run(["git", "rebase", "--abort"], cwd=ROOT, capture_output=True)
                            self.auto = False
                            raise RuntimeError("다른 기기와 같은 파일을 고쳐서 충돌이 났어요. 자동 동기화를 멈췄어요. "
                                               "내 변경은 이 기기에 그대로 있어요. '충돌 정리하기'를 누르면 "
                                               "다른 기기 버전을 받고 내 버전은 사본 파일로 남겨요.")
                        pulled = True
                    ahead = int(self.git("rev-list", "--count", "@{u}..HEAD", check=False) or 0)
                    if ahead:
                        self.git("push", "-q", "origin", "HEAD", timeout=120)
                else:
                    br = self.git("rev-parse", "--abbrev-ref", "HEAD")
                    self.git("push", "-q", "-u", "origin", br, timeout=120)
            parts = []
            if committed:
                parts.append("변경 저장")
            if pulled:
                parts.append("다른 기기 변경 받음")
            msg = " · ".join(parts) if parts else "최신 상태"
            self.last_sync, self.last_result, self.last_error = now_iso(), msg, None
            self._note(f"[{reason}] {msg}")
            return {"ok": True, "message": msg}
        except Exception as e:
            err = str(e)
            if "Authentication" in err or "could not read Username" in err or "403" in err:
                err = "깃허브 로그인이 필요해요. 터미널에서 'gh auth login' 후 'gh auth setup-git' 을 실행해 주세요. (" + err[:160] + ")"
            self.last_error = err
            self._note(f"[{reason}] 오류: {err[:200]}")
            return {"ok": False, "message": err}
        finally:
            self.lock.release()

    def resolve(self):
        """충돌 정리: 다른 기기 버전을 기본으로 받고, 내 버전은 '파일명.충돌-기기이름.md' 사본으로 보존"""
        with self.lock:
            try:
                self.git("fetch", "-q", "origin", timeout=90)
                base = self.git("merge-base", "HEAD", "@{u}")
                mine = set(self.git("diff", "--name-only", base, "HEAD").splitlines())
                theirs = set(self.git("diff", "--name-only", base, "@{u}").splitlines())
                both = sorted(x for x in mine & theirs if x)
                saved = {}
                for rel in both:
                    r = subprocess.run(["git", "show", f"HEAD:{rel}"], cwd=ROOT, capture_output=True)
                    if r.returncode == 0:
                        saved[rel] = r.stdout
                r = subprocess.run(["git", "rebase", "-q", "-X", "ours", "@{u}"], cwd=ROOT, capture_output=True, text=True,
                                   env=dict(os.environ, GIT_TERMINAL_PROMPT="0", GIT_EDITOR="true"))
                if r.returncode != 0:
                    subprocess.run(["git", "rebase", "--abort"], cwd=ROOT, capture_output=True)
                    raise RuntimeError("자동 정리에 실패했어요: " + (r.stderr or r.stdout)[:200])
                host = re.sub(r"[^\w\-]", "", socket.gethostname().split(".")[0]) or "this"
                copies = []
                for rel, data in saved.items():
                    p = ROOT / rel
                    if p.exists() and p.read_bytes() == data:
                        continue
                    cp = p.with_name(f"{p.stem}.충돌-{host}{p.suffix}")
                    cp.write_bytes(data)
                    copies.append(str(cp.relative_to(ROOT)))
                if copies:
                    self.git("add", "-A")
                    self.git("commit", "-q", "-m", f"충돌 정리 · {host} 버전 사본 보존")
                self.git("push", "-q", "origin", "HEAD", timeout=120)
                self.auto, self.last_error = True, None
                msg = "충돌 정리 완료" + (f" · 내 버전 사본: {', '.join(copies)}" if copies else "")
                self.last_sync, self.last_result = now_iso(), msg
                self._note("[정리] " + msg)
                return {"ok": True, "message": msg, "copies": copies}
            except Exception as e:
                self.last_error = str(e)
                return {"ok": False, "message": str(e)}

    def loop(self):
        time.sleep(3)
        while True:
            if self.auto:
                self.sync("자동")
            time.sleep(self.interval)


# ---------------------------------------------------------------- 노션 (선택)
NOTION_VERSION = "2022-06-28"


def notion_req(method, path, body=None):
    env = load_env()
    req = urllib.request.Request(
        "https://api.notion.com/v1" + path, method=method,
        data=json.dumps(body).encode("utf-8") if body is not None else None,
        headers={"Authorization": "Bearer " + env["NOTION_TOKEN"],
                 "Notion-Version": NOTION_VERSION, "Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(req, timeout=20) as r:
            return json.loads(r.read().decode("utf-8"))
    except urllib.error.HTTPError as e:
        raise RuntimeError(f"노션 응답 {e.code}: {e.read().decode('utf-8', 'replace')[:300]}")


def notion_push(item_id):
    env = load_env()
    if not (env.get("NOTION_TOKEN") and env.get("NOTION_DATABASE_ID")):
        raise RuntimeError(".env 에 NOTION_API_KEY, NOTION_DATABASE_ID 를 넣으면 쓸 수 있어요")
    folder = CONTENT / item_id
    meta = read_meta(folder)
    cfg = public_config()
    gh = cfg.get("github_url", "")
    props = {
        "제목": {"title": [{"text": {"content": meta["title"][:200]}}]},
        "상태": {"select": {"name": meta["status"]}},
        "키워드": {"rich_text": [{"text": {"content": meta.get("keyword", "")[:500]}}]},
        "채널": {"multi_select": [{"name": c} for c in meta.get("channels", [])]},
        "허브ID": {"rich_text": [{"text": {"content": item_id}}]},
        "수정일": {"date": {"start": meta.get("updated") or now_iso()}},
        "타깃 독자": {"rich_text": [{"text": {"content": meta.get("audience", "")[:500]}}]},
    }
    if meta.get("category") in CATEGORIES:
        props["카테고리"] = {"select": {"name": meta["category"]}}
    if meta.get("engine") in ENGINES:
        props["엔진"] = {"select": {"name": meta["engine"]}}
    if (meta.get("published_url") or "").startswith("http"):
        props["발행 URL"] = {"url": meta["published_url"]}
    if gh:
        props["GitHub"] = {"url": f"{gh.rstrip('/')}/tree/main/content/{item_id}"}
    page_id = meta.get("notion_page_id")
    if not page_id:
        q = notion_req("POST", f"/databases/{env['NOTION_DATABASE_ID']}/query",
                       {"filter": {"property": "허브ID", "rich_text": {"equals": item_id}}, "page_size": 1})
        if q.get("results"):
            page_id = q["results"][0]["id"]
    if page_id:
        notion_req("PATCH", f"/pages/{page_id}", {"properties": props})
    else:
        r = notion_req("POST", "/pages", {"parent": {"database_id": env["NOTION_DATABASE_ID"]}, "properties": props})
        page_id = r["id"]
    if meta.get("notion_page_id") != page_id:
        meta["notion_page_id"] = page_id
        write_meta(folder, meta)
    return page_id


# ---------------------------------------------------------------- HTTP
SYNC = None


class Handler(BaseHTTPRequestHandler):
    server_version = "BlogHub/1.0"

    def log_message(self, fmt, *args):
        pass

    def _host_ok(self):
        host = (self.headers.get("Host") or "").split(":")[0]
        return host in ("127.0.0.1", "localhost")

    def _send(self, code, body, ctype="application/json; charset=utf-8"):
        data = body if isinstance(body, bytes) else (
            json.dumps(body, ensure_ascii=False).encode("utf-8") if not isinstance(body, str) else body.encode("utf-8"))
        self.send_response(code)
        self.send_header("Content-Type", ctype)
        self.send_header("Content-Length", str(len(data)))
        self.send_header("Cache-Control", "no-store")
        self.end_headers()
        self.wfile.write(data)

    def _body(self):
        n = int(self.headers.get("Content-Length") or 0)
        return json.loads(self.rfile.read(n).decode("utf-8")) if n else {}

    def do_GET(self):
        if not self._host_ok():
            return self._send(403, {"error": "localhost 전용"})
        u = urlparse(self.path)
        q = parse_qs(u.query)
        try:
            if u.path in ("/", "/index.html"):
                return self._send(200, (STATIC / "index.html").read_bytes(), "text/html; charset=utf-8")
            if u.path == "/api/config":
                return self._send(200, public_config())
            if u.path == "/api/items":
                return self._send(200, list_items())
            if u.path == "/api/sync":
                return self._send(200, SYNC.status())
            if u.path == "/api/file":
                p = safe_path(q["path"][0])
                if p.suffix.lower() not in TEXT_EXT:
                    return self._send(400, {"error": "텍스트 파일만 열 수 있어요"})
                return self._send(200, {"path": q["path"][0], "content": p.read_text(encoding="utf-8"),
                                        "mtime": p.stat().st_mtime_ns})
            if u.path == "/api/raw":
                p = safe_path(q["path"][0])
                ctype = {".mp4": "video/mp4", ".mov": "video/quicktime", ".png": "image/png", ".jpg": "image/jpeg",
                         ".jpeg": "image/jpeg", ".webp": "image/webp", ".gif": "image/gif", ".mp3": "audio/mpeg"
                         }.get(p.suffix.lower(), "application/octet-stream")
                size = p.stat().st_size
                rng = re.match(r"bytes=(\d*)-(\d*)", self.headers.get("Range") or "")
                if rng and (rng.group(1) or rng.group(2)):
                    if rng.group(1):
                        start = int(rng.group(1))
                        end = min(int(rng.group(2)) if rng.group(2) else size - 1, size - 1)
                    else:
                        start, end = max(0, size - int(rng.group(2))), size - 1
                    if start > end:
                        self.send_response(416)
                        self.send_header("Content-Range", f"bytes */{size}")
                        self.end_headers()
                        return
                    with p.open("rb") as fh:
                        fh.seek(start)
                        data = fh.read(end - start + 1)
                    self.send_response(206)
                    self.send_header("Content-Type", ctype)
                    self.send_header("Accept-Ranges", "bytes")
                    self.send_header("Content-Range", f"bytes {start}-{end}/{size}")
                    self.send_header("Content-Length", str(len(data)))
                    self.end_headers()
                    self.wfile.write(data)
                    return
                return self._send(200, p.read_bytes(), ctype)
            return self._send(404, {"error": "없음"})
        except (KeyError, ValueError, FileNotFoundError) as e:
            return self._send(400, {"error": str(e)})

    def do_POST(self):
        if not self._host_ok() or self.headers.get("X-Hub") != "1":
            return self._send(403, {"error": "허브 화면에서만 요청할 수 있어요"})
        u = urlparse(self.path)
        try:
            b = self._body()
            if u.path == "/api/items":
                title = (b.get("title") or "").strip()
                if not title:
                    return self._send(400, {"error": "제목(주제)을 입력해 주세요"})
                it = new_item(title, (b.get("keyword") or "").strip(), b.get("channels") or [],
                              b.get("category") or "", (b.get("audience") or "").strip(), b.get("engine") or "Claude")
                if public_config()["notion_api"]:
                    try:
                        notion_push(it["id"])
                    except Exception as e:
                        it["notion_error"] = str(e)
                return self._send(200, it)
            m = re.fullmatch(r"/api/items/([\w\-]+)", u.path)
            if m:
                folder = CONTENT / m.group(1)
                if not folder.is_dir():
                    return self._send(404, {"error": "콘텐츠가 없어요"})
                meta = read_meta(folder)
                for k in ("title", "keyword", "status", "channels", "published_url", "category", "audience", "engine"):
                    if k in b:
                        meta[k] = b[k]
                if meta["status"] not in STATUSES:
                    return self._send(400, {"error": "상태 값이 올바르지 않아요"})
                write_meta(folder, meta)
                note = None
                if public_config()["notion_api"]:
                    try:
                        notion_push(folder.name)
                        note = "노션에도 반영했어요"
                    except Exception as e:
                        note = f"노션 반영 실패: {e}"
                return self._send(200, {"ok": True, "notion": note})
            if u.path == "/api/file":
                p = safe_path(b["path"])
                if p.suffix.lower() not in TEXT_EXT:
                    return self._send(400, {"error": "텍스트 파일만 저장할 수 있어요"})
                base = b.get("base_mtime")
                if base and p.exists() and not b.get("force") and p.stat().st_mtime_ns != int(base):
                    return self._send(409, {"error": "열어둔 사이에 이 파일이 바뀌었어요 (다른 기기에서 동기화됐을 수 있어요)"})
                p.parent.mkdir(parents=True, exist_ok=True)
                p.write_text(b["content"], encoding="utf-8")
                return self._send(200, {"ok": True, "saved": now_iso(), "mtime": p.stat().st_mtime_ns})
            if u.path == "/api/sync":
                return self._send(200, SYNC.sync("수동"))
            if u.path == "/api/sync/resolve":
                return self._send(200, SYNC.resolve())
            if u.path == "/api/sync/auto":
                SYNC.auto = bool(b.get("enabled"))
                if SYNC.auto:
                    SYNC.last_error = None
                return self._send(200, SYNC.status())
            if u.path == "/api/notion/push":
                return self._send(200, {"ok": True, "page_id": notion_push(b["id"])})
            if u.path == "/api/open":
                p = safe_path(b["path"])
                opener = "open" if sys.platform == "darwin" else ("explorer" if os.name == "nt" else "xdg-open")
                subprocess.Popen([opener, str(p)])
                return self._send(200, {"ok": True})
            return self._send(404, {"error": "없음"})
        except Exception as e:
            return self._send(400, {"ok": False, "error": str(e)})


def main():
    global SYNC
    env = load_env()
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=int(env.get("HUB_PORT", 8787)))
    ap.add_argument("--open", action="store_true", help="브라우저로 열기")
    ap.add_argument("--no-auto-sync", action="store_true")
    args = ap.parse_args()

    url = f"http://localhost:{args.port}"
    s = socket.socket()
    try:
        if s.connect_ex(("127.0.0.1", args.port)) == 0:
            print(f"이미 실행 중이에요 → {url}")
            if args.open:
                webbrowser.open(url)
            return
    finally:
        s.close()

    SYNC = GitSync(env.get("SYNC_INTERVAL", 120))
    SYNC.auto = not args.no_auto_sync
    threading.Thread(target=SYNC.loop, daemon=True).start()

    httpd = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print(f"작업 허브 실행 중 → {url}   (끄려면 이 창에서 Ctrl+C)")
    print(f"자동 동기화: {'켜짐' if SYNC.auto else '꺼짐'} · {SYNC.interval}초마다")
    if args.open:
        threading.Timer(0.8, lambda: webbrowser.open(url)).start()
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n종료 전 마지막 동기화 중…")
        print(SYNC.sync("종료")["message"])


if __name__ == "__main__":
    main()
