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
import urllib.parse

import markdown

ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "tools"))
from cards import card_alt  # noqa: E402
from content import load_posts  # noqa: E402

SITE = "https://siktaknote.com"
SITE_NAME = "식탁노트"
TAGLINE = "밥상 위의 작은 궁금증, 같이 풀어봐요"
OPERATOR = "김성호"
CONTACT_EMAIL = "tobaki@mytobaki.com"
POLICY_DATE = "2026-10-04"
e = html.escape
# 스타일이 바뀌면 주소 뒤 번호가 바뀌어 브라우저가 옛 CSS 를 쓰지 않는다
import hashlib  # noqa: E402
CSS_VER = hashlib.md5((ROOT / "assets" / "style.css").read_bytes()).hexdigest()[:8]


def site_cfg(key):
    """tools/site.json 의 설정값 (없으면 빈 문자열)."""
    try:
        cfg = json.loads((ROOT / "tools" / "site.json").read_text(encoding="utf-8"))
    except (OSError, ValueError):
        return ""
    return str(cfg.get(key, "")).strip()


def adsense_client():
    """tools/site.json 의 adsense_client (예: ca-pub-1234567890123456). 비어 있으면 광고 코드를 넣지 않는다."""
    cid = site_cfg("adsense_client")
    return cid if re.fullmatch(r"ca-pub-\d{10,20}", cid) else ""

