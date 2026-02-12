from pathlib import Path
from watcher import start_watching


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    bucket_path = project_root / "bucket"

    bucket_path.mkdir(exist_ok=True)

    start_watching(bucket_path)