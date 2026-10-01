"""content/*.md 를 읽어 글 목록을 돌려준다 (front matter + 본문)."""
import pathlib

import yaml

ROOT = pathlib.Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"


def load_posts():
    posts = []
    for path in sorted(CONTENT.glob("*.md")):
        text = path.read_text(encoding="utf-8")
        if not text.startswith("---"):
            raise ValueError(f"{path.name}: front matter가 없습니다")
        _, fm, body = text.split("---", 2)
        meta = yaml.safe_load(fm)
        meta["body"] = body.strip()
        meta["source"] = path.name
        meta["date"] = str(meta["date"])
        posts.append(meta)
    posts.sort(key=lambda p: p["order"])
    return posts
