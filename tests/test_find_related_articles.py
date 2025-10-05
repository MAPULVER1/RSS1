import sys
from pathlib import Path

import pandas as pd

project_root = Path(__file__).resolve().parents[1]
if str(project_root) not in sys.path:
    sys.path.insert(0, str(project_root))

from app import find_related_articles


def test_find_related_articles_handles_nan_titles():
    df = pd.DataFrame(
        {
            "Title": [float("nan"), None],
            "Link": ["https://example.com/one", "https://example.com/two"],
        }
    )

    related = find_related_articles("climate change", df)

    assert related == []
