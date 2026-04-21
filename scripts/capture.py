#!/usr/bin/env python3
"""
HTML Screenshot Capture — PC & Mobile side-by-side composite via Playwright.

Usage:
  capture.py <path> [options]

<path> can be a single .html file or a directory (recursive .html scan).

Default output: a single composite image per HTML file with PC on the left
and Mobile on the right (Tablet in the middle if --tablet). Top-aligned with
a white gap between panels.

Options:
  --separate             Output per-device files instead of a composite
  --full-page            Capture full scrollable page (default: viewport only)
  --pc-size WxH          PC viewport (default: 1920x1080)
  --mobile-size WxH      Mobile viewport (default: 375x812)
  --tablet               Also capture tablet (768x1024)
  --tablet-size WxH      Override tablet viewport
  --only pc|mobile|tablet  Only capture one device (can repeat)
  --gap N                Gap between panels in composite mode (default: 40)
  --bg <color>           Composite background color (default: white)
  --out <dir>            Custom output directory
  --format png|jpeg      Image format (default: png)
  --quality N            JPEG quality 1-100 (default: 90, png ignored)
  --wait N               Extra wait after load in ms (default: 300)
  --device-scale N       Device pixel ratio (default: 1 for PC, 2 for mobile)
  --port N               Local HTTP server port (default: random free port)
  --json                 Output summary JSON instead of human-readable
"""

from __future__ import annotations

import argparse
import http.server
import json
import os
import socket
import socketserver
import sys
import threading
import time
from pathlib import Path
from urllib.parse import quote


# ---------- Local HTTP server ----------

def _find_free_port() -> int:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


class _QuietHandler(http.server.SimpleHTTPRequestHandler):
    def log_message(self, *_args, **_kwargs):  # silence
        return


