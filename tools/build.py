"""식탁노트 사이트 빌드.

content/*.md  →  index.html, kitchen.html, local.html, posts/<slug>.html, sitemap.xml, robots.txt
카드 이미지는 tools/cards.py 로 먼저 만든다.

코너
  부엌 꿀팁   (category: 부엌 꿀팁)
  로컬 이야기 (category: 로컬 이야기)  section: 떠나는 날 | 그 지역의 맛 | 옛이야기,  region: 강원 등

본문 표기
  [[card:id]]      front matter cards 의 카드 이미지를 넣는다
  [[photo: 설명]]  아직 사진이 없는 자리 (사이트에는 보이지 않고 주석으로만 남는다)
  [[img:파일명|설명]]  assets/photos/파일명 사진을 넣는다

대표 이미지
  hero: {id, alt, credit}   Unsplash 사진
  hero: {card: 카드id, alt}  그 글의 카드 이미지를 대표 이미지로 쓴다 (본문에는 다시 넣지 않는다)

행사 정보 박스 (선택)
  info: {rows: [{label, value}], links: [{label, url}], checked: 2026-10-03, note?: 문구}

홈 상단 큰 카드: front matter 에 featured: true 인 글 (없으면 가장 최근 글)
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

CATS = [
    {"name": "부엌 꿀팁", "slug": "kitchen",
     "title": "부엌 꿀팁",
     "desc": "떡이 굳었을 때, 나물이 쓸 때, 김치에서 군내가 날 때. 부엌에서 막히는 순간마다 바로 쓸 수 있는 방법을 짧고 정확하게 정리합니다.",
     "meta": "굳은 떡 살리기, 나물 쓴맛 빼기, 식재료 보관법처럼 부엌에서 바로 쓰는 생활의 지혜를 정리한 식탁노트 부엌 꿀팁 모음입니다."},
    {"name": "로컬 이야기", "slug": "local",
     "title": "로컬 이야기",
     "desc": "밥상에서 시작해 지역으로 이어지는 이야기. 가볼 만한 축제와 당일 코스, 그 고장의 맛, 전해 내려오는 옛이야기를 담습니다. 강원도를 중심으로 전국 곳곳을 다룹니다.",
     "meta": "전국 축제 일정과 여행 코스, 지역의 향토 음식, 지방의 전설과 옛이야기를 정리한 식탁노트 로컬 이야기 모음입니다."},
]
CAT_BY_NAME = {c["name"]: c for c in CATS}
SECTIONS = [
    ("떠나는 날", "축제 일정과 당일·1박 코스, 타임테이블"),
    ("그 지역의 맛", "향토 음식의 유래와 먹는 법"),
    ("옛이야기", "지방에 전해 오는 전설과 설화"),
]


def unsplash(pid, w, h=None):
    q = f"?w={w}&q=75&auto=format&fit=crop"
    if h:
        q += f"&h={h}"
    return f"https://images.unsplash.com/{pid}{q}"


def hero_src(post, w, h, pre=None):
    """대표 이미지 주소. pre 가 None 이면 절대 주소."""
    hero = post["hero"]
    if hero.get("id"):
        return unsplash(hero["id"], w, h)
    path = f'assets/cards/{post["slug"]}-{hero["card"]}.png'
    return f"{SITE}/{path}" if pre is None else f"{pre}{path}"


def og_image(post):
    hero = post["hero"]
    if hero.get("card"):
        return hero_src(post, 1200, 675)
    if post.get("cards"):
        return f'{SITE}/assets/cards/{post["slug"]}-{post["cards"][0]["id"]}.png'
    return unsplash(hero["id"], 1200, 630)


def cat_of(post):
    return CAT_BY_NAME[post["category"]]


def label_of(post):
    """카드 위 배지 글자."""
    if post.get("section"):
        return " · ".join(x for x in [post["section"], post.get("region")] if x)
    return post["category"]


def newest_first(posts):
    return sorted(posts, key=lambda p: (p["date"], p["order"]), reverse=True)


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
    nav = "".join(f'<a href="{pre}{c["slug"]}.html">{e(c["name"])}</a>' for c in CATS)
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
  <nav class="nav" aria-label="코너">{nav}</nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
  <p class="foot-name">식탁<span>노트</span></p>
  <p>{TAGLINE}. 부엌에서 바로 쓰는 생활의 지혜와, 밥상에서 시작해 지역으로 이어지는 이야기를 담습니다.</p>
  <p class="foot-small">일부 사진은 <a href="https://unsplash.com/?utm_source=siktaknote&amp;utm_medium=referral" rel="noopener">Unsplash</a>의 무료 이미지를 사용합니다. 행사 일정과 요금은 바뀔 수 있으니 방문 전 공식 안내를 확인해 주세요.</p>
</div></footer>
</body>
</html>
"""