CATS = [
    {"name": "부엌 꿀팁", "slug": "kitchen",
     "title": "부엌 꿀팁",
     "seo_title": "부엌 꿀팁 — 식재료 보관법, 냄새 잡는 법, 손질 요령 모음",
     "desc": "떡이 딱딱해졌을 때, 나물이 썼을 때, 김치에서 군내가 날 때. 부엌에서 막히는 순간마다 바로 따라 할 수 있는 방법을 쉽게 알려 드립니다.",
     "meta": "굳은 떡 살리기, 나물 쓴맛 빼기, 식재료 보관법처럼 부엌에서 바로 쓰는 생활의 지혜를 정리한 식탁노트 부엌 꿀팁 모음입니다."},
    {"name": "로컬 이야기", "slug": "local",
     "title": "로컬 이야기",
     "seo_title": "로컬 이야기 — 축제 일정과 여행 코스, 향토 음식, 지역 옛이야기",
     "desc": "밥상에서 시작해 지역으로 이어지는 이야기인데요. 가볼 만한 축제와 당일 코스, 그 고장의 맛, 전해 내려오는 옛이야기를 모았습니다. 강원도 이야기를 가장 많이 담고, 전국 곳곳으로도 놀러 가요.",
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


def local_photo(fname, pre=None):
    """assets/photos/ 에 넣은 사진 주소. pre 가 None 이면 절대 주소."""
    path = f"assets/photos/{fname}"
    return f"{SITE}/{path}" if pre is None else f"{pre}{path}"


def hero_src(post, w, h, pre=None):
    """대표 이미지 주소. pre 가 None 이면 절대 주소."""
    hero = post["hero"]
    if hero.get("file"):
        return local_photo(hero["file"], pre)
    if hero.get("id"):
        return unsplash(hero["id"], w, h)
    if hero.get("bg"):
        return unsplash(hero["bg"], w, h)
    path = f'assets/cards/{post["slug"]}-{hero["card"]}.png'
    return f"{SITE}/{path}" if pre is None else f"{pre}{path}"


def og_image(post):
    hero = post["hero"]
    if hero.get("file"):
        return local_photo(hero["file"])
    if hero.get("bg"):
        return unsplash(hero["bg"], 1200, 630)
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

    # 무료 사진(front matter photos)은 둘째 소제목 앞부터 차례로 넣는다.
    # [[photo: ...]] 자리는 대표님 실사진(`[[img:...]]`)을 위해 그대로 비워 둔다.
    stock = list(post.get("photos", []))

    def stock_fig(ph):
        link = "https://unsplash.com/?utm_source=siktaknote&utm_medium=referral"
        return (f'\n<figure class="photo-fig stock"><img src="{unsplash(ph["id"], 1280, 800)}" alt="{e(ph["alt"])}" '
                f'width="1280" height="800" loading="lazy"><figcaption>사진: {e(ph["credit"])} / '
                f'<a href="{link}" rel="noopener">Unsplash</a></figcaption></figure>\n')

    def photo_slot(m):
        return f"\n<!-- 사진 자리: {e(m.group(1).strip())} -->\n"

    body = post["body"]
    body = re.sub(r"\[\[card:([^\]]+)\]\]", card, body)
    body = re.sub(r"\[\[photo:([^\]]+)\]\]", photo_slot, body)
    body = re.sub(r"\[\[img:([^\]]+)\]\]", img, body)
    if stock:
        heads = [m.start() for m in re.finditer(r"(?m)^### ", body)]
        inserts = []
        for k, ph in enumerate(stock):
            pos = heads[min(k + 1, len(heads) - 1)] if heads else len(body)
            inserts.append((pos, stock_fig(ph)))
        for pos, text in sorted(inserts, key=lambda t: t[0], reverse=True):
            body = body[:pos] + text + "\n" + body[pos:]
    out = markdown.markdown(body, extensions=["tables", "sane_lists"])
    out = out.replace("<table>", '<div class="table-wrap"><table>').replace("</table>", "</table></div>")
    return out


HEAD_FONTS = (
    '<link rel="preconnect" href="https://fonts.googleapis.com">'
    '<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
    '<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@300;400;500;700&display=swap" rel="stylesheet">'
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
        '<meta name="robots" content="index, follow, max-image-preview:large">',
        f'<link rel="alternate" type="application/rss+xml" title="{SITE_NAME}" href="{SITE}/rss.xml">',
    ]
    for key, name in (("google_site_verification", "google-site-verification"),
                      ("naver_site_verification", "naver-site-verification")):
        if site_cfg(key):
            meta.append(f'<meta name="{name}" content="{e(site_cfg(key))}">')
    if og_image:
        meta.append(f'<meta property="og:image" content="{og_image}">')
    if keywords:
        meta.append(f'<meta name="keywords" content="{e(", ".join(keywords))}">')
    if jsonld:
        if isinstance(jsonld, list):
            jsonld = {"@context": "https://schema.org", "@graph": jsonld}
        meta.append(f'<script type="application/ld+json">{json.dumps(jsonld, ensure_ascii=False)}</script>')
    ads = adsense_client()
    if ads:
        meta.append(f'<meta name="google-adsense-account" content="{ads}">')
        meta.append(f'<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client={ads}" crossorigin="anonymous"></script>')
    nav = "".join(f'<a href="{pre}{c["slug"]}.html">{e(c["name"])}</a>' for c in CATS) + f'<a href="{pre}about.html">소개</a>'
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(title)}</title>
{chr(10).join(meta)}
<link rel="icon" href="{pre}assets/favicon.svg" type="image/svg+xml">
{HEAD_FONTS}
<link rel="stylesheet" href="{pre}assets/style.css?v={CSS_VER}">
</head>
<body>
<header class="site-header"><div class="wrap header-inner">
  <a class="logo" href="{pre}index.html" aria-label="식탁노트 홈">식탁노트</a>
  <nav class="nav" aria-label="코너">{nav}</nav>
</div></header>
{body}
<footer class="site-footer"><div class="wrap">
  <p class="foot-name">식탁노트</p>
  <p>{TAGLINE}. 부엌에서 바로 써먹는 살림 꿀팁과, 밥상에서 시작해 지역으로 이어지는 이야기를 정성껏 담았습니다.</p>
  <p class="foot-links"><a href="{pre}about.html">식탁노트 소개</a><a href="{pre}privacy.html">개인정보처리방침</a><a href="{pre}contact.html">문의</a></p>
  <p class="foot-small">일부 사진은 <a href="https://unsplash.com/?utm_source=siktaknote&amp;utm_medium=referral" rel="noopener">Unsplash</a>의 무료 이미지를 사용합니다. 행사 일정과 요금은 바뀔 수 있으니 방문 전 공식 안내를 확인해 주세요.</p>
</div></footer>
</body>
</html>
"""


def photo_hero(post, w, h, lazy=True, pre="../"):
    """사진 배경 위에 제목을 얹은 대표 이미지 (hero.bg 가 있는 글)."""
    hero = post["hero"]
    card = next(c for c in post["cards"] if c["id"] == hero["card"])
    sub = f'<span>{e(card["sub"])}</span>' if card.get("sub") else ""
    load = ' loading="lazy"' if lazy else ' fetchpriority="high"'
    return (f'<div class="photo-hero" role="img" aria-label="{e(hero["alt"])}">'
            f'<img src="{local_photo(hero["file"], pre) if hero.get("file") else unsplash(hero["bg"], w, h)}" alt=""{load} width="{w}" height="{h}" onerror="this.remove()">'
            f'<div class="ph-shade"></div>'
            f'<div class="ph-top"><span class="ph-brand">식탁노트</span><span class="ph-chip">{e(label_of(post))}</span></div>'
            f'<div class="ph-text"><strong>{e(card["title"])}</strong>{sub}</div></div>')


def hero_html(post, w, h, pre):
    hero = post["hero"]
    if hero.get("card") and (hero.get("bg") or hero.get("file")):
        return photo_hero(post, w, h, lazy=False, pre=pre)
    return (f'<img src="{hero_src(post, w, h, pre)}" alt="{e(hero["alt"])}" '
            f'width="{w}" height="{h}" fetchpriority="high">')


def credit_text(post):
    h = post["hero"]
    if h.get("file"):
        return f'<span class="hh-credit">{e(h.get("credit", ""))}</span>' if h.get("credit") else ""
    if not (h.get("id") or h.get("bg")):
        return ""
    return (f'<span class="hh-credit">사진: {e(h["credit"])} / '
            '<a href="https://unsplash.com/?utm_source=siktaknote&amp;utm_medium=referral" rel="noopener">Unsplash</a></span>')


def credit(post):
    h = post["hero"]
    if h.get("file"):
        return f'<figcaption>{e(h["credit"])}</figcaption>' if h.get("credit") else ""
    if not (h.get("id") or h.get("bg")):
        return ""
    link = "https://unsplash.com/?utm_source=siktaknote&utm_medium=referral"
    return f'<figcaption>사진: {e(h["credit"])} / <a href="{link}" rel="noopener">Unsplash</a></figcaption>'


def thumb_inner(p, w, h, pre, lazy=True):
    if p["hero"].get("card") and (p["hero"].get("bg") or p["hero"].get("file")):
        return photo_hero(p, w, h, lazy, pre)
    load = 'loading="lazy"' if lazy else 'fetchpriority="high"'
    return (f'<img src="{hero_src(p, w, h, pre)}" alt="{e(p["hero"]["alt"])}" '
            f'{load} width="{w}" height="{h}">')


def post_card(p, depth, big=False):
    pre = "../" * depth
    w, h = (1200, 675) if big else (720, 450)
    cls = "post-card big" if big else "post-card"
    return f"""<a class="{cls}" href="{pre}posts/{p['slug']}.html">
  <div class="thumb">{thumb_inner(p, w, h, pre, lazy=not big)}</div>
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
    note = info.get("note") or "일정과 요금은 바뀔 수 있으니 방문 전에 공식 안내를 한 번 더 확인하시는 게 좋습니다."
    return (f'<section class="info" aria-label="행사 정보"><h2>행사 정보</h2><dl>{rows}</dl>{links_html}'
            f'<p class="info-note">{checked} 확인 기준. {e(note)}</p></section>')


SHARE_ICONS = {
    # 흑백 아이콘 (글자색을 그대로 따라감)
    "facebook": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M13.5 22v-8h2.7l.4-3.2h-3.1V8.8c0-.9.3-1.6 1.6-1.6h1.7V4.4c-.3 0-1.3-.1-2.5-.1-2.5 0-4.1 1.5-4.1 4.2v2.3H7.4V14h2.8v8h3.3z"/></svg>',
    "threads": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round"><circle cx="12" cy="12" r="3.6"/><path d="M15.6 12v1.3a2.6 2.6 0 0 0 5.2 0V12a8.8 8.8 0 1 0-3.5 7"/></g></svg>',
    "x": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><path fill="currentColor" d="M17.8 3h3.1l-6.8 7.7L22 21h-6.2l-4.8-6.3L5.5 21H2.4l7.3-8.3L2 3h6.3l4.4 5.8L17.8 3zm-1.1 16.2h1.7L7.4 4.7H5.6l11.1 14.5z"/></svg>',
    "link": '<svg viewBox="0 0 24 24" aria-hidden="true" focusable="false"><g fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round"><path d="M10 13a5 5 0 0 0 7.5.5l3-3a5 5 0 0 0-7-7l-1.7 1.7"/><path d="M14 11a5 5 0 0 0-7.5-.5l-3 3a5 5 0 0 0 7 7l1.7-1.7"/></g></svg>',
}


def share_block(url, title, where):
    """공유 버튼: 페이스북, 쓰레드, X, 주소 복사. where = top(제목 아래) | bottom(글 끝).
    앞의 셋은 자바스크립트 없이도 동작하고, 주소 복사는 SHARE_SCRIPT 가 켠다."""
    q = lambda s: urllib.parse.quote(s, safe="")
    links = [
        ("facebook", "페이스북", f"https://www.facebook.com/sharer/sharer.php?u={q(url)}"),
        ("threads", "쓰레드", f"https://www.threads.net/intent/post?text={q(title + chr(10) + url)}"),
        ("x", "X", f"https://twitter.com/intent/tweet?url={q(url)}&text={q(title)}"),
    ]
    items = "".join(
        f'<a class="sh sh-{key}" href="{e(href)}" target="_blank" rel="noopener noreferrer" '
        f'aria-label="{e(name)}에 공유하기">{SHARE_ICONS[key]}<span>{e(name)}</span></a>'
        for key, name, href in links
    )
    copy = (f'<button type="button" class="sh share-copy" data-url="{e(url)}" hidden>'
            f'{SHARE_ICONS["link"]}<span>주소 복사</span></button>')
    head = '<p class="share-label">이 글이 도움이 됐다면 나눠 주세요</p>' if where == "bottom" else ""
    return (f'<div class="share share-{where}" role="group" aria-label="이 글 공유하기">'
            f'{head}<div class="share-btns">{items}{copy}</div></div>')


SHARE_SCRIPT = """<script>
(function(){
  var bs=document.querySelectorAll('.share-copy');
  function legacy(u){
    var x=document.createElement('textarea');
    x.value=u;x.setAttribute('readonly','');x.style.position='fixed';x.style.opacity='0';
    document.body.appendChild(x);x.select();
    var ok=false;try{ok=document.execCommand('copy')}catch(_){}
    document.body.removeChild(x);return ok;
  }
  Array.prototype.forEach.call(bs,function(b){
    b.hidden=false;
    var label=b.querySelector('span'),t;
    function done(m){label.textContent=m;b.classList.add('is-done');clearTimeout(t);
      t=setTimeout(function(){label.textContent='주소 복사';b.classList.remove('is-done')},1800)}
    b.addEventListener('click',function(){
      var u=b.getAttribute('data-url');
      if(navigator.clipboard&&window.isSecureContext){
        navigator.clipboard.writeText(u).then(function(){done('복사했어요')},function(){done(legacy(u)?'복사했어요':'길게 눌러 복사해 주세요')});
      }else{done(legacy(u)?'복사했어요':'길게 눌러 복사해 주세요')}
    });
  });
})();
</script>"""


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
        "@type": "Article",
        "headline": post["title"],
        "description": post["description"],
        "datePublished": post["date"],
        "dateModified": post.get("updated", post["date"]),
        "image": images,
        "author": {"@type": "Organization", "name": SITE_NAME, "url": f"{SITE}/about.html"},
        "publisher": {"@type": "Organization", "name": SITE_NAME, "url": SITE},
        "mainEntityOfPage": url,
        "keywords": ", ".join(post.get("keywords", [])),
        "inLanguage": "ko",
    }

    jsonld["articleSection"] = cat["name"]
    jsonld = [jsonld, {
        "@type": "BreadcrumbList",
        "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": cat["name"], "item": f"{SITE}/{cat['slug']}.html"},
            {"@type": "ListItem", "position": 3, "name": post["title"], "item": url},
        ],
    }]
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
  {share_block(url, post['title'], 'top')}
  <figure class="hero">{hero_html(post, 1280, 720, '../')}{credit(post)}</figure>
  <section class="summary" aria-label="3줄 요약"><h2>3줄 요약</h2><ul>{summary}</ul></section>
  {info_box(post)}
  <div class="prose">
{render_body(post)}
  </div>
  <ul class="tags" aria-label="검색 키워드">{tags}</ul>
  {share_block(url, post['title'], 'bottom')}
  {pn}
