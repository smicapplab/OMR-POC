from pathlib import Path
from processor import process_existing_pngs


if __name__ == "__main__":
    project_root = Path(__file__).resolve().parent.parent
    bucket_path = project_root / "bucket"

    bucket_path.mkdir(exist_ok=True)

    process_existing_pngs(bucket_path)

