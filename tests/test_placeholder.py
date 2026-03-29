"""Placeholder tests — real tests added as each module is built."""
from pathlib import Path


def test_project_structure():
    for f in ["knowledge_base.py", "tools.py", "agent.py", "app.py", "requirements.txt"]:
        assert Path(f).exists(), f"Missing: {f}"


def test_requirements_has_key_packages():
    content = Path("requirements.txt").read_text()
    for pkg in ["anthropic", "langgraph", "streamlit", "pydantic"]:
        assert pkg in content, f"{pkg} missing from requirements.txt"