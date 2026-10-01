"""말랑이의 부엌 과학 — 세로 웹툰 생성기.

캐릭터는 SVG 조각으로 그려서 회차가 늘어도 모습이 똑같이 유지된다.
  python3 tools/webtoon.py page  <out.html>   # 미리보기용 페이지 (Google Fonts)
  python3 tools/webtoon.py png   <out.png>    # 사이트용 세로 이미지 (로컬 폰트)
"""
import html
import pathlib
import sys

e = html.escape
INK = "#4a4038"
W, H = 720, 540

# ---------------------------------------------------------------- characters

def mallang(x, y, s=1.0, mood="normal", arm=None, hard=False):
    """감자떡 캐릭터 말랑이. mood: normal | happy | worry | talk | relax"""
    fill = "#e2dccf" if hard else "#f7f3ea"
    parts = [f'<g transform="translate({x},{y}) scale({s})">']
    parts.append('<ellipse cx="0" cy="40" rx="76" ry="9" fill="#000" opacity=".07"/>')
    if arm == "point":
        parts.append(f'<path d="M70 4 C92 -4 104 -18 110 -34" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                     f'<circle cx="111" cy="-37" r="7" fill="{fill}" stroke="{INK}" stroke-width="4"/>')
    if arm == "up":
        parts.append(f'<path d="M-70 4 C-92 -6 -98 -26 -100 -44" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                     f'<circle cx="-100" cy="-47" r="7" fill="{fill}" stroke="{INK}" stroke-width="4"/>'
                     f'<path d="M70 4 C92 -6 98 -26 100 -44" stroke="{INK}" stroke-width="5" fill="none" stroke-linecap="round"/>'
                     f'<circle cx="100" cy="-47" r="7" fill="{fill}" stroke="{INK}" stroke-width="4"/>')
    body = "M-82 28 C-84 -38 -42 -64 0 -64 C42 -64 84 -38 82 28 C44 42 -44 42 -82 28Z"
    parts.append(f'<path d="{body}" fill="{fill}" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    parts.append('<path d="M-52 20 C-50 -16 50 -16 52 20 C22 28 -22 28 -52 20Z" fill="#9b7a5c" opacity=".13"/>')
    # 감자떡 가장자리 주름
    parts.append(f'<path d="M-70 30 l6 -7 M-48 35 l5 -8 M-24 38 l4 -8 M0 39 v-8 M24 38 l-4 -8 M48 35 l-5 -8 M70 30 l-6 -7" '
                 f'stroke="{INK}" stroke-width="2.5" opacity=".35" stroke-linecap="round"/>')
    if not hard:
        parts.append('<path d="M-56 -22 C-48 -42 -30 -52 -14 -54" stroke="#fff" stroke-width="7" fill="none" stroke-linecap="round"/>')
    else:
        parts.append('<path d="M-18 -62 l7 15 -9 10 7 13 M40 -50 l-4 12 8 8" stroke="#8f8577" stroke-width="3" fill="none" stroke-linecap="round" stroke-linejoin="round"/>')
    # face
    if mood == "happy":
        parts.append(f'<path d="M-33 -6 Q-25 -16 -17 -6 M17 -6 Q25 -16 33 -6" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                     '<path d="M-11 6 Q0 22 11 6Z" fill="#c4574a"/>')
    elif mood == "relax":
        parts.append(f'<path d="M-33 -4 Q-25 2 -17 -4 M17 -4 Q25 2 33 -4" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                     f'<path d="M-9 9 Q0 15 9 9" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    else:
        parts.append(f'<ellipse cx="-24" cy="-6" rx="5.5" ry="7.5" fill="{INK}"/><ellipse cx="24" cy="-6" rx="5.5" ry="7.5" fill="{INK}"/>'
                     '<circle cx="-22" cy="-9" r="1.8" fill="#fff"/><circle cx="26" cy="-9" r="1.8" fill="#fff"/>')
        if mood == "worry":
            parts.append(f'<path d="M-34 -22 L-15 -17 M34 -22 L15 -17" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>'
                         f'<path d="M-11 13 q5.5 -6 11 0 q5.5 6 11 0" stroke="{INK}" stroke-width="3.5" fill="none" stroke-linecap="round"/>'
                         '<path d="M62 -40 C68 -30 70 -24 66 -20 C62 -16 56 -20 58 -26 Z" fill="#9fd0ec" stroke="#5b95b8" stroke-width="2"/>')
        elif mood == "talk":
            parts.append('<path d="M-9 6 Q0 19 9 6Z" fill="#c4574a"/>')
        else:
            parts.append(f'<path d="M-8 7 Q0 14 8 7" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    parts.append('<ellipse cx="-42" cy="9" rx="10" ry="5.5" fill="#f19c94" opacity=".55"/><ellipse cx="42" cy="9" rx="10" ry="5.5" fill="#f19c94" opacity=".55"/>')
    parts.append("</g>")
    return "".join(parts)


def kid(x, y, s=1.0, mood="curious", hold=None):
    """아이 캐릭터 하나. mood: curious | surprised | happy | think. hold: tteok | hard | spoon"""
    p = [f'<g transform="translate({x},{y}) scale({s})">']
    p.append(f'<path d="M-58 170 C-60 104 -40 86 0 86 C40 86 60 104 58 170Z" fill="#f4c86a" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>')
    p.append(f'<path d="M-24 92 Q0 110 24 92" stroke="{INK}" stroke-width="3.5" fill="none"/>')
    p.append(f'<circle cx="-60" cy="28" r="11" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/><circle cx="60" cy="28" r="11" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/>')
    p.append(f'<circle cx="0" cy="22" r="62" fill="#f7d6b8" stroke="{INK}" stroke-width="4.5"/>')
    p.append('<path d="M-62 18 C-68 -46 -18 -52 4 -52 C36 -52 70 -38 62 18 C52 -4 30 -14 6 -16 C2 -6 -10 0 -22 2 C-12 -6 -10 -12 -12 -16 C-32 -12 -50 0 -62 18Z" fill="#3b2f29"/>')
    p.append(f'<path d="M14 -52 C18 -66 30 -70 36 -64" stroke="#3b2f29" stroke-width="6" fill="none" stroke-linecap="round"/>')
    if mood == "happy":
        p.append(f'<path d="M-30 26 Q-22 16 -14 26 M14 26 Q22 16 30 26" stroke="{INK}" stroke-width="4.5" fill="none" stroke-linecap="round"/>'
                 '<path d="M-15 44 Q0 64 15 44Z" fill="#c4574a"/>')
    elif mood == "think":
        p.append(f'<ellipse cx="-20" cy="26" rx="5.5" ry="7.5" fill="{INK}"/><ellipse cx="22" cy="24" rx="5.5" ry="7.5" fill="{INK}"/>'
                 f'<path d="M-8 50 Q2 46 12 50" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    else:
        p.append(f'<ellipse cx="-22" cy="26" rx="5.5" ry="7.5" fill="{INK}"/><ellipse cx="22" cy="26" rx="5.5" ry="7.5" fill="{INK}"/>'
                 '<circle cx="-20" cy="23" r="1.8" fill="#fff"/><circle cx="24" cy="23" r="1.8" fill="#fff"/>')
        if mood == "surprised":
            p.append('<ellipse cx="0" cy="52" rx="8" ry="10" fill="#8f3a32"/>'
                     f'<path d="M-34 6 L-14 10 M34 6 L14 10" stroke="{INK}" stroke-width="3.5" stroke-linecap="round"/>')
        else:
            p.append(f'<path d="M-9 48 Q0 56 9 48" stroke="{INK}" stroke-width="4" fill="none" stroke-linecap="round"/>')
    p.append('<ellipse cx="-38" cy="42" rx="10" ry="6" fill="#f19c94" opacity=".55"/><ellipse cx="38" cy="42" rx="10" ry="6" fill="#f19c94" opacity=".55"/>')
    if hold == "hard":
        p.append(f'<rect x="44" y="96" width="46" height="30" rx="8" fill="#e2dccf" stroke="{INK}" stroke-width="4" transform="rotate(-12 67 111)"/>'
                 '<path d="M58 100 l5 9 -6 7" stroke="#8f8577" stroke-width="2.5" fill="none" transform="rotate(-12 67 111)"/>'
                 f'<circle cx="52" cy="128" r="12" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/>')
    elif hold == "tteok":
        p.append(f'<rect x="44" y="98" width="44" height="28" rx="12" fill="#f7f3ea" stroke="{INK}" stroke-width="4" transform="rotate(-10 66 112)"/>'
                 f'<circle cx="52" cy="128" r="12" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/>')
    else:
        p.append(f'<circle cx="-50" cy="140" r="12" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/><circle cx="50" cy="140" r="12" fill="#f7d6b8" stroke="{INK}" stroke-width="4"/>')
    p.append("</g>")
    return "".join(p)


def bead(x, y, r=17, face=True, squeeze=False):
    """전분 알갱이"""
    rx, ry = (r * 1.08, r * 0.86) if squeeze else (r, r)
    g = f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{ry}" fill="#f0e2c2" stroke="#8a7656" stroke-width="3"/>'
    if face:
        g += (f'<circle cx="{x-5}" cy="{y-2}" r="2.2" fill="{INK}"/><circle cx="{x+5}" cy="{y-2}" r="2.2" fill="{INK}"/>')
        g += (f'<path d="M{x-4} {y+5} h8" stroke="{INK}" stroke-width="2.4" stroke-linecap="round"/>' if squeeze
              else f'<path d="M{x-4} {y+4} Q{x} {y+8} {x+4} {y+4}" stroke="{INK}" stroke-width="2.4" fill="none" stroke-linecap="round"/>')
    return g


def drop(x, y, s=1.0, face=True):
    """물방울"""
    g = (f'<g transform="translate({x},{y}) scale({s})"><path d="M0 -20 C9 -6 14 1 14 8 A14 14 0 0 1 -14 8 C-14 1 -9 -6 0 -20Z" '
         f'fill="#a9d6f0" stroke="#4f8db3" stroke-width="2.8"/>')
    if face:
        g += f'<circle cx="-4" cy="6" r="1.9" fill="{INK}"/><circle cx="4" cy="6" r="1.9" fill="{INK}"/>'
    return g + "</g>"


def table(y=470):
    return (f'<rect x="0" y="{y}" width="{W}" height="{H-y}" fill="#d9b98c"/>'
            f'<rect x="0" y="{y}" width="{W}" height="10" fill="#c49e6c"/>')


def plate(x, y, rx=120):
    return (f'<ellipse cx="{x}" cy="{y}" rx="{rx}" ry="{rx*0.24}" fill="#fff" stroke="{INK}" stroke-width="4"/>'
            f'<ellipse cx="{x}" cy="{y-2}" rx="{rx*0.72}" ry="{rx*0.15}" fill="none" stroke="#d8d1c3" stroke-width="3"/>')


def fridge(x, y):
    return (f'<g transform="translate({x},{y})"><rect x="0" y="0" width="130" height="250" rx="16" fill="#eef4f8" stroke="{INK}" stroke-width="4.5"/>'
            f'<line x1="0" y1="92" x2="130" y2="92" stroke="{INK}" stroke-width="4"/>'
            f'<rect x="104" y="30" width="9" height="40" rx="4" fill="{INK}"/><rect x="104" y="116" width="9" height="56" rx="4" fill="{INK}"/>'
            '<g stroke="#6aa6cf" stroke-width="3.5" stroke-linecap="round"><path d="M50 30 v34 M35 39 l30 16 M35 55 l30 -16"/></g></g>')


def steamer(x, y):
    return (f'<g transform="translate({x},{y})">'
            '<g stroke="#b9c7cf" stroke-width="7" fill="none" stroke-linecap="round" opacity=".9">'
            '<path d="M-60 -150 c-18 -20 18 -36 0 -58"/><path d="M0 -160 c-18 -20 18 -36 0 -58"/><path d="M60 -150 c-18 -20 18 -36 0 -58"/></g>'
            f'<path d="M-150 -30 L-138 70 Q0 92 138 70 L150 -30Z" fill="#d7b47a" stroke="{INK}" stroke-width="4.5" stroke-linejoin="round"/>'
            '<path d="M-146 4 Q0 26 146 4 M-142 38 Q0 60 142 38" stroke="#b08a52" stroke-width="4" fill="none"/>'
            f'<ellipse cx="0" cy="-30" rx="150" ry="28" fill="#e9d2a6" stroke="{INK}" stroke-width="4.5"/></g>')


def sparkles(pts, color="#f3b43f"):
    out = []
    for x, y in pts:
        out.append(f'<path d="M{x} {y-12} L{x+3} {y-3} L{x+12} {y} L{x+3} {y+3} L{x} {y+12} L{x-3} {y+3} L{x-12} {y} L{x-3} {y-3}Z" fill="{color}"/>')
    return "".join(out)


def svg(inner, bg):
    return (f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg" role="img" aria-hidden="true">'
            f'<rect width="{W}" height="{H}" fill="{bg}"/>{inner}</svg>')


# ---------------------------------------------------------------- episode 1

def panel1():
    art = table() + plate(470, 470, 130) + mallang(470, 420, 1.0, "worry", hard=True) + kid(170, 250, 1.15, "surprised", hold="hard")
    art += (f'<text x="292" y="330" font-family="Jua, sans-serif" font-size="30" fill="#8f8577" transform="rotate(-8 292 330)">똑똑!</text>'
            '<path d="M268 350 l-10 -10 M276 342 l-4 -14" stroke="#8f8577" stroke-width="3.5" stroke-linecap="round"/>')
    return svg(art, "#fdf6ec"), [
        ("kid", "어제 산 떡이 돌덩이가 됐어!", 6, 6, "bl"),
        ("mal", "나… 밤새 냉장고에 있었거든…", 48, 22, "br"),
    ]


def panel2():
    art = table() + mallang(170, 400, 1.05, "talk", arm="point")
    art += f'<circle cx="480" cy="230" r="170" fill="#fff" stroke="{INK}" stroke-width="5"/>'
    art += f'<path d="M352 342 L300 394" stroke="{INK}" stroke-width="10" stroke-linecap="round"/>'
    pts = [(420, 170), (470, 150), (525, 175), (400, 225), (455, 215), (510, 230), (565, 220), (430, 280), (490, 285), (545, 280), (470, 330)]
    art += "".join(bead(x, y, 20) for x, y in pts)
    return svg(art, "#f6f1e7"), [
        ("mal", "내 몸속엔 ‘전분’이라는 작은 알갱이들이 잔뜩 살고 있어.", 4, 6, "bl"),
    ]


def panel3():
    art = '<g stroke="#f5c18a" stroke-width="5" fill="none" stroke-linecap="round" opacity=".7">'
    art += "".join(f'<path d="M{x} 520 c-14 -22 14 -40 0 -64"/>' for x in (60, 660))
    art += "</g>"
    pts = [(150, 250), (300, 230), (450, 262), (600, 236), (220, 360), (380, 345), (545, 372), (120, 470), (300, 480), (470, 490), (630, 466)]
    for i, (x, y) in enumerate(pts):
        art += bead(x, y, 22)
    dpts = [(225, 245), (375, 250), (525, 250), (300, 360), (465, 360), (210, 478), (385, 488), (555, 482), (630, 350), (100, 360)]
    art += "".join(drop(x, y, 1.15) for x, y in dpts)
    return svg(art, "#fff3e4"), [
        ("cap", "따뜻할 때", 3, 4, None),
        ("nar", "알갱이들이 물방울과 손잡고 느슨하게 풀어져 있어요. 그래서 갓 만든 떡은 말랑말랑!", 26, 4, None),
    ]


def panel4():
    art = '<g stroke="#9cc4e0" stroke-width="3.5" stroke-linecap="round">'
    for x, y in ((80, 120), (640, 160), (110, 470), (620, 470)):
        art += f'<path d="M{x} {y-14} v28 M{x-12} {y-7} l24 14 M{x-12} {y+7} l24 -14"/>'
    art += "</g>"
    art += f'<rect x="190" y="200" width="340" height="250" rx="40" fill="#f7f1e2" stroke="#c9b894" stroke-width="3" stroke-dasharray="8 8"/>'
    for r in range(5):
        for c in range(7):
            art += bead(230 + c * 44 + (r % 2) * 10, 236 + r * 44, 19, squeeze=True)
    art += drop(150, 250, 1.05) + drop(575, 230, 1.05) + drop(140, 400, 1.05) + drop(585, 400, 1.05)
    art += '<g stroke="#4f8db3" stroke-width="3" stroke-linecap="round"><path d="M172 252 l-14 -4 M171 402 l-14 2 M552 232 l14 -4 M562 402 l14 2"/></g>'
    return svg(art, "#eaf3f9"), [
        ("cap", "차가워지면", 3, 4, None),
        ("nar", "알갱이들이 물방울을 밀어내고 꽉 뭉쳐요. 이걸 ‘전분의 노화’라고 해요.", 26, 4, None),
        ("tag", "0~5℃ 냉장고 온도에서 가장 빨라요!", 22, 87, None),
    ]


def panel5():
    art = steamer(450, 400) + mallang(450, 352, 0.9, "relax")
    art += sparkles([(330, 250), (580, 255)])
    art += kid(120, 280, 1.0, "happy")
    return svg(art, "#f3f7f2"), [
        ("mal", "아~ 다시 풀린다~", 52, 8, "bl"),
        ("kid", "열이랑 물을 다시 주면 되는구나!", 3, 8, "bl"),
        ("tag", "찜기 5분이면 말랑!", 56, 87, None),
    ]


def panel6():
    art = table() + plate(250, 470, 120)
    for i, x in enumerate((200, 250, 300)):
        art += f'<rect x="{x-22}" y="440" width="44" height="26" rx="12" fill="#f7f3ea" stroke="{INK}" stroke-width="4"/>'
    art += kid(250, 220, 0.95, "happy", hold="tteok") + fridge(470, 210)
    art += mallang(425, 438, 0.58, "happy", arm="up")
    return svg(art, "#fdf6ec"), [
        ("mal", "남은 떡은 냉장고 말고 냉동실로! 얼면 거의 안 굳어.", 47, 3, "bl"),
        ("kid", "냉장고가 범인이었네!", 3, 4, "bl"),
    ]


EPISODE = {
    "no": 1,
    "title": "떡은 왜 돌덩이가 될까?",
    "panels": [panel1, panel2, panel3, panel4, panel5, panel6],
    "text": [
        "떡이 딱딱해지는 건 상해서가 아니라 떡 속 전분 알갱이 때문이에요.",
        "따뜻할 때 전분 알갱이는 물과 어울려 느슨하게 풀어져 있어서 떡이 말랑해요.",
        "차가워지면 알갱이들이 물을 밀어내고 다시 촘촘하게 뭉치는데, 이걸 ‘전분의 노화’라고 해요. 0~5℃, 냉장고 온도에서 가장 빨리 일어나요.",
        "그래서 굳은 떡은 찜기에 5분 정도 쪄서 열과 수분을 다시 주면 말랑해지고, 남은 떡은 냉장고보다 냉동실에 보관하는 게 좋아요.",
    ],
}

# ---------------------------------------------------------------- page

CSS = """
:root{--bg:#ffffff;--fg:#2b2620;--muted:#7d766a;--line:#ebe5d8;--accent:#3c5b45;--accent-soft:#e3ebe1;--paper:#ffffff;--ink:#4a4038}
@media (prefers-color-scheme: dark){:root:not([data-theme="light"]){--bg:#1b1a17;--fg:#ece7dc;--muted:#a39b8c;--line:#38342e;--accent:#8db396;--accent-soft:#2b3a2f;color-scheme:dark}}
:root[data-theme="dark"]{--bg:#1b1a17;--fg:#ece7dc;--muted:#a39b8c;--line:#38342e;--accent:#8db396;--accent-soft:#2b3a2f;color-scheme:dark}
*{box-sizing:border-box}
body{margin:0;background:var(--bg);color:var(--fg);font-family:'Noto Sans KR',sans-serif;word-break:keep-all}
.wrap{max-width:720px;margin:0 auto;padding-inline:16px;padding-block:28px 56px}
.ep-head{text-align:center;margin-bottom:22px}
.ep-head .corner{display:inline-block;font-family:Jua,sans-serif;font-size:1rem;color:var(--accent);background:var(--accent-soft);padding:4px 14px;border-radius:999px}
.ep-head h1{font-family:Jua,sans-serif;font-weight:400;font-size:clamp(1.7rem,6vw,2.3rem);margin:12px 0 4px;line-height:1.3}
.ep-head p{margin:0;color:var(--muted);font-size:.9rem}
.strip{display:flex;flex-direction:column;gap:18px}
.panel{position:relative;border:4px solid #4a4038;border-radius:18px;overflow:hidden;background:#fff;container-type:inline-size}
.panel svg{display:block;width:100%;height:auto}
.b{position:absolute;font-family:Jua,'Noto Sans KR',sans-serif;font-weight:400;color:#2b2620;line-height:1.3;font-size:max(15px,4.2cqw)}
.b.kid,.b.mal{background:#fff;border:3px solid #4a4038;border-radius:22px;padding:.45em .8em;max-width:46%}
.b.mal{background:#fffbe8}
.b.kid::after,.b.mal::after{content:"";position:absolute;width:18px;height:18px;background:inherit;border:inherit;border-top:none;border-left:none;bottom:-11px;transform:rotate(45deg)}
.b.bl::after{left:22%;transform:rotate(45deg)}
.b.br::after{right:22%;transform:rotate(45deg)}
.b.cap{font-family:Jua,sans-serif;font-weight:400;background:#4a4038;color:#fff;border-radius:10px;padding:.3em .8em}
.b.nar{background:rgba(255,255,255,.94);border:3px solid #4a4038;border-radius:12px;padding:.5em .8em;max-width:72%}
.b.tag{font-family:Jua,sans-serif;font-weight:400;background:#3c5b45;color:#fff;border-radius:999px;padding:.3em 1em;font-size:max(14px,3.6cqw)}
.explain{margin-top:30px;border-top:2px solid var(--fg);padding-top:16px}
.explain h2{font-size:1rem;margin:0 0 10px}
.explain p{margin:0 0 10px;line-height:1.8;font-size:.98rem}
.cast{display:flex;gap:10px;flex-wrap:wrap;margin-top:18px;font-size:.84rem;color:var(--muted)}
.cast span{border:1px solid var(--line);border-radius:999px;padding:3px 10px}
"""


def bubble(kind, text, left, top, tail):
    cls = f"b {kind}" + (f" {tail}" if tail else "")
    return f'<div class="{cls}" style="left:{left}%;top:{top}%">{e(text)}</div>'


def episode_html(ep, fonts_css):
    panels = []
    for i, fn in enumerate(ep["panels"], 1):
        art, bubbles = fn()
        alt = " / ".join(t for _, t, *_ in bubbles)
        panels.append(f'<figure class="panel" aria-label="{i}컷: {e(alt)}" style="margin:0">{art}{"".join(bubble(*b) for b in bubbles)}</figure>')
    text = "".join(f"<p>{e(t)}</p>" for t in ep["text"])
    return f"""<title>말랑이의 부엌 과학 {ep['no']}화</title>
{fonts_css}
<style>{CSS}</style>
<main class="wrap">
  <header class="ep-head">
    <span class="corner">말랑이의 부엌 과학</span>
    <h1>{ep['no']}화. {e(ep['title'])}</h1>
    <p>식탁노트 만화 코너</p>
  </header>
  <div class="strip">{''.join(panels)}</div>
  <section class="explain">
    <h2>만화로 본 내용, 글로 한 번 더</h2>
    {text}
    <div class="cast"><span>말랑이 · 감자떡</span><span>하나 · 궁금한 게 많은 아이</span><span>전분 알갱이들</span></div>
  </section>
</main>
"""


GOOGLE = ('<link rel="preconnect" href="https://fonts.googleapis.com"><link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>'
          '<link href="https://fonts.googleapis.com/css2?family=Gaegu:wght@700&family=Jua&family=Noto+Sans+KR:wght@400;700&display=swap" rel="stylesheet">')


def local_fonts(font_dir):
    fd = pathlib.Path(font_dir)
    return ("<style>"
            f"@font-face{{font-family:Jua;src:url('file://{fd}/jua/files/jua-korean-400-normal.woff2')}}"
            f"@font-face{{font-family:Gaegu;font-weight:700;src:url('file://{fd}/gaegu/files/gaegu-korean-700-normal.woff2')}}"
            "</style>")


if __name__ == "__main__":
    mode, out = sys.argv[1], pathlib.Path(sys.argv[2])
    if mode == "page":
        out.write_text(episode_html(EPISODE, GOOGLE), encoding="utf-8")
    else:
        from playwright.sync_api import sync_playwright
        font_dir = sys.argv[3]
        tmp = out.with_suffix(".tmp.html")
        tmp.write_text("<!doctype html><meta charset=utf-8>" + episode_html(EPISODE, local_fonts(font_dir)), encoding="utf-8")
        with sync_playwright() as p:
            b = p.chromium.launch()
            pg = b.new_page(viewport={"width": 720, "height": 900}, device_scale_factor=1)
            pg.goto(f"file://{tmp}")
            pg.wait_for_timeout(600)
            pg.locator(".strip").screenshot(path=str(out))
            b.close()
        tmp.unlink()
    print("ok", out)
