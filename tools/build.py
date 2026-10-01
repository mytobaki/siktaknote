"""식탁노트 사이트 빌드.

content/*.md  →  index.html, posts/<slug>.html, sitemap.xml, robots.txt
카드 이미지는 tools/cards.py 로 먼저 만든다.

본문 표기
  [[card:id]]      front matter cards 의 카드 이미지를 넣는다
  [[photo: 설명]]  아직 사진이 없는 자리 (사이트에는 보이지 않고 주석으로만 남는다)
  [[img:파일명|설명]]  assets/photos/파일명 사진을 넣는다
"""
import html
import json
import pathlib
import re
import sys

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from cards import card_alt  # noqa: E402
from content import load_posts  # noqa: E402

SITE = "https://siktaknote.com"
SITE_NAME = "식탁노트"
TAGLINE = "매일 밥상에서 생기는 질문에 답합니다"
e = html.escape


def unsplash(pid, w, h=None):
    q = f"?w={w}&q=75&auto=format&fit=crop"
    if h:
        q += f"&h={h}"
    return f"https://images.unsplash.com/{pid}{q}"


def reading_minutes(text):
    plain = re.sub(r"\[\[.*?\]\]|[#*|>\-`]", "", text)
    return max(1, round(len(re.sub(r"\s+", "", plain)) / 500))


def render_body(post):
    cards = {c["id"]: c for c in post.get("cards", [])}
    first = [True]

    def card(m):
        c = cards[m.group(1).strip()]
        lazy = "" if first[0] else ' loading="lazy"'
        first[0] = False
        src = f'../assets/cards/{post["slug"]}-{c["id"]}.png'
        return (f'\n<figure class="card-fig"><img src="{src}" alt="{e(card_alt(c))}" '
                f'width="1200" height="675"{lazy}></figure>\n')

    def photo_slot(m):
        return f"\n<!-- 사진 자리: {e(m.group(1).strip())} -->\n"

    def img(m):
        fname, _, alt = m.group(1).partition("|")
        return (f'\n<figure class="photo-fig"><img src="../assets/photos/{e(fname.strip())}" '
                f'alt="{e(alt.strip())}" loading="lazy"></figure>\n')

    body = post["body"]
    body = re.sub(r"\[\[card:([^\]]+)\]\]", card, body)
    body = re.sub(r"\[\[photo:([^\]]+)\]\]", photo_slot, body)
    body = re.sub(r"\[\[img:([^\]]+)\]\]", img, body)
    out = markdown.markdown(body, extensions=["tables", "sane_lists"])
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out


HEAD_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@400;500;700'
    '&family=Noto+Serif+KR:wght@600;700&display=swap" rel="stylesheet">'
)


