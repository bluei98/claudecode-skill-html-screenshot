# 🖼️ html-screenshot

> Render local HTML at PC + Mobile viewports and export them **side-by-side** as a single image. A Claude Code skill.

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

## Why

Mobile responsive screenshots usually live in two places — DevTools, then external image tools — or get exported as separate per-device files that don't read well in PRs, blog posts, or chat. **One composite image** with consistent height and a contrasting canvas reads at a glance and embeds cleanly anywhere.

```
 ┌──────────────────────────┐ ┌──────┐
 │                          │ │      │
 │           PC             │ │ Mob  │   ← single PNG/JPEG
 │       (1920×1080)        │ │ ile  │     padded canvas, gradient bg
 │                          │ │      │     height-normalized panels
 └──────────────────────────┘ └──────┘
```

## Features

- ⚡ **One command, one image** — PC + Mobile composited side-by-side
- 🎨 **14 background presets** + custom solid color or gradient (vertical / horizontal / diagonal)
- 📐 **Height-normalized panels** so PC and Mobile align cleanly (no upscaling)
- 📱 **Optional tablet panel** between PC and Mobile (`--tablet`)
- 🌐 **Local HTTP server** auto-spawned per run — relative `CSS / JS / img / fetch` work without `file://` quirks
- 📂 **File or folder input** — recursive `.html` discovery, output mirrors source tree
- 🔄 **Full-page or viewport** capture (`--full-page`)
- 🧩 **Per-device fallback** with `--separate` (keeps original native pixel resolution)
- 🤖 **Built for Claude Code** — invoke via `/html-screenshot <path>`

## Quick start

```bash
# Single file → ./index.png next to source
/html-screenshot ./index.html

# Folder → ./site/screenshots/{tree}/{stem}.png
/html-screenshot ./site/ --full-page --tablet

# Fancy preset background, custom PC size
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

## Install

```bash
pip install playwright pillow
python -m playwright install chromium
```

Place the folder at `~/.claude/skills/html-screenshot/`, or wire it as a git submodule.

## Triggers

`/html-screenshot` · `html screenshot` · `render HTML` · `webpage capture` · `PC mobile capture`

## Flags

| Flag | Default | Description |
|------|---------|-------------|
| `<path>` | — | (required) HTML file or directory |
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

### 1. Preset names

| Preset | Type | Colors |
|--------|------|--------|
| `slate` *(default)* | solid | `#e2e8f0` |
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

### 2. Custom solid

Any CSS color name or `#hex`:

```bash
--bg "#1e293b"
--bg "lavender"
```

### 3. Custom gradient

`color1,color2[,direction]` where direction is `diagonal` *(default)*, `vertical`, or `horizontal`:

```bash
--bg "#0f172a,#1e293b,vertical"
--bg "#667eea,#764ba2"          # diagonal
```

## Output rules

| Input | Default (composite) | With `--separate` |
|-------|---------------------|-------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

In composite mode, panels are normalized to the **smallest panel height** (no upscaling), then placed left → right: PC → Tablet → Mobile.

## Tips

> 💡 For long pages, prefer `--full-page` and consider `--bg dark --padding 40` for a denser presentation image.
>
> 💡 `--separate` retains original per-device pixel resolution — useful when you need the raw frames for further compositing.
>
> 💡 The local HTTP server starts on a random free port and shuts down after capture — no leaked processes.

## Roadmap

- [ ] Optional device chrome (browser frame around PC, phone bezel around Mobile)
- [ ] Drop shadow on panels
- [ ] WebP output
- [ ] Animated GIF / MP4 from scroll-through

PRs welcome.

## License

[MIT](LICENSE) © Haru

## Author

Built by **Haru** — building tools for makers and writers.

- 🧵 Threads · [@life.of.haru](https://www.threads.net/@life.of.haru)
- 📷 Instagram · [@life.of.haru](https://www.instagram.com/life.of.haru)
- ✍️ Blog · [harulogs.com](https://harulogs.com/en)

If this skill saved you time, a ⭐ on the repo means a lot.