</article>
<section class="more"><h2>{e(more_title)}</h2><div class="grid">{rel}</div></section>
</main>
{SHARE_SCRIPT}"""
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


def section_block(cat, posts, total, limit=6):
    shown = newest_first(posts)
    more = ""
    if total > limit:
        more = f'<a class="list-more" href="{cat["slug"]}.html">전체 {total}편 보기 →</a>'
    return f"""<section id="{cat['slug']}" class="list">
  <div class="list-head"><h2>{e(cat['name'])}</h2><span>{total}편</span>{more}</div>
  <div class="grid">{"".join(post_card(p, 0) for p in shown[:limit])}</div>
</section>"""


def build_index(posts):
    featured = next((p for p in newest_first(posts) if p.get("featured")), newest_first(posts)[0])
    rest = [p for p in posts if p is not featured]
    blocks = []
    for cat in reversed(CATS):  # 새로 생긴 로컬 이야기를 먼저 보여준다
        items = [p for p in rest if p["category"] == cat["name"]]
        if items:
            total = sum(1 for p in posts if p["category"] == cat["name"])
            blocks.append(section_block(cat, items, total))
    h1a, _, h1b = TAGLINE.partition(", ")
    h1a = h1a + "," if h1b else h1a
    body = f"""<main class="wrap">
