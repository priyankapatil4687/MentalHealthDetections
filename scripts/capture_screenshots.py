"""Capture dashboard screenshots for the Marathi guide. Needs the dashboard running on PORT and Microsoft Edge."""
import sys
from pathlib import Path

from playwright.sync_api import sync_playwright

PORT = sys.argv[1] if len(sys.argv) > 1 else "8610"
OUT = Path(__file__).resolve().parent.parent / "docs" / "guide_assets"
OUT.mkdir(parents=True, exist_ok=True)

PAGES = [("01_overview", "Overview"), ("02_age", "Age analysis"), ("03_language", "Language analysis"),
         ("04_age_language", "Age x Language"), ("05_models", "Model comparison"),
         ("06_explain", "Explainability"), ("07_genai", "Generative AI"), ("08_limits", "Limitations")]

with sync_playwright() as p:
    browser = p.chromium.launch(channel="msedge", headless=True)
    page = browser.new_page(viewport={"width": 1500, "height": 2500})
    page.goto(f"http://localhost:{PORT}/")
    page.wait_for_selector("text=Navigation", timeout=60000)
    page.wait_for_timeout(3000)
    for fname, label in PAGES:
        page.locator("[data-testid='stSidebar']").get_by_text(label, exact=True).first.click()
        page.wait_for_timeout(3500)
        page.screenshot(path=str(OUT / f"{fname}.png"))
        print("saved", fname)
    browser.close()
