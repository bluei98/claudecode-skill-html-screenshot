# 🖼️ html-screenshot

> 로컬 HTML을 PC와 모바일 뷰포트로 렌더링해 **좌·우 합성 단일 이미지**로 내보내는 Claude Code 스킬.

<p align="left">
  <a href="README.md"><img alt="English" src="https://img.shields.io/badge/lang-English-blue.svg"></a>
  <a href="README.ko.md"><img alt="한국어" src="https://img.shields.io/badge/lang-한국어-red.svg"></a>
  <a href="README.ja.md"><img alt="日本語" src="https://img.shields.io/badge/lang-日本語-green.svg"></a>
</p>

<p align="left">
  <img alt="License" src="https://img.shields.io/badge/license-MIT-blue.svg">
  <img alt="Python" src="https://img.shields.io/badge/python-3.9%2B-blue.svg">
  <img alt="Playwright" src="https://img.shields.io/badge/playwright-chromium-2EAD33.svg">
  <img alt="Claude Code" src="https://img.shields.io/badge/Claude%20Code-skill-D97757.svg">
</p>

---

## 왜 만들었나

모바일 반응형 스크린샷은 보통 DevTools와 외부 이미지 툴을 오가며 작업하거나, 디바이스별 개별 파일로 내보내야 해서 PR·블로그·채팅에 첨부할 때 가독성이 떨어집니다. **한 장의 합성 이미지**는 동일한 높이와 대비되는 캔버스 위에 배치되어 한눈에 파악되고 어디든 깔끔하게 임베드됩니다.

```
 ┌──────────────────────────┐ ┌──────┐
 │                          │ │      │
 │           PC             │ │ Mob  │   ← 단일 PNG/JPEG
 │       (1920×1080)        │ │ ile  │     여백 있는 캔버스, 그라디언트 배경
 │                          │ │      │     높이 자동 정규화
 └──────────────────────────┘ └──────┘
```

## 주요 기능

- ⚡ **명령 한 줄 → 이미지 한 장** PC + 모바일 좌우 합성
- 🎨 **배경 프리셋 14종** + 단색·그라디언트 커스텀 (대각선 / 세로 / 가로)
- 📐 **패널 높이 자동 정규화** PC와 모바일 정렬이 깔끔 (업스케일 없음)
- 📱 **태블릿 패널 옵션** (`--tablet`)으로 PC와 모바일 사이에 추가
- 🌐 **로컬 HTTP 서버** 자동 기동 — 상대경로 `CSS / JS / img / fetch` 정상 동작 (`file://` 이슈 없음)
- 📂 **파일 또는 폴더 입력** — `.html` 재귀 탐색, 출력은 원본 트리 구조 유지
- 🔄 **풀페이지 또는 뷰포트** 캡처 (`--full-page`)
- 🧩 **개별 디바이스 파일** 모드 (`--separate`) — 원본 픽셀 해상도 보존
- 🤖 **Claude Code 전용** — `/html-screenshot <path>` 로 호출

## 빠른 시작

