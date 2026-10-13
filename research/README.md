# research: forecasting workstream

The M.Tech research is AI forecasting of Indian events (`../NEW_DIRECTION.md`; formal guide approval pending). Implementation order: Documentation → Flutter UI → Python backend → connect the UI to real data. Exception: the December 2026 pilot is recorded by hand (`forecast/PILOT_PROTOCOL.md`).

- `forecast/`: protocol, Minor 1 design, backend milestone, literature. Documentation only so far; the Python pipeline (`forecast/pipeline/`) is written later by the user.
- The old thesis workspace (`reflica_bench`: benchmark v0.2.0, baselines, B5 engine, LLM pilot, 203 tests) was **removed on 14 Oct 2026**. It is kept in branch `archive/old-reflica-2026-10-14`. Restore a file with `git checkout archive/old-reflica-2026-10-14 -- <path>`.
- `pyproject.toml` and `pytest.ini` still describe the old package. Update them when the pipeline code is written (`../docs/CLEANUP_EDITS.md` section C).
