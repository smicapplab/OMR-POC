import sys
import logging
from pathlib import Path
from watcher import start_watching


def configure_logging() -> None:
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s | %(levelname)s | %(message)s",
    )


def resolve_bucket_path() -> Path:
    """
    Resolve bucket directory from:
    1. CLI argument (optional)
    2. Default project root / bucket
    """
    project_root = Path(__file__).resolve().parent.parent

    if len(sys.argv) > 1:
        return Path(sys.argv[1]).resolve()

    return project_root / "bucket"


def main():
    configure_logging()

    bucket_path = resolve_bucket_path()

    logging.info(f"Using bucket path: {bucket_path}")

    if not bucket_path.exists():
        logging.warning("Bucket path does not exist. Creating it.")
        bucket_path.mkdir(parents=True, exist_ok=True)

    if not bucket_path.is_dir():
        logging.error("Bucket path is not a directory.")
        sys.exit(1)

    logging.info("Starting OMR bucket listener...")
    start_watching(bucket_path)


if __name__ == "__main__":
    main()