<section class="home-hero">
  <div class="hh-text">
    <p class="eyebrow">Kitchen · Local · Stories</p>
    <h1>{e(h1a)}<br>{e(h1b)}</h1>
    <p class="hh-lead">떡이 딱딱해져서 막막했던 순간의 해결법부터, 밥상에서 시작해 우리 지역 곳곳으로 떠나는 축제 소식과 맛 이야기, 옛이야기까지 쉽고 따뜻하게 모았습니다.</p>
    <div class="hh-actions"><a class="btn" href="kitchen.html">부엌 꿀팁 보기<span aria-hidden="true">→</span></a><a class="btn-line" href="local.html">로컬 이야기</a></div>
  </div>
  <figure class="hh-visual">
    <a href="posts/{featured['slug']}.html"><img src="{hero_src(featured, 960, 1080)}" alt="{e(featured['hero']['alt'])}" width="960" height="1080" fetchpriority="high" onerror="this.style.visibility='hidden'"></a>
    <figcaption><a href="posts/{featured['slug']}.html"><small>지금 읽을 글</small>{e(featured['title'])}</a>{credit_text(featured)}</figcaption>
  </figure>
</section>
<ul class="values" aria-label="식탁노트가 지키는 것">
  <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M7 3h7l4 4v14H7z"/><path d="M14 3v4h4"/><path d="m10 14 2 2 4-4"/></svg><span>출처를 확인한 정보</span></li>
  <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M3 11h14a0 0 0 0 1 0 0 7 7 0 0 1-7 7 7 7 0 0 1-7-7z"/><path d="M17 12.5h2.5a1.5 1.5 0 0 0 0-3H17"/><path d="M8 7c0-1.2 1-1.8 1-3M12 7c0-1.2 1-1.8 1-3"/><path d="M6 21h8"/></svg><span>바로 따라 하는 방법</span></li>
  <li><svg viewBox="0 0 24 24" aria-hidden="true"><path d="M12 21s-6-5.4-6-10.5a6 6 0 0 1 12 0C18 15.6 12 21 12 21z"/><circle cx="12" cy="10.5" r="2.2"/></svg><span>밥상에서 지역까지</span></li>