def credit(post):
    h = post["hero"]
    if not h.get("id"):
        return ""
    link = "https://unsplash.com/?utm_source=siktaknote&utm_medium=referral"
    return f'<figcaption>사진: {e(h["credit"])} / <a href="{link}" rel="noopener">Unsplash</a></figcaption>'


def post_card(p, depth, big=False):
    pre = "../" * depth
    w, h = (1200, 675) if big else (720, 450)
    cls = "post-card big" if big else "post-card"
    return f"""<a class="{cls}" href="{pre}posts/{p['slug']}.html">
  <div class="thumb"><img src="{hero_src(p, w, h, pre)}" alt="{e(p['hero']['alt'])}" loading="lazy" width="{w}" height="{h}"></div>
  <div class="pc-body">
    <span class="badge">{e(label_of(p))}</span>
    <h3>{e(p['title'])}</h3>
    <p>{e(p['description'])}</p>
  </div>
</a>"""


def info_box(post):
    info = post.get("info")
    if not info:
        return ""
    rows = "".join(f"<div><dt>{e(r['label'])}</dt><dd>{e(str(r['value']))}</dd></div>" for r in info.get("rows", []))
    links = "".join(
        f'<li><a href="{e(l["url"])}" rel="noopener nofollow" target="_blank">{e(l["label"])}</a></li>'
        for l in info.get("links", [])
    )
    links_html = f'<ul class="info-links" aria-label="공식 안내 링크">{links}</ul>' if links else ""
    checked = str(info.get("checked", post["date"])).replace("-", ".")
    note = info.get("note") or "일정과 요금은 바뀔 수 있으니 방문 전에 공식 안내를 한 번 더 확인하세요."
    return (f'<section class="info" aria-label="행사 정보"><h2>행사 정보</h2><dl>{rows}</dl>{links_html}'
            f'<p class="info-note">{checked} 확인 기준. {e(note)}</p></section>')


