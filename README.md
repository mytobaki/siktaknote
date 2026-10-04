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

## 코너와 로컬 이야기 글

- `category`: `부엌 꿀팁` 또는 `로컬 이야기`
- 로컬 이야기 글은 `section`(떠나는 날 / 그 지역의 맛 / 옛이야기)과 `region`(강원, 경남, 제주 등)을 함께 쓴다.
- 대표 이미지: `hero: {id, alt, credit}`(Unsplash) 또는 `hero: {card: 카드id, alt}`(그 글의 카드 이미지)
- 행사 글은 `info:`(rows, links, checked)로 정보 박스를 넣고, 카드 `type: timeline`으로 타임테이블을 그린다.
- 행사 일정은 공식 사이트나 한국관광공사에서 확인하고, 언론 보도로만 확인한 것은 글에 그렇게 밝힌다.
- 홈 상단 큰 카드는 `featured: true`인 글(없으면 최신 글).

### 대표 이미지에 사진 배경 (hero.bg)
`hero: {card: hero, alt, bg: <Unsplash photo-id>, credit: 촬영자}` 로 쓰면 카드 PNG 대신 사진 위에 제목(`cards` 의 hero 카드 title/sub)을 얹어 보여줍니다. 사진은 Unsplash 에서 불러오며, 불러오지 못하면 초록 바탕 위에 제목만 남습니다. 공유 미리보기(og:image)에는 사진만 쓰입니다.
