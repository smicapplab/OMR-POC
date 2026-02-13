import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from processor import extract_test_data, wait_until_stable
from db.persist_scan import update_scan_status

class PNGHandler(FileSystemEventHandler):
    def __init__(self, bucket_path: Path):
        self.bucket_path = bucket_path
        self.success_path = bucket_path / "success"
        self.error_path = bucket_path / "error"

        self.success_path.mkdir(exist_ok=True)
        self.error_path.mkdir(exist_ok=True)

    def on_created(self, event):
        if event.is_directory:
            return

        file_path = Path(event.src_path)

        if file_path.suffix.lower() != ".png":
            return

        print(f"[DETECTED] {file_path.name}")

        try:
            wait_until_stable(file_path)

            scan_id = extract_test_data(file_path)

            target = self.success_path / file_path.name
            shutil.move(str(file_path), target)

            relative_path = f"bucket/success/{file_path.name}"
            update_scan_status(
                scan_id=scan_id,
                new_file_path=Path(relative_path),
                status="success",
            )

            print(f"[MOVED] {file_path.name} → success/")

        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")

            if file_path.exists():
                target = self.error_path / file_path.name
                shutil.move(str(file_path), target)

                if 'scan_id' in locals():
                    relative_path = f"bucket/error/{file_path.name}"
                    update_scan_status(
                        scan_id=scan_id,
                        new_file_path=Path(relative_path),
                        status="error",
                    )

                print(f"[MOVED] {file_path.name} → error/")


def start_watching(bucket_path: Path):
    event_handler = PNGHandler(bucket_path)
    observer = Observer()
    observer.schedule(event_handler, str(bucket_path), recursive=False)
    observer.start()

    print(f"[WATCHING] {bucket_path}")

    try:
        while True:
            pass
    except KeyboardInterrupt:
        observer.stop()

    observer.join()