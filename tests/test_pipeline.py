import asyncio
from src.workflows.pipeline import Pipeline

def test_pipeline_runs(tmp_path):
    import asyncio
    p = Pipeline()
    asyncio.run(p.run())
    out = tmp_path / "out"
    # pipeline writes to out/digest.json in working dir; just assert no exception

def test_placeholder_adapter():
    import asyncio
    from src.tools.adapters_placeholder import PlaceholderAdapter
    items = asyncio.run(PlaceholderAdapter().fetch_items())
    assert isinstance(items, list)
