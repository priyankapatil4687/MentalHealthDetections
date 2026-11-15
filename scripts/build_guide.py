"""Crop screenshots and render docs/guide_assets/guide.html to docs/Marathi_User_Guide.pdf (needs Microsoft Edge)."""
from pathlib import Path

from PIL import Image
from playwright.sync_api import sync_playwright

ASSETS = Path(__file__).resolve().parent.parent / "docs" / "guide_assets"
CROPPED = ASSETS / "cropped"
PDF = ASSETS.parent / "Marathi_User_Guide.pdf"
CROPPED.mkdir(exist_ok=True)

for src in sorted(ASSETS.glob("0*.png")):
    img = Image.open(src).convert("RGB")
    w, h = img.size
    px = img.load()
    last = 0
    for y in range(h - 1, -1, -1):
        if any(px[x, y] != (255, 255, 255) and px[x, y] != (253, 253, 253) for x in range(330, w - 20, 6)):
            last = y
            break
    left = 0 if src.name.startswith("01") else 300
    img.crop((left, 0, w, min(h, last + 50))).save(CROPPED / src.name)
    print("cropped", src.name, f"{h}->{min(h, last + 50)}")

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page()
    page.goto((ASSETS / "guide.html").as_uri())
    page.wait_for_load_state("networkidle")
    page.pdf(path=str(PDF), format="A4", print_background=True,
             margin={"top": "14mm", "bottom": "14mm", "left": "12mm", "right": "12mm"})
    browser.close()
print("PDF:", PDF, PDF.stat().st_size // 1024, "KB")
