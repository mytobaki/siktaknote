"""식탁노트 카드 이미지 생성기.

content/*.md 앞부분(front matter)의 `cards:` 목록을 읽어
assets/cards/<slug>-<id>.png (1200x675) 로 그린다.

카드 종류
  title   : title, sub
  steps   : title, steps[{head, note}]
  columns : title, cols[{head, value?, lines[], tone? (good|mid|bad)}]
  timeline: title, items[{time, head, note?}]   (5줄 이하, 한 줄씩)
로컬 이야기 글은 section·region 이 카드 상단 라벨에 들어간다.
"""
import html
import pathlib
import sys

from playwright.sync_api import sync_playwright

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from content import load_posts  # noqa: E402

OUT = ROOT / "assets" / "cards"
W, H = 1200, 675

BASE_CSS = """
:root{
  --bg:#fafaf9; --ink:#141414; --muted:#6e6e6e; --line:#e4e4e4;
  --accent:#141414; --sage:#f0f0ef; --paper:#ffffff;
  --good:#141414; --good-bg:#f0f0ef;
  --mid:#6e6e6e;  --mid-bg:#f6f6f5;
  --bad:#9b2c2c;  --bad-bg:#f8eeee;
  --serif:'Noto Sans CJK KR', sans-serif;
  --sans:'Noto Sans CJK KR', sans-serif;
}
*{box-sizing:border-box;margin:0;padding:0}
html,body{width:%dpx;height:%dpx;overflow:hidden}
body{background:var(--bg);color:var(--ink);font-family:var(--sans);
  position:relative;padding:56px 72px 52px;display:flex;flex-direction:column;word-break:keep-all;overflow-wrap:break-word}
.top{display:flex;justify-content:space-between;align-items:center;margin-bottom:30px}
.mark{font-family:var(--sans);font-weight:700;font-size:24px;letter-spacing:.32em}
.mark span{color:var(--accent)}
.eyebrow{font-size:18px;font-weight:500;color:var(--ink);background:transparent;border:1.5px solid var(--ink);
  padding:6px 16px;border-radius:2px;letter-spacing:.14em}
.foot{position:absolute;right:72px;bottom:34px;font-size:19px;color:var(--muted);letter-spacing:.03em}
h1{font-family:var(--sans);font-weight:700;letter-spacing:-.035em;line-height:1.22}
""" % (W, H)

TITLE_CSS = """
.plate{position:absolute;right:-170px;top:50%;width:620px;height:620px;transform:translateY(-44%);
  border-radius:50%;border:1.5px solid #e2e2e1;}
.plate::before{content:"";position:absolute;inset:48px;border-radius:50%;border:1.5px solid #e2e2e1;background:#f3f3f2}
.plate::after{content:"";position:absolute;inset:150px;border-radius:50%;background:#ebebea}
.body{flex:1;display:flex;flex-direction:column;justify-content:center;max-width:760px;position:relative;z-index:1}
.body h1{font-size:76px;margin-bottom:28px}
.body p{font-size:32px;color:var(--muted);line-height:1.5}
.rule{width:56px;height:3px;background:var(--accent);margin-bottom:32px}
"""

STEPS_CSS = """
h1.t{font-size:52px;margin-bottom:8px}
.stage{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:30px}
.row{display:flex;align-items:stretch;gap:0}
.step{flex:1;background:var(--paper);border:1.5px solid var(--line);border-radius:6px;
  padding:32px 26px 36px;display:flex;flex-direction:column;gap:16px}
.num{width:64px;height:64px;border-radius:50%;background:var(--accent);color:#fff;
  font-family:var(--serif);font-weight:700;font-size:34px;display:flex;align-items:center;justify-content:center}
.step b{font-size:var(--hs);line-height:1.3;font-weight:700}
.step span{font-size:var(--ns);color:var(--muted);line-height:1.45}
.arrow{width:44px;display:flex;align-items:center;justify-content:center;color:var(--accent);font-size:34px;font-weight:700}
"""

COLS_CSS = """
h1.t{font-size:52px;margin-bottom:8px}
.stage{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:30px}
.grid{display:grid;gap:22px}
.col{background:var(--paper);border:1.5px solid var(--line);border-radius:6px;overflow:hidden;display:flex;flex-direction:column}
.col .hd{padding:20px 26px;font-size:var(--hs);font-weight:700;background:#f3f3f2}
.col.good .hd{background:var(--good-bg);color:var(--good)}
.col.mid .hd{background:var(--mid-bg);color:var(--mid)}
.col.bad .hd{background:var(--bad-bg);color:var(--bad)}
.col .bd{padding:24px 26px 30px;display:flex;flex-direction:column;gap:14px}
.col .val{font-family:var(--serif);font-weight:700;font-size:var(--vs);color:var(--accent);line-height:1.2;margin-bottom:4px}
.col.bad .val{color:var(--bad)} .col.mid .val{color:var(--mid)}
.col ul{list-style:none;display:flex;flex-direction:column;gap:10px}
.col li{font-size:var(--ls);line-height:1.4;padding-left:20px;position:relative}
.col li::before{content:"";position:absolute;left:0;top:.62em;width:8px;height:8px;border-radius:50%;background:#bdbdbd}
.col.good li::before{background:var(--good)} .col.mid li::before{background:var(--mid)} .col.bad li::before{background:var(--bad)}
"""