def build_post(post, posts):
    cat = cat_of(post)
    same = [p for p in posts if p["category"] == post["category"]]
    sidx = same.index(post)
    prev_p = same[sidx - 1] if sidx > 0 else None
    next_p = same[sidx + 1] if sidx + 1 < len(same) else None
    # 같은 코너의 다른 글을 돌려가며 3편, 모자라면 다른 코너 글로 채운다
    pool = [p for p in same[sidx:] + same[:sidx] if p is not post and p not in (prev_p, next_p)]
    enough = len(pool) >= 3
    if not enough:
        pool += [p for p in newest_first(posts) if p not in pool and p is not post]
    related = pool[:3]
    more_title = f"다른 {cat['name']}" if enough else "함께 읽으면 좋은 글"

    url = f"{SITE}/posts/{post['slug']}.html"
    og = og_image(post)
    mins = reading_minutes(post["body"])
    summary = "".join(f"<li>{e(s)}</li>" for s in post.get("summary", []))
    tags = "".join(f"<li>#{e(k.replace(' ', ''))}</li>" for k in post.get("keywords", []))

    pn = '<nav class="prev-next" aria-label="이전 글, 다음 글">'
    pn += (f'<a class="pn prev" href="{prev_p["slug"]}.html"><span>이전 글</span>{e(prev_p["title"])}</a>' if prev_p else "<span></span>")
    pn += (f'<a class="pn next" href="{next_p["slug"]}.html"><span>다음 글</span>{e(next_p["title"])}</a>' if next_p else "<span></span>")
    pn += "</nav>"

    rel = "".join(post_card(p, 1) for p in related)

    images = [og]
    hero_url = hero_src(post, 1200, 675)
    if hero_url not in images:
        images.append(hero_url)
    jsonld = {
        "@context": "https://schema.org",
        "@type": "Article",
        "headline": post["title"],
        "description": post["description"],
        "datePublished": post["date"],
        "dateModified": post.get("updated", post["date"]),
        "image": images,
        "author": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "mainEntityOfPage": url,
        "keywords": ", ".join(post.get("keywords", [])),
        "inLanguage": "ko",
    }

    crumb = f'<a href="../index.html">홈</a> › <a href="../{cat["slug"]}.html">{e(cat["name"])}</a>'
    if post.get("section"):
        crumb += f' › <a href="../{cat["slug"]}.html#{e(post["section"])}">{e(post["section"])}</a>'
    updated = post.get("updated")
    date_html = f'<time datetime="{post["date"]}">{post["date"].replace("-", ".")}</time>'
    if updated and str(updated) != post["date"]:
        date_html += f' · 수정 <time datetime="{updated}">{str(updated).replace("-", ".")}</time>'

    body = f"""<main class="wrap article-wrap">
<article class="article">
  <p class="crumb">{crumb}</p>
  <span class="badge">{e(label_of(post))}</span>
  <h1>{e(post['title'])}</h1>
  <p class="meta">{date_html} · {mins}분이면 읽어요</p>
  <figure class="hero"><img src="{hero_src(post, 1280, 720, '../')}" alt="{e(post['hero']['alt'])}" width="1280" height="720">{credit(post)}</figure>
  <section class="summary" aria-label="3줄 요약"><h2>3줄 요약</h2><ul>{summary}</ul></section>
  {info_box(post)}
  <div class="prose">
{render_body(post)}
  </div>
  <ul class="tags" aria-label="검색 키워드">{tags}</ul>
  {pn}
</article>
<section class="more"><h2>{e(more_title)}</h2><div class="grid">{rel}</div></section>
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


def section_block(cat, posts, limit=6):
    shown = newest_first(posts)
    more = ""
    if len(shown) > limit:
        more = f'<a class="list-more" href="{cat["slug"]}.html">전체 {len(shown)}편 보기 →</a>'
    return f"""<section id="{cat['slug']}" class="list">
  <div class="list-head"><h2>{e(cat['name'])}</h2><span>{len(posts)}편</span>{more}</div>
  <div class="grid">{"".join(post_card(p, 0) for p in shown[:limit])}</div>
</section>"""


def build_index(posts):
    featured = next((p for p in newest_first(posts) if p.get("featured")), newest_first(posts)[0])
    rest = [p for p in posts if p is not featured]
    blocks = []
    for cat in reversed(CATS):  # 새로 생긴 로컬 이야기를 먼저 보여준다
        items = [p for p in rest if p["category"] == cat["name"]]
        if items:
            blocks.append(section_block(cat, items))
    body = f"""<main class="wrap">
<section class="intro">
  <h1>{TAGLINE}</h1>
  <p>부엌에서 막히는 순간의 해결법, 그리고 밥상에서 시작해 지역으로 이어지는 축제·맛·옛이야기를 짧고 정확하게 정리합니다.</p>
</section>
<section class="feature">
  <div class="list-head"><h2>지금 읽을 글</h2></div>
  {post_card(featured, 0, big=True)}
