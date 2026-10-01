# 식탁노트 (siktaknote.com)

부엌에서 바로 쓰는 생활의 지혜를 정리하는 블로그. GitHub Pages로 배포한다.

## 글 추가하는 법

1. `content/NN-slug.md` 파일을 만든다 (기존 글의 앞부분 형식을 그대로 따른다).
2. 카드 이미지: `python3 tools/cards.py` → `assets/cards/`
3. 페이지 생성: `python3 tools/build.py` → `index.html`, `posts/`, `sitemap.xml`
4. 커밋하고 `main`에 푸시하면 몇 분 안에 사이트에 반영된다.

## 본문 표기

- `[[card:id]]` — 앞부분 `cards:`에 정의한 카드 이미지
- `[[photo: 설명]]` — 아직 사진이 없는 자리 (사이트에는 안 보이고 주석으로 남음)
- `[[img:파일명|설명]]` — `assets/photos/`에 넣은 실사진