TIMELINE_CSS = """
h1.t{font-size:52px;margin-bottom:8px}
.stage{flex:1;display:flex;flex-direction:column;justify-content:center;padding-bottom:30px}
.tl{display:flex;flex-direction:column;gap:12px}
.tr{display:flex;align-items:center;gap:22px;background:var(--paper);border:1.5px solid var(--line);
  border-radius:6px;padding:12px 26px 12px 14px}
.tt{flex:none;min-width:176px;text-align:center;background:var(--accent);color:#fff;border-radius:3px;
  font-family:var(--serif);font-weight:700;font-size:30px;padding:8px 14px}
.tx{font-size:31px;font-weight:700;white-space:nowrap}
.tn{font-size:26px;color:var(--muted);margin-left:10px;font-weight:400}
"""

e = html.escape


def eyebrow_label(post):
    if post.get("section"):
        return " · ".join(x for x in [post["section"], post.get("region")] if x)
    return post["category"]


def frame(post, inner, css):
    return f"""<!doctype html><html lang="ko"><head><meta charset="utf-8">
<style>{BASE_CSS}{css}</style></head><body>
<div class="top"><div class="mark">식탁<span>노트</span></div><div class="eyebrow">{e(eyebrow_label(post))}</div></div>
{inner}
<div class="foot">siktaknote.com</div>
</body></html>"""


def render_title(post, c):
    inner = f"""<div class="plate"></div>
<div class="body"><div class="rule"></div><h1>{e(c['title'])}</h1><p>{e(c.get('sub', ''))}</p></div>"""
    return frame(post, inner, TITLE_CSS)


def render_steps(post, c):
    steps = c["steps"]
    n = len(steps)
    hs, ns = (38, 28) if n <= 3 else (33, 25) if n == 4 else (28, 22)
    parts = []
    for i, s in enumerate(steps, 1):
        parts.append(
            f'<div class="step"><div class="num">{i}</div><b>{e(s["head"])}</b>'
            f'<span>{e(s.get("note", ""))}</span></div>'
        )
        if i < n:
            parts.append('<div class="arrow">→</div>')
    tight = ".step{padding:26px 16px 28px}.arrow{width:28px;font-size:28px}.num{width:54px;height:54px;font-size:28px}" if n >= 5 else ""
    inner = f'<h1 class="t">{e(c["title"])}</h1><div class="stage"><div class="row" style="--hs:{hs}px;--ns:{ns}px">{"".join(parts)}</div></div>'
    return frame(post, inner, STEPS_CSS + tight)


def render_columns(post, c):
    cols = c["cols"]
    n = len(cols)
    sizes = {2: (38, 52, 32), 3: (34, 46, 29), 4: (30, 38, 26)}[min(max(n, 2), 4)]
    hs, vs, ls = sizes
    items = []
    for col in cols:
        tone = col.get("tone", "")
        val = f'<div class="val">{e(col["value"])}</div>' if col.get("value") else ""
        lis = "".join(f"<li>{e(x)}</li>" for x in col.get("lines", []))
        items.append(f'<div class="col {tone}"><div class="hd">{e(col["head"])}</div><div class="bd">{val}<ul>{lis}</ul></div></div>')
    inner = (
        f'<h1 class="t">{e(c["title"])}</h1>'
        f'<div class="stage"><div class="grid" style="grid-template-columns:repeat({n},1fr);--hs:{hs}px;--vs:{vs}px;--ls:{ls}px">{"".join(items)}</div></div>'
    )
    return frame(post, inner, COLS_CSS)


def render_timeline(post, c):
    rows = []
    for it in c["items"]:
        note = f'<span class="tn">{e(it["note"])}</span>' if it.get("note") else ""
        rows.append(f'<div class="tr"><div class="tt">{e(it["time"])}</div><div class="tx">{e(it["head"])}{note}</div></div>')
    tight = (".tl{gap:8px}.tr{padding:7px 22px 7px 10px;border-radius:14px}.tt{font-size:25px;padding:5px 12px;min-width:150px}"
             ".tx{font-size:28px}.tn{font-size:23px}") if len(c["items"]) >= 5 else ""
    inner = f'<h1 class="t">{e(c["title"])}</h1><div class="stage"><div class="tl">{"".join(rows)}</div></div>'
    return frame(post, inner, TIMELINE_CSS + tight)


RENDER = {"title": render_title, "steps": render_steps, "columns": render_columns, "timeline": render_timeline}


def card_alt(c):
    """카드에 적힌 글을 한 줄로 — 이미지 대체 텍스트와 검색용."""
    bits = [c["title"]]
    if c["type"] == "title":
        bits.append(c.get("sub", ""))
    elif c["type"] == "steps":
        bits += [f'{i}. {s["head"]}' + (f' ({s["note"]})' if s.get("note") else "") for i, s in enumerate(c["steps"], 1)]
    elif c["type"] == "timeline":
        bits += [f'{it["time"]} {it["head"]}' + (f' ({it["note"]})' if it.get("note") else "") for it in c["items"]]
    else:
        for col in c["cols"]:
            seg = col["head"]
            if col.get("value"):
                seg += f' {col["value"]}'
            if col.get("lines"):
                seg += ": " + ", ".join(col["lines"])
            bits.append(seg)
    return " — ".join(b for b in bits if b)


def main(only=None):
    OUT.mkdir(parents=True, exist_ok=True)
    posts = load_posts()
    with sync_playwright() as p:
        browser = p.chromium.launch()
        page = browser.new_page(viewport={"width": W, "height": H}, device_scale_factor=1)
        for post in posts:
            if only and post["slug"] not in only:
                continue
            for c in post.get("cards", []):
                page.set_content(RENDER[c["type"]](post, c), wait_until="load")
                out = OUT / f'{post["slug"]}-{c["id"]}.png'
                page.screenshot(path=str(out), full_page=False)
                print("card", out.relative_to(ROOT))
        browser.close()


if __name__ == "__main__":
    main(set(sys.argv[1:]) or None)
