import yaml
from pathlib import Path

def load_prompts(file_path: str) -> dict:
    """Loads prompts from a YAML file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        return yaml.safe_load(f)