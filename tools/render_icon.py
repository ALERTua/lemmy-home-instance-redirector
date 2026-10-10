# /// script
# requires-python = ">=3.11"
# dependencies = ["selenium==4.49.*"]
# ///
"""Render src/icons/icon.svg into PNG files with a transparent background.

Usage: uv run --python 3.13 tools/render_icon.py

addons.mozilla.org takes the icon of the listing only as PNG or JPG. Firefox draws the SVG
on a canvas, so the PNG keeps the transparency.
"""

import base64
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import firefox as ff  # noqa: E402

ROOT = Path(__file__).resolve().parent.parent
SVG = ROOT / "src" / "icons" / "icon.svg"
OUT = ROOT / "docs"
SIZES = (128,)

DRAW = """
const [svg, size, done] = arguments;
const img = new Image();
img.onload = () => {
  const canvas = document.createElement('canvas');
  canvas.width = canvas.height = size;
  canvas.getContext('2d').drawImage(img, 0, 0, size, size);
  done(canvas.toDataURL('image/png'));
};
img.onerror = () => done(null);
img.src = 'data:image/svg+xml;base64,' + svg;
"""


def main():
    svg = base64.b64encode(SVG.read_bytes()).decode()
    with ff.session() as driver:
        driver.switch_to.window(driver.window_handles[-1])
        driver.get("about:blank")
        for size in SIZES:
            data_url = driver.execute_async_script(DRAW, svg, size)
            if not data_url:
                sys.exit(f"Firefox could not draw {SVG}")
            path = OUT / f"icon-{size}.png"
            path.write_bytes(base64.b64decode(data_url.split(",", 1)[1]))
            print("saved", path.relative_to(ROOT))


if __name__ == "__main__":
    main()
