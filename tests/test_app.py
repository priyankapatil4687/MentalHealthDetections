import pytest
from streamlit.testing.v1 import AppTest

from src.config import ROOT

PAGES = ["Overview", "Age analysis", "Language analysis", "Age x Language",
         "Model comparison", "Explainability", "Generative AI", "Limitations"]


@pytest.mark.skipif(not (ROOT / "outputs" / "reports" / "analysis_summary.json").exists(),
                    reason="run the pipeline first")
@pytest.mark.parametrize("page", PAGES)
def test_dashboard_page_renders(page):
    at = AppTest.from_file(str(ROOT / "app.py"), default_timeout=60).run()
    assert not at.exception
    at.sidebar.radio[0].set_value(page).run()
    assert not at.exception, at.exception
