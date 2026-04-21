---
name: html-screenshot
description: "HTML 파일/폴더 → PC & Mobile 렌더링 스크린샷 PNG/JPEG export. 로컬 HTTP 서버로 안전하게 렌더링. Trigger: /html-screenshot, 'HTML 스크린샷', 'html screenshot', 'HTML 캡쳐', 'HTML 캡처', '웹페이지 캡처', 'PC/모바일 캡처', 'render HTML'"
---

# HTML Screenshot — Execution Skill

> HTML 파일 또는 폴더를 입력받아 PC·Mobile 뷰포트로 렌더링 후, **좌측 PC + 우측 Mobile**을 한 장에 합성한 스크린샷(PNG/JPEG)을 저장한다.
> Playwright(Chromium headless) + 로컬 HTTP 서버 기반 — 상대경로 CSS/JS/이미지/fetch 모두 정상 동작.
> `--separate` 플래그로 디바이스별 개별 파일 저장도 가능.

## WHEN TRIGGERED — EXECUTE IMMEDIATELY

**DO NOT just display documentation. EXECUTE immediately.**

### Main Flow

1. Parse `$ARGUMENTS` for path + flags
2. If no path provided → call `AskUserQuestion`:
   ```
   캡처할 HTML 파일 또는 폴더 경로를 알려주세요.

   예시:
   1. "./index.html"                            — 단일 파일
   2. "./site/"                                 — 폴더 내 모든 .html 재귀
   3. "./index.html --full-page"                — 풀페이지 스크롤 캡처
   4. "./page.html --pc-size 1440x900"          — PC 해상도 커스텀
   5. "./site/ --tablet --format jpeg"          — 태블릿 추가 + JPEG
   ```
3. Resolve path (절대경로 변환) → `scripts/capture.py` 실행
4. 결과 요약 + 생성 파일 목록 출력

---

## Configuration Defaults

```yaml
pc_size: "1920x1080"       # --pc-size override
mobile_size: "375x812"     # --mobile-size override (iPhone X class)
tablet_size: "768x1024"    # --tablet-size override
full_page: false           # --full-page 있으면 true
format: "png"              # --format jpeg 가능
quality: 90                # JPEG 전용
wait_ms: 300               # 로드 후 대기 시간
device_scale: auto         # PC=1x, Mobile/Tablet=2x (DPR)
devices: [pc, mobile]      # 기본 2종 — --tablet, --only 로 조정
composite: true            # --separate 시 비활성
gap: 60                    # 패널 간격 (px)
padding: 80                # 외곽 여백 (px)
bg: "slate"                # 프리셋명 / 단색 / 그라디언트
```

### 배경 프리셋

| 이름 | 종류 | 색상 |
|------|------|------|
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

직접 지정하려면:
- 단색: `--bg "#1e293b"` 또는 `--bg "white"`
- 그라디언트: `--bg "#667eea,#764ba2"` (대각선 기본)
- 방향 지정: `--bg "#0f172a,#1e293b,vertical"` (vertical/horizontal/diagonal)

## Flag Parsing

Parse from `$ARGUMENTS`:

| Flag | 기본값 | 설명 |
|------|--------|------|
| `<path>` | — | (필수) HTML 파일 또는 디렉토리 |
| `--separate` | off | 합성 대신 디바이스별 개별 파일 저장 |
| `--full-page` | off | 뷰포트 대신 전체 스크롤 영역 캡처 |
| `--pc-size <WxH>` | 1920x1080 | PC 뷰포트 크기 |
| `--mobile-size <WxH>` | 375x812 | Mobile 뷰포트 크기 |
| `--tablet` | off | 태블릿(768x1024) 추가 — 합성 시 PC와 Mobile 사이에 배치 |
| `--tablet-size <WxH>` | 768x1024 | 태블릿 크기 커스텀 |
| `--only <pc\|mobile\|tablet>` | — | 특정 기기만 (반복 가능) — 1개만 있으면 합성 없이 단일 이미지 |
| `--gap <px>` | 60 | 합성 시 패널 간격 |
| `--padding <px>` | 80 | 캔버스 외곽 여백 |
| `--bg <value>` | `slate` | 단색 / 그라디언트 / 프리셋 (아래 참고) |
| `--out <dir>` | — | 커스텀 출력 디렉토리 |
| `--format <png\|jpeg>` | png | 이미지 포맷 |
| `--quality <1-100>` | 90 | JPEG 품질 |
| `--wait <ms>` | 300 | 로드 후 추가 대기 (애니메이션 있을 때) |
| `--device-scale <n>` | auto | DPR 강제 지정 |

---

## Phase 1: Input Resolution (입력 경로 해석)

**EXECUTE these steps:**

### Step 1.1: Path Validation

`$ARGUMENTS` 의 첫 번째 인자를 경로로 해석:

1. 절대경로 변환 (`realpath` 또는 Python `Path.resolve()`)
2. 존재 여부 확인:
   - 파일이면 `.html` / `.htm` 확장자 체크
   - 디렉토리면 `.html`/`.htm` 재귀 검색 (최소 1개 이상)
   - 없으면 에러 → 사용자에게 경로 재확인 요청

### Step 1.2: Output Directory Resolution

**출력 규칙**:

| 입력 | 출력 디렉토리 | 파일명 (기본: 합성) | 파일명 (`--separate`) |
|------|-------------|------|------|
| `./foo.html` (파일) | 원본과 **같은 폴더** | `foo.png` | `foo-pc.png`, `foo-mobile.png` |
| `./site/` (폴더) | `./site/screenshots/` | `{relative}/{stem}.png` | `{relative}/{stem}-{device}.png` |
| `--out <dir>` 지정 | 지정된 디렉토리 | 위와 동일 네이밍 규칙 | 위와 동일 네이밍 규칙 |