```bash
# 단일 파일 → 원본 옆에 ./index.png
/html-screenshot ./index.html

# 폴더 → ./site/screenshots/{tree}/{stem}.png
/html-screenshot ./site/ --full-page --tablet

# 멋진 프리셋 배경 + PC 해상도 커스텀
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

## 설치

```bash
pip install playwright pillow
python -m playwright install chromium
```

폴더를 `~/.claude/skills/html-screenshot/` 에 배치하거나 git 서브모듈로 연결하세요.

## 트리거

`/html-screenshot` · `HTML 스크린샷` · `HTML 캡처` · `HTML 캡쳐` · `웹페이지 캡처` · `PC/모바일 캡처`

## 플래그

| 플래그 | 기본값 | 설명 |
|--------|--------|------|
| `<path>` | — | (필수) HTML 파일 또는 디렉토리 |
| `--separate` | off | 합성 대신 디바이스별 개별 파일 저장 |
| `--full-page` | off | 뷰포트 대신 전체 스크롤 영역 캡처 |
| `--pc-size <WxH>` | `1920x1080` | PC 뷰포트 크기 |
| `--mobile-size <WxH>` | `375x812` | Mobile 뷰포트 크기 (iPhone X 클래스) |
| `--tablet` | off | PC와 Mobile 사이에 태블릿 패널 추가 |
| `--tablet-size <WxH>` | `768x1024` | 태블릿 뷰포트 크기 |
| `--only <pc\|mobile\|tablet>` | — | 지정 디바이스만 캡처 (반복 가능) |
| `--gap <px>` | `60` | 합성 시 패널 간격 |
| `--padding <px>` | `80` | 캔버스 외곽 여백 |
| `--bg <value>` | `slate` | 배경 — 프리셋명, 단색, 그라디언트 |
| `--out <dir>` | — | 출력 디렉토리 지정 |
| `--format <png\|jpeg>` | `png` | 이미지 포맷 |
| `--quality <1-100>` | `90` | JPEG 품질 |
| `--wait <ms>` | `300` | 로드 후 추가 대기 (애니메이션 대응) |
| `--device-scale <n>` | auto | DPR 강제 지정 (기본: PC=1, Mobile/Tablet=2) |
| `--port <n>` | 랜덤 | 로컬 HTTP 서버 포트 |
| `--json` | off | 머신 리더블 JSON 요약 출력 |

## 배경

`--bg`는 세 가지 형태를 지원합니다:

### 1. 프리셋

| 프리셋 | 종류 | 색상 |
|--------|------|------|
| `slate` *(기본)* | solid | `#e2e8f0` |
| `white` / `black` / `dark` | solid | white / black / `#0f172a` |
| `purple` | gradient | `#667eea → #764ba2` |
| `sunset` | gradient | `#ff7e5f → #feb47b` |
| `ocean` | gradient | `#2193b0 → #6dd5ed` |
| `midnight` | gradient | `#0f2027 → #2c5364` |
| `mint` | gradient | `#a8e6cf → #3ec6e0` |
| `aurora` | gradient | `#a18cd1 → #fbc2eb` |
| `forest` | gradient | `#134e5e → #71b280` |
| `fire` | gradient | `#f12711 → #f5af19` |
| `candy` | gradient | `#ee9ca7 → #ffdde1` |
| `sky` | gradient | `#74b9ff → #a29bfe` |

### 2. 단색

CSS 색상명 또는 `#hex`:

```bash
--bg "#1e293b"
--bg "lavender"
```

### 3. 그라디언트

`color1,color2[,direction]` — direction은 `diagonal` *(기본)*, `vertical`, `horizontal` 중 하나:

```bash
--bg "#0f172a,#1e293b,vertical"
--bg "#667eea,#764ba2"          # 대각선
```

## 출력 규칙

| 입력 | 기본 (합성) | `--separate` 사용 시 |
|------|-------------|---------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

합성 모드에서는 패널을 **가장 작은 패널 높이**에 맞춰 다운스케일(업스케일 없음)한 뒤, PC → Tablet → Mobile 순으로 좌→우 배치합니다.

## 팁

> 💡 긴 페이지는 `--full-page`를 권장하며, 시연용 이미지는 `--bg dark --padding 40` 조합이 깔끔합니다.
>
> 💡 `--separate`는 디바이스별 원본 픽셀 해상도를 그대로 보존 — 추가 합성용 raw 프레임이 필요할 때 유용.
>
> 💡 로컬 HTTP 서버는 랜덤 포트로 시작해 캡처 후 자동 종료됩니다. 프로세스 잔존 없음.

## 로드맵

- [ ] 디바이스 크롬 (PC 브라우저 프레임, 모바일 베젤)
- [ ] 패널 드롭 섀도우
- [ ] WebP 출력
- [ ] 스크롤 애니메이션 GIF / MP4

PR 환영합니다.

## 라이선스

[MIT](LICENSE) © Haru

## 만든 사람

**Haru** — 메이커와 작가들을 위한 도구를 만듭니다.

- 🧵 Threads · [@life.of.haru](https://www.threads.net/@life.of.haru)
- 📷 Instagram · [@life.of.haru](https://www.instagram.com/life.of.haru)
- ✍️ 블로그 · [harulogs.com](https://harulogs.com/ko)

이 스킬이 시간을 아껴줬다면 ⭐ 한 번 부탁드립니다.
