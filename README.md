# html-screenshot

> [한국어](README.ko.md) · [日本語](README.ja.md) · **English**

A Claude Code skill that renders local HTML files at PC and Mobile viewports, then composites the two views side-by-side into a single PNG/JPEG. Built on Playwright (Chromium headless) with an automatic local HTTP server so relative `CSS/JS/img/fetch` paths work out of the box.

## Quick start

```text
/html-screenshot ./index.html
/html-screenshot ./site/ --full-page --tablet
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

Default output: `{stem}.png` next to the source file (single-file input) or under `{folder}/screenshots/` mirroring the input tree (folder input).

## Install

The skill ships as a self-contained directory. Required runtime:

```bash
pip install playwright pillow
python -m playwright install chromium
```

Place the folder at `~/.claude/skills/html-screenshot/` (or use as a git submodule — see below).

## Triggers

`/html-screenshot`, "html screenshot", "HTML 스크린샷", "HTML 캡처", "HTML 캡쳐", "render HTML"

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `<path>` | — | (required) HTML file or directory to capture |
| `--separate` | off | Save per-device files instead of compositing |
| `--full-page` | off | Capture full scrollable page instead of viewport |
| `--pc-size <WxH>` | `1920x1080` | PC viewport |
| `--mobile-size <WxH>` | `375x812` | Mobile viewport (iPhone X class) |
| `--tablet` | off | Add a tablet panel between PC and Mobile |
| `--tablet-size <WxH>` | `768x1024` | Tablet viewport |
| `--only <pc\|mobile\|tablet>` | — | Capture only the listed device(s) — repeatable |
| `--gap <px>` | `60` | Spacing between panels in composite |
| `--padding <px>` | `80` | Outer padding of the composite canvas |
| `--bg <value>` | `slate` | Background — preset name, solid color, or gradient |
| `--out <dir>` | — | Override output directory |
| `--format <png\|jpeg>` | `png` | Output format |
| `--quality <1-100>` | `90` | JPEG quality |
| `--wait <ms>` | `300` | Extra delay after page load (animations) |
| `--device-scale <n>` | auto | DPR override (default: PC=1, Mobile/Tablet=2) |
| `--port <n>` | random | Local HTTP server port |
| `--json` | off | Print machine-readable summary |

## Backgrounds

`--bg` accepts three forms:

**Preset names** (curated):

| Preset | Type | Colors |
|--------|------|--------|
| `slate` (default) | solid | `#e2e8f0` |
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

**Custom solid color**: any CSS name or `#hex` — `--bg "#1e293b"`

**Custom gradient**: `color1,color2[,direction]` where direction is `diagonal` (default), `vertical`, or `horizontal` — `--bg "#0f172a,#1e293b,vertical"`

## Output rules

| Input | Default output (composite) | With `--separate` |
|-------|----------------------------|-------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

In composite mode, panels are normalized to the **smallest panel height** (no upscaling), then placed side-by-side: PC → Tablet → Mobile, top-aligned within the padded canvas.

## Notes

- A local HTTP server is spun up on a random free port for the input directory; it is shut down after capture. This avoids `file://` quirks (CORS, fetch).
- For long pages, prefer `--full-page` and consider `--bg dark` with `--padding 40` for a denser presentation image.
- `--separate` retains the original per-device pixel resolution (no resize).

## Why this exists

Mobile responsive screenshots usually live in two places (DevTools then external tools), or are generated as separate files that don't read well in chat/PRs/blog posts. A single composite image with consistent height + a contrasting canvas reads at a glance and embeds cleanly anywhere.

## License

MIT
