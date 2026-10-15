import importlib.util
from pathlib import Path


def load_dlpc350():
    dlpc350_path = (Path(__file__).resolve().parents[1] / "dlpc350" / "dlpc350.py").resolve()
    if not dlpc350_path.exists():
        raise FileNotFoundError(f"Could not find dlpc350.py at {dlpc350_path}")

    spec = importlib.util.spec_from_file_location("dlpc350_real", dlpc350_path)
    if spec is None or spec.loader is None:
        raise ImportError(f"Could not load module spec for {dlpc350_path}")

    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod.DLPC350


DLPC350 = load_dlpc350()
__all__ = ["load_dlpc350", "DLPC350"]