</ul>
{"".join(blocks)}
</main>"""
    jsonld = [
        {"@type": "WebSite", "@id": f"{SITE}/#website", "name": SITE_NAME, "alternateName": "siktaknote",
         "url": f"{SITE}/", "inLanguage": "ko", "description": TAGLINE,
         "publisher": {"@id": f"{SITE}/#org"}},
        {"@type": "Organization", "@id": f"{SITE}/#org", "name": SITE_NAME, "url": f"{SITE}/",
         "email": CONTACT_EMAIL},
    ]
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
    jsonld = [
        {"@type": "CollectionPage", "name": f"{cat['name']} | {SITE_NAME}", "url": f"{SITE}/{cat['slug']}.html",
         "inLanguage": "ko", "description": cat["meta"],
         "mainEntity": {"@type": "ItemList", "itemListElement": [
             {"@type": "ListItem", "position": i + 1, "url": f"{SITE}/posts/{p['slug']}.html", "name": p["title"]}
             for i, p in enumerate(items)]}},
        {"@type": "BreadcrumbList", "itemListElement": [
            {"@type": "ListItem", "position": 1, "name": "홈", "item": f"{SITE}/"},
            {"@type": "ListItem", "position": 2, "name": cat["name"], "item": f"{SITE}/{cat['slug']}.html"}]},
    ]
    return page(
        title=f"{cat['seo_title']} | {SITE_NAME}",
        description=cat["meta"],
        canonical=f"{SITE}/{cat['slug']}.html",
        body=body,
        depth=0,
        og_image=og_image(items[0]),
        jsonld=jsonld,
    )


def build_static(slug, title, description, h1, inner):
    url = f"{SITE}/{slug}.html"
    body = f"""<main class="wrap article-wrap">
