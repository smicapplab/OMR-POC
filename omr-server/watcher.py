import shutil
from pathlib import Path
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
from processor import extract_test_data, wait_until_stable


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

            extract_test_data(file_path)

            #target = self.success_path / file_path.name
            #shutil.move(str(file_path), target)

            print(f"[MOVED] {file_path.name} → success/")

        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")

            if file_path.exists():
                #target = self.error_path / file_path.name
                #shutil.move(str(file_path), target)

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