</section>
{"".join(blocks)}
</main>"""
    jsonld = {"@context": "https://schema.org", "@type": "WebSite", "name": SITE_NAME, "url": SITE, "inLanguage": "ko"}
    return page(
        title=f"{SITE_NAME} — {TAGLINE}",
        description="굳은 떡 살리기, 나물 쓴맛 빼기 같은 부엌 꿀팁과 전국 축제 코스, 향토 음식, 지방의 옛이야기를 정리하는 식탁노트입니다.",
        canonical=f"{SITE}/",
        body=body,
        depth=0,
        og_image=og_image(featured),
        jsonld=jsonld,
    )


def build_category(cat, posts):
    items = newest_first([p for p in posts if p["category"] == cat["name"]])
    if cat["slug"] == "local":
        chips = "".join(f'<a href="#{e(s)}">{e(s)}</a>' for s, _ in SECTIONS if any(p.get("section") == s for p in items))
        groups = []
        for s, desc in SECTIONS:
            sub = [p for p in items if p.get("section") == s]
            if not sub:
                continue
            groups.append(
                f'<section id="{e(s)}" class="list"><div class="list-head"><h2>{e(s)}</h2><span>{len(sub)}편 · {e(desc)}</span></div>'
                f'<div class="grid">{"".join(post_card(p, 0) for p in sub)}</div></section>'
            )
        inner = f'<div class="chips" aria-label="분류">{chips}</div>{"".join(groups)}'
    else:
        inner = (f'<section class="list"><div class="list-head"><h2>{e(cat["name"])}</h2><span>{len(items)}편</span></div>'
                 f'<div class="grid">{"".join(post_card(p, 0) for p in items)}</div></section>')
    body = f"""<main class="wrap">
<section class="intro">
  <p class="crumb"><a href="index.html">홈</a> › {e(cat['name'])}</p>
  <h1>{e(cat['title'])}</h1>
  <p>{e(cat['desc'])}</p>
</section>
{inner}
</main>"""
    jsonld = {"@context": "https://schema.org", "@type": "CollectionPage", "name": f"{cat['name']} | {SITE_NAME}",
              "url": f"{SITE}/{cat['slug']}.html", "inLanguage": "ko"}
    return page(
        title=f"{cat['name']} | {SITE_NAME}",
        description=cat["meta"],
        canonical=f"{SITE}/{cat['slug']}.html",
        body=body,
        depth=0,
        og_image=og_image(items[0]),
        jsonld=jsonld,
    )


def build_sitemap(posts):
    urls = [(f"{SITE}/", max(p.get("updated", p["date"]) for p in posts))]
    for cat in CATS:
        sub = [p for p in posts if p["category"] == cat["name"]]
        if sub:
            urls.append((f"{SITE}/{cat['slug']}.html", max(p.get("updated", p["date"]) for p in sub)))
    urls += [(f"{SITE}/posts/{p['slug']}.html", p.get("updated", p["date"])) for p in posts]
    rows = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n'


def main():
    posts = load_posts()
    for p in posts:
        p["date"] = str(p["date"])
        if p.get("updated"):
            p["updated"] = str(p["updated"])
        if p["category"] not in CAT_BY_NAME:
            raise ValueError(f"{p['source']}: 알 수 없는 category {p['category']!r}")
    (ROOT / "posts").mkdir(exist_ok=True)
    for p in posts:
        (ROOT / "posts" / f"{p['slug']}.html").write_text(build_post(p, posts), encoding="utf-8")
        print("post", p["slug"])
    (ROOT / "index.html").write_text(build_index(posts), encoding="utf-8")
    for cat in CATS:
        if any(p["category"] == cat["name"] for p in posts):
            (ROOT / f"{cat['slug']}.html").write_text(build_category(cat, posts), encoding="utf-8")
    (ROOT / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("index, categories, sitemap, robots")


if __name__ == "__main__":
    main()