def _start_server(root: Path, port: int) -> socketserver.TCPServer:
    handler = lambda *a, **kw: _QuietHandler(*a, directory=str(root), **kw)  # noqa: E731
    # Allow quick restart
    class _Server(socketserver.TCPServer):
        allow_reuse_address = True

    server = _Server(("127.0.0.1", port), handler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


# ---------- Helpers ----------

def _parse_size(s: str) -> tuple[int, int]:
    try:
        w, h = s.lower().split("x")
        return int(w), int(h)
    except Exception as e:  # noqa: BLE001
        raise argparse.ArgumentTypeError(f"invalid size '{s}', expected WxH (e.g. 1920x1080)") from e


def _collect_html_files(target: Path) -> list[Path]:
    if target.is_file():
        if target.suffix.lower() not in (".html", ".htm"):
            raise SystemExit(f"not an HTML file: {target}")
        return [target]
    if target.is_dir():
        files = sorted([p for p in target.rglob("*.html")] + [p for p in target.rglob("*.htm")])
        if not files:
            raise SystemExit(f"no HTML files found under: {target}")
        return files
    raise SystemExit(f"path not found: {target}")


def _resolve_root_and_base(target: Path) -> tuple[Path, Path, bool]:
    """
    Returns (server_root, input_base, is_folder_mode).
    server_root: directory served by HTTP server (covers all HTML files + their assets)
    input_base: directory used for output path resolution
    is_folder_mode: True if user passed a directory (use screenshots/ subdir)
    """
    target = target.resolve()
    if target.is_file():
        return target.parent, target.parent, False
    return target, target, True


def _output_dir_for(
    html_file: Path,
    input_base: Path,
    out_dir: Path | None,
    is_folder_mode: bool,
) -> Path:
    if not is_folder_mode:
        return out_dir if out_dir else html_file.parent
    rel_parent = html_file.relative_to(input_base).parent
    base = out_dir if out_dir else (input_base / "screenshots")
    return base / rel_parent


def _output_path_for(
    html_file: Path,
    input_base: Path,
    out_dir: Path | None,
    is_folder_mode: bool,
    device: str | None,
    fmt: str,
) -> Path:
    folder = _output_dir_for(html_file, input_base, out_dir, is_folder_mode)
    filename = f"{html_file.stem}-{device}.{fmt}" if device else f"{html_file.stem}.{fmt}"
    return folder / filename


BG_PRESETS: dict[str, str] = {
    "slate":    "#e2e8f0",                # default solid
    "white":    "white",
    "black":    "black",
    "dark":     "#0f172a",
    "purple":   "#667eea,#764ba2",        # blue → purple
    "sunset":   "#ff7e5f,#feb47b",        # warm orange
    "ocean":    "#2193b0,#6dd5ed",        # teal
    "midnight": "#0f2027,#2c5364",        # deep blue-gray
    "mint":     "#a8e6cf,#3ec6e0",        # mint → cyan
    "aurora":   "#a18cd1,#fbc2eb",        # lilac → pink
    "forest":   "#134e5e,#71b280",        # deep green
    "fire":     "#f12711,#f5af19",        # red → amber
    "candy":    "#ee9ca7,#ffdde1",        # soft pink
    "sky":      "#74b9ff,#a29bfe",        # cool sky
}


def _resolve_bg(spec: str) -> str:
    return BG_PRESETS.get(spec.strip().lower(), spec)


def _parse_color(spec: str) -> tuple[int, int, int]:
    from PIL import ImageColor
    return ImageColor.getrgb(spec.strip())[:3]


def _make_background(w: int, h: int, bg: str):
    """
    bg may be:
      - solid color (e.g. "white", "#e2e8f0")
      - gradient "color1,color2"         → diagonal (top-left → bottom-right)
      - gradient "color1,color2,DIR"     → DIR in {vertical, horizontal, diagonal}
    """
    from PIL import Image

    parts = [p.strip() for p in bg.split(",")]
    if len(parts) == 1:
        return Image.new("RGB", (w, h), _parse_color(parts[0]))
    c1 = _parse_color(parts[0])
    c2 = _parse_color(parts[1])
    direction = parts[2].lower() if len(parts) >= 3 else "diagonal"
    if direction == "vertical":
        strip = Image.new("RGB", (1, h))
        for y in range(h):
            t = y / max(h - 1, 1)
            strip.putpixel((0, y), tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
        return strip.resize((w, h), Image.BILINEAR)
    if direction == "horizontal":
        strip = Image.new("RGB", (w, 1))
        for x in range(w):
            t = x / max(w - 1, 1)
            strip.putpixel((x, 0), tuple(int(c1[i] + (c2[i] - c1[i]) * t) for i in range(3)))
        return strip.resize((w, h), Image.BILINEAR)
    # diagonal: interpolate via 2×2 corners with bilinear resize
    mid = tuple((c1[i] + c2[i]) // 2 for i in range(3))
    corners = Image.new("RGB", (2, 2))
    corners.putpixel((0, 0), c1)
    corners.putpixel((1, 0), mid)
    corners.putpixel((0, 1), mid)
    corners.putpixel((1, 1), c2)
    return corners.resize((w, h), Image.BILINEAR)


def _composite_images(
    image_paths: list[Path],
    out_path: Path,
    *,
    fmt: str,
    quality: int,
    gap: int,
    bg: str,
    padding: int,
    canvas_size: tuple[int, int] | None = None,
) -> Path:
    from PIL import Image

    imgs = [Image.open(p).convert("RGB") for p in image_paths]
    # Normalize all panels to a shared height (smallest, to avoid upscaling) while
    # preserving aspect ratio. This gives visually balanced PC/Mobile side-by-side.
    target_h = min(img.height for img in imgs)
    normalized = []
    for img in imgs:
        if img.height == target_h:
            normalized.append(img)
        else:
            new_w = round(img.width * target_h / img.height)
            normalized.append(img.resize((new_w, target_h), Image.LANCZOS))
    inner_w = sum(img.width for img in normalized) + gap * (len(normalized) - 1)
    canvas_w, canvas_h = inner_w + padding * 2, target_h + padding * 2
    resolved_bg = _resolve_bg(bg)
    canvas = _make_background(canvas_w, canvas_h, resolved_bg)
    x = padding
    for img in normalized:
        canvas.paste(img, (x, padding))
        x += img.width + gap

    # Fit into a fixed output canvas (contain mode, bg-letterboxed)
    if canvas_size is not None:
        target_w, target_h_out = canvas_size
        src_w, src_h = canvas.size
        scale = min(target_w / src_w, target_h_out / src_h)
        new_w = max(1, int(round(src_w * scale)))
        new_h = max(1, int(round(src_h * scale)))
        scaled = canvas.resize((new_w, new_h), Image.LANCZOS)
        final = _make_background(target_w, target_h_out, resolved_bg)
        final.paste(scaled, ((target_w - new_w) // 2, (target_h_out - new_h) // 2))
        canvas = final

    save_kwargs: dict = {}
    if fmt == "jpeg":
        save_kwargs["quality"] = quality
    canvas.save(out_path, **save_kwargs)
    return out_path


def _url_for(html_file: Path, server_root: Path, port: int) -> str:
    rel = html_file.resolve().relative_to(server_root.resolve())
    # Encode each path segment
    parts = [quote(p) for p in rel.parts]
    return f"http://127.0.0.1:{port}/" + "/".join(parts)


# ---------- Capture ----------

def capture(
    files: list[Path],
    server_root: Path,
    input_base: Path,
    is_folder_mode: bool,
    *,
    port: int,
    devices: list[dict],
    out_dir: Path | None,
    full_page: bool,
    fmt: str,
    quality: int,
    wait_ms: int,
) -> list[dict]:
    from playwright.sync_api import sync_playwright

    results: list[dict] = []
    server = _start_server(server_root, port)
    try:
        with sync_playwright() as p:
            browser = p.chromium.launch(headless=True)
            try:
                for dev in devices:
                    context = browser.new_context(
                        viewport={"width": dev["width"], "height": dev["height"]},
                        device_scale_factor=dev["scale"],
                        user_agent=dev.get("user_agent"),
                        is_mobile=dev.get("is_mobile", False),
                        has_touch=dev.get("has_touch", False),
                    )
                    page = context.new_page()
                    for html_file in files:
                        url = _url_for(html_file, server_root, port)
                        out_path = _output_path_for(html_file, input_base, out_dir, is_folder_mode, dev["name"], fmt)
                        out_path.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            page.goto(url, wait_until="networkidle", timeout=30_000)
                        except Exception:
                            # Fallback: some pages never reach networkidle (long-polling, analytics)
                            page.goto(url, wait_until="load", timeout=30_000)
                        if wait_ms > 0:
                            page.wait_for_timeout(wait_ms)
                        shot_kwargs = {
                            "path": str(out_path),
                            "full_page": full_page,
                            "type": fmt,
                        }
                        if fmt == "jpeg":
                            shot_kwargs["quality"] = quality
                        page.screenshot(**shot_kwargs)
                        results.append({
                            "html": str(html_file),
                            "device": dev["name"],
                            "viewport": f"{dev['width']}x{dev['height']}",
                            "scale": dev["scale"],
                            "full_page": full_page,
                            "output": str(out_path),
                            "size_bytes": out_path.stat().st_size,
                        })
                    context.close()
            finally:
                browser.close()
    finally:
        server.shutdown()
        server.server_close()
    return results


# ---------- Device profiles ----------

def _build_devices(args) -> list[dict]:
    pc = {
        "name": "pc",
        "width": args.pc_size[0],
        "height": args.pc_size[1],
        "scale": args.device_scale or 1,
        "is_mobile": False,
        "has_touch": False,
    }
    mobile = {
        "name": "mobile",
        "width": args.mobile_size[0],
        "height": args.mobile_size[1],
        "scale": args.device_scale or 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": (
            "Mozilla/5.0 (iPhone; CPU iPhone OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        ),
    }
    tablet = {
        "name": "tablet",
        "width": args.tablet_size[0],
        "height": args.tablet_size[1],
        "scale": args.device_scale or 2,
        "is_mobile": True,
        "has_touch": True,
        "user_agent": (
            "Mozilla/5.0 (iPad; CPU OS 16_6 like Mac OS X) "
            "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.6 Mobile/15E148 Safari/604.1"
        ),
    }
    all_devs = {"pc": pc, "mobile": mobile, "tablet": tablet}
    if args.only:
        selected = [all_devs[name] for name in args.only if name in all_devs]
        if not selected:
            raise SystemExit(f"--only: no valid device in {args.only}")
        return selected
    picks = [pc, mobile]
    if args.tablet:
        picks.append(tablet)
    return picks


# ---------- Main ----------

def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Capture PC/Mobile screenshots from HTML files.")
    parser.add_argument("path", type=Path, help="HTML file or directory")
    parser.add_argument("--full-page", action="store_true")
    parser.add_argument("--pc-size", type=_parse_size, default=(1920, 1080))
    parser.add_argument("--mobile-size", type=_parse_size, default=(375, 812))
    parser.add_argument("--tablet", action="store_true")
    parser.add_argument("--tablet-size", type=_parse_size, default=(768, 1024))
    parser.add_argument("--only", action="append", choices=["pc", "mobile", "tablet"])
    parser.add_argument("--out", type=Path, default=None)
    parser.add_argument("--format", choices=["png", "jpeg"], default="png")
    parser.add_argument("--quality", type=int, default=90)
    parser.add_argument("--wait", type=int, default=300, help="Extra wait after load in ms")
    parser.add_argument("--device-scale", type=int, default=0, help="0 = auto (1 pc / 2 mobile)")
    parser.add_argument("--port", type=int, default=0)
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--separate", action="store_true", help="Keep per-device files instead of composing a single side-by-side image")
    parser.add_argument("--gap", type=int, default=60, help="Gap (px) between panels in composite mode")
    parser.add_argument("--padding", type=int, default=80, help="Outer canvas padding (px) in composite mode")
    parser.add_argument("--canvas-size", type=_parse_size, default=None,
                        help="Fixed final image size WxH (e.g. 854x533). Composite is scaled (contain) and letterboxed with the bg to fill this size exactly.")
    parser.add_argument(
        "--bg",
        default="slate",
        help=(
            "Composite background. Accepts: solid (CSS name/#hex), gradient "
            "('color1,color2[,vertical|horizontal|diagonal]'), or a preset name "
            "(slate, white, black, dark, purple, sunset, ocean, midnight, mint, "
            "aurora, forest, fire, candy, sky)."
        ),
    )
    args = parser.parse_args(argv)

    target = args.path.resolve()
    files = _collect_html_files(target)
    server_root, input_base, is_folder_mode = _resolve_root_and_base(target)
    port = args.port or _find_free_port()
    devices = _build_devices(args)

    out_dir = args.out.resolve() if args.out else None
    if out_dir:
        out_dir.mkdir(parents=True, exist_ok=True)

    t0 = time.time()
    results = capture(
        files,
        server_root,
        input_base,
        is_folder_mode,
        port=port,
        devices=devices,
        out_dir=out_dir,
        full_page=args.full_page,
        fmt=args.format,
        quality=args.quality,
        wait_ms=args.wait,
    )

    composites: list[dict] = []
    if not args.separate and len(devices) >= 2:
        # Order panels left→right by visual width (desktop → tablet → mobile)
        order = sorted({d["name"] for d in devices}, key=lambda n: -{"pc": 3, "tablet": 2, "mobile": 1}[n])
        for html_file in files:
            per_device = {r["device"]: Path(r["output"]) for r in results if r["html"] == str(html_file)}
            panels = [per_device[name] for name in order if name in per_device]
            if len(panels) < 2:
                continue
            composite_path = _output_path_for(html_file, input_base, out_dir, is_folder_mode, None, args.format)
            composite_path.parent.mkdir(parents=True, exist_ok=True)
            _composite_images(
                panels,
                composite_path,
                fmt=args.format,
                quality=args.quality,
                gap=args.gap,
                bg=args.bg,
                padding=args.padding,
                canvas_size=args.canvas_size,
            )
            composites.append({
                "html": str(html_file),
                "devices": order,
                "output": str(composite_path),
                "size_bytes": composite_path.stat().st_size,
            })
            # Composite is the user-facing artifact; remove per-device intermediates
            for p in panels:
                try:
                    p.unlink()
                except OSError:
                    pass

    elapsed = time.time() - t0

    summary = {
        "input": str(target),
        "files_processed": len(files),
        "captures": len(results),
        "devices": [d["name"] for d in devices],
        "full_page": args.full_page,
        "mode": "separate" if args.separate else "composite",
        "elapsed_seconds": round(elapsed, 2),
        "results": results,
        "composites": composites,
    }

    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
        return 0

    if composites:
        print(f"✅ Composed {len(composites)} side-by-side image(s) from {len(files)} HTML file(s) in {elapsed:.1f}s")
        for c in composites:
            rel = Path(c["output"])
            try:
                rel = rel.relative_to(Path.cwd())
            except ValueError:
                pass
            kb = c["size_bytes"] / 1024
            devs = " | ".join(c["devices"])
            print(f"  • [{devs}]  →  {rel}  ({kb:.1f} KB)")
    else:
        print(f"✅ Captured {len(results)} image(s) from {len(files)} HTML file(s) in {elapsed:.1f}s")
        for r in results:
            rel = Path(r["output"])
            try:
                rel = rel.relative_to(Path.cwd())
            except ValueError:
                pass
            kb = r["size_bytes"] / 1024
            print(f"  • [{r['device']:>6}] {r['viewport']:>9}  →  {rel}  ({kb:.1f} KB)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