<article class="article">
  <p class="crumb"><a href="index.html">홈</a> › {e(h1)}</p>
  <h1>{e(h1)}</h1>
  <div class="prose">
{inner}
  </div>
</article>
</main>"""
    return page(title=f"{title} | {SITE_NAME}", description=description, canonical=url, body=body, depth=0)


ABOUT = f"""
<p>안녕하세요, 식탁노트예요. 밥상 위에서 생기는 작은 궁금증을 같이 풀어 보려고 만든 사이트입니다. 굳어 버린 떡은 어떻게 살리지, 사 온 무는 어떻게 두어야 끝까지 쓸 수 있지, 이번 주말 축제는 언제 어떻게 가면 편할까. 이런 질문에 차근차근 답해 드리는 게 목표예요.</p>

<h3>두 개의 코너가 있어요</h3>
<p><strong>부엌 꿀팁</strong>에서는 냄새 잡기, 식재료 보관, 손질처럼 부엌에서 바로 써먹는 방법을 정리하는데요. 왜 그렇게 하면 되는지도 함께 적어서, 상황이 조금 달라져도 응용할 수 있게 하려고 합니다.</p>
<p><strong>로컬 이야기</strong>에서는 밥상에서 시작해 지역으로 이어지는 이야기를 다룹니다. 가 볼 만한 축제와 하루 코스, 그 고장의 향토 음식, 전해 내려오는 옛이야기를 모아요. 강원도 이야기를 가장 많이 담고, 전국 곳곳으로도 놀러 갑니다.</p>

<h3>글은 이렇게 만들어요</h3>
<p>글은 AI 도구의 도움을 받아 초안을 쓰고, 운영자가 내용을 확인한 뒤에 올립니다. 축제 일정이나 옛이야기처럼 사실 확인이 필요한 글은 공식 사이트, 한국관광공사, 한국민족문화대백과사전 같은 공개된 자료를 바탕으로 하고, 확인하지 못한 부분은 확인하지 못했다고 그대로 적어요. 행사 정보에는 확인한 날짜를 함께 밝히고, 바뀐 내용이 있으면 고쳐 쓰고 있습니다.</p>
<p>부엌 꿀팁은 널리 알려진 생활 지식을 정리한 것이라, 식품 안전이나 건강에 관한 전문적인 조언은 아닙니다. 몸 상태나 식재료 상태가 걱정될 때는 전문가의 안내를 따라 주세요.</p>

<h3>잘못된 내용을 발견하셨나요</h3>
<p>틀린 정보나 바뀐 일정을 알려 주시면 확인해서 바로잡겠습니다. <a href="contact.html">문의 페이지</a>에서 연락 방법을 확인해 주세요.</p>

<h3>사진과 광고</h3>
<p>글에 쓰인 사진 가운데 일부는 <a href="https://unsplash.com/?utm_source=siktaknote&amp;utm_medium=referral" rel="noopener">Unsplash</a>의 무료 이미지이고, 사진을 찍은 분의 이름을 글마다 밝혀 두었습니다. 앞으로 이 사이트에는 구글 애드센스 같은 광고가 게재될 수 있는데요. 광고가 붙더라도 글의 내용은 광고와 관계없이 쓰고, 광고 관련 안내는 <a href="privacy.html">개인정보처리방침</a>에 적어 두었습니다.</p>

<h3>운영자</h3>
<p>식탁노트는 {OPERATOR}가 운영합니다.</p>
"""

PRIVACY = f"""
<p>식탁노트(siktaknote.com, 이하 "사이트")는 방문해 주시는 분들의 개인정보를 소중하게 다룹니다. 이 방침은 사이트에서 어떤 정보가 쓰이는지, 광고와 쿠키는 어떻게 다뤄지는지 알려 드리기 위한 글이에요.</p>

