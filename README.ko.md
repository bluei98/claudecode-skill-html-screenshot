# html-screenshot

> **한국어** · [日本語](README.ja.md) · [English](README.md)

로컬 HTML 파일을 PC와 모바일 뷰포트로 렌더링한 뒤, 두 화면을 좌우로 나란히 합성한 단일 PNG/JPEG로 내보내는 Claude Code 스킬입니다. Playwright(Chromium headless)와 자동 로컬 HTTP 서버를 사용해 상대경로 `CSS/JS/img/fetch`가 그대로 동작합니다.

## 빠른 시작

```text
/html-screenshot ./index.html
/html-screenshot ./site/ --full-page --tablet
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

기본 출력: 단일 파일 입력 시 원본 옆에 `{stem}.png`, 폴더 입력 시 `{folder}/screenshots/` 아래에 트리 구조 유지하며 저장.

## 설치

자체 완결 디렉토리로 동작합니다. 런타임 의존성:

```bash
pip install playwright pillow
python -m playwright install chromium
```

폴더를 `~/.claude/skills/html-screenshot/` 위치에 두거나 git 서브모듈로 연결하면 됩니다 (아래 참고).

## 트리거

`/html-screenshot`, "HTML 스크린샷", "HTML 캡처", "HTML 캡쳐", "html screenshot", "render HTML"

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
| `--only <pc\|mobile\|tablet>` | — | 지정한 디바이스만 캡처 (반복 가능) |
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

## 배경 색상

`--bg`는 세 가지 형태를 지원합니다:

**프리셋** (큐레이션):

| 프리셋 | 종류 | 색상 |
|--------|------|------|
| `slate` (기본) | solid | `#e2e8f0` |
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

**커스텀 단색**: CSS 색상명 또는 `#hex` — `--bg "#1e293b"`

**커스텀 그라디언트**: `color1,color2[,direction]` — direction은 `diagonal`(기본), `vertical`, `horizontal` 중 하나 — `--bg "#0f172a,#1e293b,vertical"`

## 출력 규칙

| 입력 | 기본 출력 (합성) | `--separate` 사용 시 |
|------|-----------------|---------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

합성 모드에서는 패널들을 **가장 작은 패널의 높이**에 맞춰 다운스케일(업스케일 없음)한 뒤, PC → Tablet → Mobile 순으로 캔버스 안에 좌우로 배치합니다.

## 참고

- 입력 디렉토리를 루트로 로컬 HTTP 서버가 랜덤 포트로 자동 시작되며 캡처 후 종료됩니다. `file://` 프로토콜의 CORS·fetch 이슈를 회피합니다.
- 긴 페이지는 `--full-page` 사용을 권장하며, 시연용 이미지는 `--bg dark --padding 40` 조합이 깔끔합니다.
- `--separate` 모드는 디바이스별 원본 픽셀 해상도를 그대로 유지합니다 (리사이즈 없음).

## 왜 만들었나

모바일 반응형 스크린샷은 보통 DevTools와 외부 툴을 오가며 작업하거나, 디바이스별로 개별 파일을 만들어야 해서 채팅·PR·블로그에 첨부할 때 가독성이 떨어집니다. 한 장에 동일 높이로 나란히 합성된 이미지는 한눈에 파악되고 어디든 깔끔하게 임베드됩니다.

## 라이선스

MIT
