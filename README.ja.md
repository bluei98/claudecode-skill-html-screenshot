# 🖼️ html-screenshot

> ローカル HTML を PC・Mobile ビューポートでレンダリングし、**横並び合成の 1 枚の画像** として書き出す Claude Code スキル。

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

## なぜ作ったのか

モバイル対応のスクリーンショットは通常、DevTools と外部画像ツールを行き来したり、デバイスごとに別ファイルとして書き出す必要があり、PR・ブログ・チャットに貼ったときに視認性が落ちがちです。**1 枚の合成画像** は同じ高さでコントラストのあるキャンバスに並んで配置されるため、一目で把握でき、どこにでも綺麗に埋め込めます。

```
 ┌──────────────────────────┐ ┌──────┐
 │                          │ │      │
 │           PC             │ │ Mob  │   ← 単一の PNG/JPEG
 │       (1920×1080)        │ │ ile  │     余白付きキャンバス、グラデーション背景
 │                          │ │      │     パネル高さを自動正規化
 └──────────────────────────┘ └──────┘
```

## 主な機能

- ⚡ **コマンド 1 つで 1 枚の画像** PC + Mobile を横並び合成
- 🎨 **背景プリセット 14 種** + 単色・グラデーションのカスタム指定 (diagonal / vertical / horizontal)
- 📐 **パネル高さの自動正規化** PC と Mobile が綺麗に揃う(アップスケールなし)
- 📱 **タブレットパネル オプション** (`--tablet`) — PC と Mobile の間に挿入
- 🌐 **ローカル HTTP サーバー** を自動起動 — 相対パスの `CSS / JS / img / fetch` がそのまま動作 (`file://` の罠を回避)
- 📂 **ファイルまたはフォルダ入力** — `.html` を再帰探索、出力は元のツリー構造を保持
- 🔄 **フルページ または ビューポート** キャプチャ (`--full-page`)
- 🧩 **デバイス別個別保存** モード (`--separate`) — 元のピクセル解像度を保持
- 🤖 **Claude Code 専用** — `/html-screenshot <path>` で呼び出し

## クイックスタート

```bash
# 単一ファイル → 元ファイル隣に ./index.png
/html-screenshot ./index.html

# フォルダ → ./site/screenshots/{tree}/{stem}.png
/html-screenshot ./site/ --full-page --tablet

# 洒落たプリセット背景 + PC サイズのカスタム
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

## インストール

```bash
pip install playwright pillow
python -m playwright install chromium
```

フォルダを `~/.claude/skills/html-screenshot/` に配置するか、git サブモジュールとして接続してください。

## トリガー

`/html-screenshot` · `HTML スクリーンショット` · `HTML キャプチャ` · `ウェブページ キャプチャ` · `PC・モバイル キャプチャ`

## フラグ

| フラグ | デフォルト | 説明 |
|--------|------------|------|
| `<path>` | — | (必須) HTML ファイルまたはディレクトリ |
| `--separate` | off | 合成せずデバイス別に個別ファイル保存 |
| `--full-page` | off | ビューポートではなくスクロール領域全体をキャプチャ |
| `--pc-size <WxH>` | `1920x1080` | PC ビューポート |
| `--mobile-size <WxH>` | `375x812` | Mobile ビューポート (iPhone X クラス) |
| `--tablet` | off | PC と Mobile の間にタブレットパネルを追加 |
| `--tablet-size <WxH>` | `768x1024` | タブレットビューポート |
| `--only <pc\|mobile\|tablet>` | — | 指定デバイスのみキャプチャ (繰り返し可) |
| `--gap <px>` | `60` | 合成時のパネル間隔 |
| `--padding <px>` | `80` | キャンバス外周の余白 |
| `--canvas-size <WxH>` | — | 最終画像サイズを固定(例:`854x533`)。合成をアスペクト比維持でコンテイン縮小し、背景でレターボックス。ブログサムネイル / OG 画像規格に便利 |
| `--bg <value>` | `slate` | 背景 — プリセット名 / 単色 / グラデーション |
| `--out <dir>` | — | 出力ディレクトリの指定 |
| `--format <png\|jpeg>` | `png` | 画像フォーマット |
| `--quality <1-100>` | `90` | JPEG 品質 |
| `--wait <ms>` | `300` | ロード後の追加待機 (アニメーション対応) |
| `--device-scale <n>` | auto | DPR の強制指定 (デフォルト: PC=1, Mobile/Tablet=2) |
| `--port <n>` | ランダム | ローカル HTTP サーバーのポート |
| `--json` | off | マシンリーダブルな JSON サマリーを出力 |

## 背景

`--bg` は 3 種類の指定方法に対応します:

### 1. プリセット

| プリセット | 種別 | 色 |
|-----------|------|-----|
| `slate` *(デフォルト)* | solid | `#e2e8f0` |
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

### 2. 単色

CSS 名 または `#hex`:

```bash
--bg "#1e293b"
--bg "lavender"
```

### 3. グラデーション

`color1,color2[,direction]` (direction は `diagonal` *(デフォルト)* / `vertical` / `horizontal`):

```bash
--bg "#0f172a,#1e293b,vertical"
--bg "#667eea,#764ba2"          # diagonal
```

## 出力ルール

| 入力 | デフォルト (合成) | `--separate` 指定時 |
|------|------------------|---------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

合成モードでは、各パネルを **最も小さいパネルの高さ** に合わせてダウンスケール(アップスケールはなし)した上で、PC → Tablet → Mobile の順に左→右に配置します。

## ヒント

> 💡 長いページには `--full-page` を、プレゼン用の絵作りには `--bg dark --padding 40` の組み合わせがおすすめです。
>
> 💡 `--separate` モードはデバイス別の元ピクセル解像度をそのまま保持 — さらなる合成用の素材が必要な場合に便利。
>
> 💡 ローカル HTTP サーバーはランダムポートで起動し、キャプチャ後に自動シャットダウンされます(プロセス残存なし)。

## ロードマップ

- [ ] デバイスクローム(PC のブラウザフレーム、モバイルのベゼル)
- [ ] パネルのドロップシャドウ
- [ ] WebP 出力
- [ ] スクロールアニメーションの GIF / MP4

PR 歓迎です。

## ライセンス

[MIT](LICENSE) © Haru

## 作者

**Haru** — メイカーやライターのためのツールを作っています。

- 🧵 Threads · [@life.of.haru](https://www.threads.net/@life.of.haru)
- 📷 Instagram · [@life.of.haru](https://www.instagram.com/life.of.haru)
- ✍️ ブログ · [harulogs.com](https://harulogs.com/ja)

このスキルが時間の節約になったら、リポジトリへの ⭐ をいただけると嬉しいです。