<h3>1. 직접 수집하는 개인정보</h3>
<p>사이트에는 회원가입, 댓글, 구독 신청처럼 개인정보를 입력받는 기능이 없고, 방문자의 개인정보를 직접 수집하거나 저장하지 않습니다. 문의 메일을 보내 주시면 보내신 분의 이메일 주소와 내용을 확인할 수 있는데, 이 정보는 답변을 드리는 데에만 쓰고 처리가 끝나면 지체 없이 파기합니다.</p>

<h3>2. 접속 기록</h3>
<p>사이트는 GitHub Pages를 통해 제공돼요. 사이트에 접속하면 호스팅 업체인 GitHub의 서버에 접속 기록(IP 주소, 브라우저 종류, 접속 시간 등)이 남을 수 있어요. 이 기록은 해당 업체의 정책에 따라 관리되고, 식탁노트가 따로 내려받아 보관하지 않습니다.</p>

<h3>3. 광고와 쿠키</h3>
<p>사이트에는 구글 애드센스를 비롯한 광고가 게재될 수 있어요. 광고가 게재될 때는 다음과 같이 운영됩니다.</p>
<ul>
<li>Google을 비롯한 제3자 광고 공급업체는 쿠키를 사용해, 이용자가 이 사이트나 다른 웹사이트를 이전에 방문한 기록을 바탕으로 광고를 게재합니다.</li>
<li>Google은 광고 쿠키를 사용해 Google과 파트너가 이 사이트와 인터넷상의 다른 사이트 방문 기록을 바탕으로 이용자에게 광고를 게재할 수 있어요.</li>
<li>이용자는 <a href="https://adssettings.google.com" rel="noopener">Google 광고 설정</a>에서 맞춤 광고를 끌 수 있어요. 다른 광고 공급업체의 맞춤 광고는 <a href="https://www.aboutads.info" rel="noopener">www.aboutads.info</a>에서 선택을 해제할 수 있습니다.</li>
<li>Google의 광고 관련 정책은 <a href="https://policies.google.com/technologies/ads?hl=ko" rel="noopener">Google 광고 기술 정책</a>에서 볼 수 있어요.</li>
<li>사용 중인 브라우저의 설정에서 쿠키를 차단하거나 삭제할 수도 있어요. 다만 일부 기능이 제대로 동작하지 않을 수 있어요.</li>
</ul>

<h3>4. 외부 서비스</h3>
<p>사이트는 글꼴(Google Fonts)과 일부 사진(Unsplash)을 해당 서비스의 서버에서 불러와요. 이때 방문자의 IP 주소와 브라우저 정보가 해당 서비스에 전달될 수 있어요. 글 안에 있는 공식 사이트 등 외부 링크로 이동하면 그 사이트의 개인정보 방침이 적용됩니다.</p>

<h3>5. 방문 통계</h3>
<p>현재는 방문자 통계 도구를 쓰지 않아요. 앞으로 도입하게 되면 이 방침에 쓰는 도구와 목적을 먼저 적어 두겠습니다.</p>

<h3>6. 어린이의 개인정보</h3>
<p>사이트는 만 14세 미만 어린이의 개인정보를 수집하지 않습니다.</p>

<h3>7. 문의</h3>
<p>개인정보와 관련해 궁금한 점은 {OPERATOR}에게 이메일(<a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a>)로 알려 주세요.</p>

<h3>8. 방침이 바뀔 때</h3>
<p>이 방침의 내용이 바뀌면 이 페이지에 새로 적고 날짜를 고치겠습니다.</p>
<p>시행일: {POLICY_DATE.replace("-", ".")}</p>
"""

CONTACT = f"""
<p>식탁노트에 궁금한 점이나 하고 싶은 말씀이 있으면 편하게 메일을 보내 주세요.</p>

<h3>이메일</h3>
<p><a href="mailto:{CONTACT_EMAIL}">{CONTACT_EMAIL}</a></p>
<p>운영자: {OPERATOR}</p>

<h3>이런 내용을 보내 주세요</h3>
<ul>
<li>글에서 틀린 정보나 바뀐 일정을 발견했을 때</li>
<li>다뤄 줬으면 하는 부엌 고민이나 지역 이야기가 있을 때</li>
<li>글이나 사진의 저작권과 관련해 알리실 내용이 있을 때</li>
<li>그 밖에 사이트에 대한 의견</li>
</ul>