def page(*, title, description, canonical, body, depth, og_image=None, og_type="website", jsonld=None, keywords=None):
    pre = "../" * depth
    meta = [
        f'<meta name="description" content="{e(description)}">',
        f'<link rel="canonical" href="{canonical}">',
        f'<meta property="og:site_name" content="{SITE_NAME}">',
        f'<meta property="og:type" content="{og_type}">',
        f'<meta property="og:title" content="{e(title)}">',
        f'<meta property="og:description" content="{e(description)}">',
        f'<meta property="og:url" content="{canonical}">',
        '<meta property="og:locale" content="ko_KR">',
        '<meta name="twitter:card" content="summary_large_image">',
    ]
    if og_image:
        meta.append(f'<meta property="og:image" content="{og_image}">')
    if keywords:
        meta.append(f'<meta name="keywords" content="{e(", ".join(keywords))}">')
    if jsonld:
        meta.append(f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{chr(10).join(meta)}
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
{HEAD_FONTS}
<link rel="stylesheet" href="{pre}assets/style.css">
</head>
<body>
<header class="site-header"><div class="wrap header-inner">
  <a class="logo" href="{pre}index.html">식탁<span>노트</span></a>
  <nav class="nav" aria-label="카테고리"><a href="{pre}index.html#kitchen">부엌 꿀팁</a></nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
  <p class="foot-name">식탁<span>노트</span></p>
  <p>{TAGLINE}. 부엌에서 바로 쓰는 생활의 지혜와 제철 식재료 이야기를 담습니다.</p>
  <p class="foot-small">일부 사진은 <a href="https://unsplash.com/?utm_source=siktaknote&amp;utm_medium=referral" rel="noopener">Unsplash</a>의 무료 이미지를 사용합니다.</p>
</div></footer>
</body>
</html>
"""


def credit(post):
    h = post["hero"]
    link = "https://unsplash.com/?utm_source=siktaknote&utm_medium=referral"
    return f'사진: {e(h["credit"])} / <a href="{link}" rel="noopener">Unsplash</a>'


def post_card(p, depth, big=False):
    pre = "../" * depth
    w, h = (1200, 675) if big else (720, 450)
    cls = "post-card big" if big else "post-card"
    return f"""<a class="{cls}" href="{pre}posts/{p['slug']}.html">
  <div class="thumb"><img src="{unsplash(p['hero']['id'], w, h)}" alt="{e(p['hero']['alt'])}" loading="lazy" width="{w}" height="{h}"></div>
  <div class="pc-body">
    <span class="badge">{e(p['category'])}</span>
    <h3>{e(p['title'])}</h3>
    <p>{e(p['description'])}</p>
  </div>
</a>"""


def build_post(post, posts):
    idx = posts.index(post)
    prev_p = posts[idx - 1] if idx > 0 else None
    next_p = posts[idx + 1] if idx + 1 < len(posts) else None
    related = [p for p in posts if p is not post][:0]
    others = [p for p in posts if p is not post]
    # 앞뒤 글을 빼고 이어지는 글 3편
    related = [p for p in others[idx:] + others[:idx] if p not in (prev_p, next_p)][:3]

    url = f"{SITE}/posts/{post['slug']}.html"
    first_card = post["cards"][0]["id"] if post.get("cards") else None
    og = f"{SITE}/assets/cards/{post['slug']}-{first_card}.png" if first_card else unsplash(post["hero"]["id"], 1200, 630)
    mins = reading_minutes(post["body"])
    summary = "".join(f"<li>{e(s)}</li>" for s in post.get("summary", []))
    tags = "".join(f"<li>#{e(k.replace(' ', ''))}</li>" for k in post.get("keywords", []))

    pn = '<nav class="prev-next" aria-label="이전 글, 다음 글">'
    pn += (f'<a class="pn prev" href="{prev_p["slug"]}.html"><span>이전 글</span>{e(prev_p["title"])}</a>' if prev_p else "<span></span>")
    pn += (f'<a class="pn next" href="{next_p["slug"]}.html"><span>다음 글</span>{e(next_p["title"])}</a>' if next_p else "<span></span>")
    pn += "</nav>"

    rel = "".join(post_card(p, 1) for p in related)

    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["description"],
        "datePublished": post["date"],
        "dateModified": post.get("updated", post["date"]),
        "image": [og, unsplash(post["hero"]["id"], 1200, 675)],
        "author": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "mainEntityOfPage": url,
        "keywords": ", ".join(post.get("keywords", [])),
        "inLanguage": "ko",
    }

    body = f"""<main class="wrap article-wrap">
<article class="article">
  <p class="crumb"><a href="../index.html">홈</a> › <a href="../index.html#kitchen">{e(post['category'])}</a></p>
  <span class="badge">{e(post['category'])}</span>
  <h1>{e(post['title'])}</h1>
  <p class="meta"><time datetime="{post['date']}">{post['date'].replace('-', '.')}</time> · {mins}분이면 읽어요</p>
  <figure class="hero"><img src="{unsplash(post['hero']['id'], 1280, 720)}" alt="{e(post['hero']['alt'])}" width="1280" height="720"><figcaption>{credit(post)}</figcaption></figure>
  <section class="summary" aria-label="3줄 요약"><h2>3줄 요약</h2><ul>{summary}</ul></section>
  <div class="prose">
{render_body(post)}
  </div>
  <ul class="tags" aria-label="검색 키워드">{tags}</ul>
  {pn}
</article>
<section class="more"><h2>다른 부엌 꿀팁</h2><div class="grid">{rel}</div></section>
</main>"""
    return page(
        title=f"{post['title']} | {SITE_NAME}",
        description=post["description"],
        canonical=url,
        body=body,
        depth=1,
        og_image=og,
        og_type="article",
        jsonld=jsonld,
        keywords=post.get("keywords"),
    )


def build_index(posts):
    featured, rest = posts[0], posts[1:]
    cards = "".join(post_card(p, 0) for p in rest)
    body = f"""<main class="wrap">
<section class="intro">
  <h1>{TAGLINE}</h1>
  <p>떡이 굳었을 때, 나물이 쓸 때, 김치에서 군내가 날 때. 부엌에서 막히는 순간마다 바로 쓸 수 있는 방법을 짧고 정확하게 정리합니다.</p>
</section>
<section id="kitchen" class="list">
  <div class="list-head"><h2>부엌 꿀팁</h2><span>{len(posts)}편</span></div>
  {post_card(featured, 0, big=True)}
  <div class="grid">{cards}</div>
</section>
</main>"""
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE, "inLanguage": "ko"}
    return page(
        title=f"{SITE_NAME} — {TAGLINE}",
        description="굳은 떡 살리기, 나물 쓴맛 빼기, 김치 군내 잡기처럼 부엌에서 바로 쓰는 생활의 지혜를 정리하는 식탁노트입니다.",
        canonical=f"{SITE}/",
        body=body,
        depth=0,
        og_image=f"{SITE}/assets/cards/{featured['slug']}-{featured['cards'][0]['id']}.png",
        jsonld=jsonld,
    )


def build_sitemap(posts):
    urls = [(f"{SITE}/", max(p["date"] for p in posts))]
    urls += [(f"{SITE}/posts/{p['slug']}.html", p.get("updated", p["date"])) for p in posts]
    rows = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n'


def main():
    posts = load_posts()
    (ROOT / "posts").mkdir(exist_ok=True)
    for p in posts:
        (ROOT / "posts" / f"{p['slug']}.html").write_text(build_post(p, posts), encoding="utf-8")
        print("post", p["slug"])
    (ROOT / "index.html").write_text(build_index(posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("index, sitemap, robots")


if __name__ == "__main__":
    main()