- **기본 동작**: 각 HTML당 하나의 합성 이미지 (좌 PC → [Tablet] → 우 Mobile, 상단 정렬, 흰 배경 40px gap)
- **합성 결과 이외의 개별 파일은 자동 삭제됨** — 보관하려면 `--separate` 사용
- 단일 파일 입력 시 `screenshots/` 서브폴더 **없이** 원본 옆에 바로 저장
- 폴더 입력 시 원본 트리 구조를 `screenshots/` 아래에 유지

---

## Phase 2: Screenshot Execution (캡처 실행)

### Step 2.1: Run Capture Script

```bash
python3 "${SKILL_DIR}/scripts/capture.py" "<resolved_path>" \
  [--full-page] \
  [--pc-size WxH] [--mobile-size WxH] \
  [--tablet] [--tablet-size WxH] \
  [--only pc --only mobile] \
  [--out <dir>] \
  [--format png|jpeg] [--quality N] \
  [--wait N] [--device-scale N] \
  [--json]
```

스크립트 내부 동작:
1. 대상 디렉토리를 루트로 **로컬 HTTP 서버** 자동 시작 (포트 자동 할당)
2. Chromium headless 실행 → 각 디바이스 context 생성
3. 각 HTML 파일마다 `http://127.0.0.1:{port}/...` 로 로드 (`networkidle` 대기)
4. 추가 대기 후 스크린샷 저장 (`path`, `full_page`, `type` 지정)
5. 서버 종료 + 브라우저 종료

### Step 2.2: Progress Feedback

Bash tool 로 실행하되 출력을 그대로 사용자에게 중계한다.

대량 캡처 (>10 파일) 이면 실행 전 안내:
```
🔄 {n}개 HTML 파일을 {devices}로 캡처합니다. (예상 소요: ~{n*2}초)
```

### Step 2.3: Error Recovery

| Error | Recovery |
|-------|----------|
| `ModuleNotFoundError: playwright` | `pip install playwright && python3 -m playwright install chromium` 안내 후 중단 |
| `Executable doesn't exist` (브라우저 미설치) | `python3 -m playwright install chromium` 안내 |
| Port already in use | `--port` 플래그로 재시도 제안 |
| HTML 파싱 에러 / JS 무한 로딩 | 스크립트 자체적으로 `load` fallback 후 진행 |
| 경로에 공백/한글 포함 | 스크립트는 `quote()` 로 URL 인코딩 — 문제 없음 |

---

## Phase 3: Result Summary (결과 요약)

### Step 3.1: Summary Table

```markdown
## HTML Screenshots Generated

**입력**: `{path}` ({files_processed}개 파일)
**디바이스**: {devices}  |  **풀페이지**: {full_page}  |  **포맷**: {format}
**소요 시간**: {elapsed}s

| File | PC | Mobile | [Tablet] |
|------|----|----|-----|
| index.html | ✅ index-pc.png (240 KB) | ✅ index-mobile.png (180 KB) | — |
| about.html | ✅ about-pc.png (210 KB) | ✅ about-mobile.png (160 KB) | — |
```

### Step 3.2: Output Paths

모든 생성 파일의 **절대경로**를 코드블록으로 제공해 사용자가 바로 열람 가능하게 한다:

```
/abs/path/to/index-pc.png
/abs/path/to/index-mobile.png
...
```

### Step 3.3: Suggestions

```markdown
### Next Steps
- 풀페이지 캡처가 필요하면 `--full-page` 추가
- 해상도를 변경하려면 `--pc-size 1440x900 --mobile-size 390x844`
- JPEG로 용량 절약: `--format jpeg --quality 85`
- 태블릿 뷰도 필요하면 `--tablet` 추가
```

---

## Language Detection

- 입력 언어 감지 (한/영/일/중)
- 진행 메시지 및 결과 요약을 감지 언어로 출력
- 파일명 생성 규칙은 언어와 무관 (`{stem}-{device}.{ext}` 고정)

---

## Tool Usage

| Tool | Purpose |
|------|---------|
| `Bash` | `python3 scripts/capture.py` 실행 |
| `AskUserQuestion` | 경로 미입력 시 요청 |
| `Read` | (옵션) HTML 내용 미리보기 |

## Reference Files

- `${SKILL_DIR}/scripts/capture.py` — Playwright 기반 캡처 스크립트 (로컬 서버 포함)

---

## Boundaries

**Will:**
- 로컬 HTML 파일/폴더를 PC·Mobile(·Tablet) 뷰포트로 렌더링 후 PNG/JPEG 저장
- 뷰포트 캡처(기본) 또는 풀페이지 스크롤 캡처(`--full-page`) 선택
- 상대경로 에셋(CSS/JS/img/fetch)을 로컬 HTTP 서버로 정상 로드
- 폴더 입력 시 `.html` 재귀 수집 + 원본 트리 구조로 `screenshots/` 하위 저장
- 커스텀 해상도/포맷/품질/대기시간 지원

**Won't:**
- 원격 URL 캡처 (이 스킬은 로컬 HTML 전용 — 원격은 Playwright MCP 사용 권장)
- PDF 변환 (PDF는 별도 요청 필요)
- 다중 페이지 스크롤 애니메이션 GIF 생성
- 인증이 필요한 외부 API 호출이 포함된 HTML의 완전 렌더링 (해당 요청은 실패 또는 부분 렌더링)
- 브라우저 자동 설치 — `playwright install chromium` 은 1회 수동 실행 필요
