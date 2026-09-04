import pathlib, yaml

_DEFAULT = pathlib.Path(__file__).parent / "default.yaml"

def load(path=None):
    """Load config YAML. If path is None, loads the default config."""
    p = pathlib.Path(path) if path else _DEFAULT
    with open(p) as f:
        return yaml.safe_load(f)
