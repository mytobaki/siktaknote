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

### 직접 올린 사진을 대표 이미지로 (hero.file)
사진을 `assets/photos/<slug>.jpg`(가로 1280px)로 넣고, 부엌 꿀팁은 `hero: {file, alt, credit}`, 로컬 이야기는 `hero: {card: hero, file, alt, credit}`(사진 위에 제목)로 쓴다. 캔바 AI 이미지는 credit 에 그렇게 밝히고, 장소 이미지는 "실제 장소 사진이 아니에요"를 붙인다.

### 대표 이미지에 사진 배경 (hero.bg)
`hero: {card: hero, alt, bg: <Unsplash photo-id>, credit: 촬영자}` 로 쓰면 카드 PNG 대신 사진 위에 제목(`cards` 의 hero 카드 title/sub)을 얹어 보여줍니다. 사진은 Unsplash 에서 불러오며, 불러오지 못하면 초록 바탕 위에 제목만 남습니다. 공유 미리보기(og:image)에는 사진만 쓰입니다.

## 애드센스 (tools/site.json)

애드센스 가입 후 게시자 ID를 `tools/site.json` 에 넣고 `python3 tools/build.py` 를 실행하면 모든 페이지 head 에 애드센스 코드와 `google-adsense-account` 메타태그가 들어가고, 루트에 `ads.txt` 가 만들어진다.

    {"adsense_client": "ca-pub-1234567890123456"}

비워 두면(기본) 광고 코드와 ads.txt 는 만들어지지 않는다. 소개·개인정보처리방침·문의 페이지 문구는 `tools/build.py` 의 ABOUT / PRIVACY / CONTACT 에 있고, 문의 이메일은 `CONTACT_EMAIL` 한 곳에서 바꾼다.

## 검색 등록 (tools/site.json)

- `google_site_verification`: 구글 서치 콘솔 "HTML 태그" 방식의 content 값 → 모든 페이지에 `google-site-verification` 메타태그
- `naver_site_verification`: 네이버 서치어드바이저 "HTML 태그" 방식의 content 값 → `naver-site-verification` 메타태그
- 빌드하면 `sitemap.xml`(글의 `updated` 날짜를 lastmod로 사용)과 `rss.xml`(네이버 RSS 제출용)이 함께 만들어진다.
- 글 내용을 크게 고치면 front matter에 `updated: YYYY-MM-DD` 를 적는다 (글 상단 "수정" 날짜, 구조화 데이터 dateModified, sitemap 에 반영).
