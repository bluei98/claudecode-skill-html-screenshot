# html-screenshot

> [한국어](README.ko.md) · **日本語** · [English](README.md)

ローカル HTML ファイルを PC・Mobile ビューポートでレンダリングし、両方のビューを横並びに合成して 1 枚の PNG/JPEG として書き出す Claude Code スキルです。Playwright(Chromium headless)と自動起動するローカル HTTP サーバーを利用するため、相対パスの `CSS/JS/img/fetch` がそのまま動作します。

## クイックスタート

```text
/html-screenshot ./index.html
/html-screenshot ./site/ --full-page --tablet
/html-screenshot ./page.html --bg sunset --pc-size 1440x900
```

デフォルト出力: 単一ファイルなら元ファイルの隣に `{stem}.png`、フォルダ指定なら `{folder}/screenshots/` 配下に元のツリー構造を保ったまま保存。

## インストール

ディレクトリ単体で完結します。実行時依存:

```bash
pip install playwright pillow
python -m playwright install chromium
```

フォルダを `~/.claude/skills/html-screenshot/` に配置するか、git サブモジュールとして接続してください(下記参照)。

## トリガー

`/html-screenshot`, "html screenshot", "HTML スクリーンショット", "HTML キャプチャ", "render HTML"

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

**プリセット名** (キュレーション済み):

| プリセット | 種別 | 色 |
|-----------|------|-----|
| `slate` (デフォルト) | solid | `#e2e8f0` |
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

**カスタム単色**: CSS 名 または `#hex` — `--bg "#1e293b"`

**カスタムグラデーション**: `color1,color2[,direction]`(direction は `diagonal`(デフォルト)/`vertical`/`horizontal`)— `--bg "#0f172a,#1e293b,vertical"`

## 出力ルール

| 入力 | デフォルト出力 (合成) | `--separate` 指定時 |
|------|---------------------|---------------------|
| `./foo.html` | `./foo.png` | `./foo-pc.png`, `./foo-mobile.png` |
| `./site/` | `./site/screenshots/{tree}/{stem}.png` | `./site/screenshots/{tree}/{stem}-{device}.png` |

合成モードでは、各パネルを **最も小さいパネルの高さ** に合わせてダウンスケール(アップスケールはなし)した上で、PC → Tablet → Mobile の順に余白付きキャンバスへ横並び配置します。

## 補足

- 入力ディレクトリをルートとするローカル HTTP サーバーがランダムポートで自動起動し、キャプチャ完了後にシャットダウンされます。`file://` プロトコル特有の CORS / fetch の問題を回避できます。
- 長いページには `--full-page` を、プレゼン用の絵作りには `--bg dark --padding 40` の組み合わせがおすすめです。
- `--separate` モードではデバイス別の元ピクセル解像度がそのまま保持されます(リサイズなし)。

## 開発の動機

モバイル対応のスクリーンショットは通常、DevTools と外部ツールを行き来したり、デバイスごとに別ファイルを作る必要があり、チャット・PR・ブログ記事に貼ったときに視認性が落ちがちでした。同じ高さで横並びに合成された 1 枚の画像は一目で把握でき、どこにでも綺麗に埋め込めます。

## ライセンス

MIT