<h3>답변은 이렇게 드려요</h3>
<p>보내 주신 메일은 순서대로 확인하고, 보통 며칠 안에 답장을 드려요. 틀린 정보를 알려 주시면 확인한 뒤 글을 고치고, 글 아래의 수정한 날짜에 반영합니다.</p>
<p>개인정보 처리에 관해서는 <a href="privacy.html">개인정보처리방침</a>을 참고해 주세요.</p>
"""

STATIC_PAGES = [
    ("about", "식탁노트 소개", "식탁노트는 부엌 꿀팁과 지역 이야기를 쉽고 따뜻하게 풀어 쓰는 사이트예요. 어떤 사이트인지, 글을 어떻게 만드는지 소개합니다.", "식탁노트 소개", ABOUT),
    ("privacy", "개인정보처리방침", "식탁노트의 개인정보처리방침이에요. 수집하는 정보, 광고와 쿠키, 외부 서비스 이용에 관한 안내를 담았습니다.", "개인정보처리방침", PRIVACY),
    ("contact", "문의", "식탁노트에 궁금한 점이나 정정 제보, 의견이 있을 때 연락하는 방법을 안내해요.", "문의", CONTACT),
]


def build_sitemap(posts):
    urls = [(f"{SITE}/", max(p.get("updated", p["date"]) for p in posts))]
    for cat in CATS:
        sub = [p for p in posts if p["category"] == cat["name"]]
        if sub:
            urls.append((f"{SITE}/{cat['slug']}.html", max(p.get("updated", p["date"]) for p in sub)))
    urls += [(f"{SITE}/posts/{p['slug']}.html", p.get("updated", p["date"])) for p in posts]
    urls += [(f"{SITE}/{slug}.html", POLICY_DATE) for slug, *_ in STATIC_PAGES]
    rows = "".join(f"<url><loc>{u}</loc><lastmod>{d}</lastmod></url>" for u, d in urls)
    return f'<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{rows}</urlset>\n'


def build_rss(posts):
    from email.utils import format_datetime
    from datetime import datetime, timezone, timedelta
    kst = timezone(timedelta(hours=9))

    def rfc(d):
        return format_datetime(datetime.fromisoformat(str(d)).replace(hour=9, tzinfo=kst))

    items = []
    for p in sorted(posts, key=lambda p: (p.get("updated", p["date"]), p["order"]), reverse=True):
        url = f"{SITE}/posts/{p['slug']}.html"
        items.append(
            f"<item><title>{e(p['title'])}</title><link>{url}</link><guid isPermaLink=\"true\">{url}</guid>"
            f"<description>{e(p['description'])}</description><category>{e(p['category'])}</category>"
            f"<pubDate>{rfc(p['date'])}</pubDate></item>")
    latest = max(p.get("updated", p["date"]) for p in posts)
    return ('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0" xmlns:atom="http://www.w3.org/2005/Atom"><channel>'
            f"<title>{SITE_NAME}</title><link>{SITE}/</link><description>{e(TAGLINE)}</description><language>ko</language>"
            f'<atom:link href="{SITE}/rss.xml" rel="self" type="application/rss+xml"/>'
            f"<lastBuildDate>{rfc(latest)}</lastBuildDate>{''.join(items)}</channel></rss>\n")


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
    for slug, title, desc, h1, inner in STATIC_PAGES:
        (ROOT / f"{slug}.html").write_text(build_static(slug, title, desc, h1, inner), encoding="utf-8")
    ads = adsense_client()
    ads_txt = ROOT / "ads.txt"
    if ads:
        ads_txt.write_text(f"google.com, {ads.replace('ca-', '')}, DIRECT, f08c47fec0942fa0\n", encoding="utf-8")
    elif ads_txt.exists():
        ads_txt.unlink()
    (ROOT / "sitemap.xml").write_text(build_sitemap(posts), encoding="utf-8")
    (ROOT / "rss.xml").write_text(build_rss(posts), encoding="utf-8")
    (ROOT / "robots.txt").write_text(f"User-agent: *\nAllow: /\nSitemap: {SITE}/sitemap.xml\n", encoding="utf-8")
    print("index, categories, sitemap, robots")


if __name__ == "__main__":
    main()
