import time
from pathlib import Path
from student.read_student_info import read_student_info
from school.previous.prev_read_info import read_previous_school_info
from school.current.curr_read_info import read_current_school_info
from answers.read_answers import detect_answers

import json
import cv2


def wait_until_stable(file_path: Path, timeout: int = 10):
    """
    Wait until file size stops changing.
    Prevents processing partially-written files.
    """
    start_time = time.time()
    last_size = -1

    while True:
        current_size = file_path.stat().st_size

        if current_size == last_size:
            return

        if time.time() - start_time > timeout:
            raise TimeoutError(f"File {file_path} did not stabilize.")

        last_size = current_size
        time.sleep(0.5)


def extract_test_data(file_path: Path):
    """
    Placeholder for OMR extraction logic.
    Replace with real processing later.
    """
    print(f"[PROCESSING] {file_path}")


    # Load image using OpenCV
    img = cv2.imread(str(file_path))
    if img is None:
        raise ValueError(f"Failed to load image: {file_path}")

    # student_info = read_student_info(img)
    # print( student_info )

    # prev_school = read_previous_school_info(img)
    # print( prev_school )

    # curr_school = read_current_school_info(img)
    # print( curr_school )

    answers = detect_answers(img)
    print( answers )


    print(f"[SUCCESS] {file_path.name}")


def process_existing_pngs(directory: Path):
    """
    For testing: manually scan a directory and process all existing PNG files.
    This simulates new file triggers without using watchdog events.
    """
    if not directory.exists():
        raise FileNotFoundError(f"{directory} does not exist")

    png_files = sorted(directory.glob("*.png"))

    if not png_files:
        print("[INFO] No PNG files found.")
        return

    for file_path in png_files:
        try:
            print(f"[MANUAL TRIGGER] {file_path.name}")
            wait_until_stable(file_path)
            extract_test_data(file_path)
        except Exception as e:
            print(f"[ERROR] {file_path.name}: {e}")