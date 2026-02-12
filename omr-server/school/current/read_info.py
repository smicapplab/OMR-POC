import cv2
import numpy as np
from pathlib import Path
from school.current.overlay_test import (
    build_region_grid,
    build_division_grid,
    build_school_id_grid,
    build_school_type_grid
)


# =========================
# CONFIG
# =========================
IMAGE_PATH = "template/answer3.png"

FILL_THRESHOLD = 0.45
DOMINANCE_GAP = 0.10

REGION_ROWS = list("ABCDEFGHIJKLMNOPQRSTUVWXYZ")

REGION_MAP = {
    1: "REGION I",
    2: "REGION II",
    3: "REGION III",
    4: "REGION IV-A",
    5: "REGION V",
    6: "REGION VI",
    7: "REGION VII",
    8: "REGION VIII",
    9: "REGION IX",
    10: "REGION X",
    11: "REGION XI",
    12: "REGION XII",
    13: "NCR",
    14: "CAR",
    15: "BARMM"
}
DIGIT_ROWS = list("0123456789")

SCHOOL_TYPE_ROWS = [
    "National Barangay/Community HS",
    "National Comprehensive HS",
    "Integrated School",
    "Public Science HS",
    "Public Vocational HS",
    "State College/University",
    "Private Non-Sectarian HS",
    "Private Sectarian HS",
    "Private Vocational HS",
    "Private Science HS"
]


# =========================
# CORE SCORING UTIL
# =========================

def compute_fill_score(gray_roi: np.ndarray) -> float:
    thresh = cv2.adaptiveThreshold(
        gray_roi,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        21,
        5
    )

    filled = cv2.countNonZero(thresh)
    total = thresh.shape[0] * thresh.shape[1]
    return filled / float(total)


def decide_selection(scores: dict, threshold=FILL_THRESHOLD):
    sorted_items = sorted(scores.items(), key=lambda x: x[1], reverse=True)
    top_val, top_score = sorted_items[0]
    second_score = sorted_items[1][1] if len(sorted_items) > 1 else 0

    if top_score < threshold:
        return None, top_score, "blank"

    if (top_score - second_score) < DOMINANCE_GAP:
        return None, top_score, "multi"

    return top_val, top_score, "single"


# =========================
# GRID READER (COORDINATE STYLE)
# =========================

def read_grid(gray_img, grid, rows, threshold=FILL_THRESHOLD):
    """
    Supports:
    1. Region grid: { row_index: (x, y) }
    2. Multi-column grid: { col_index: { row_index: (x, y) } }
    """

    results = {}
    decoded = ""

    # -----------------
    # REGION STYLE
    # -----------------
    if all(isinstance(v, tuple) for v in grid.values()):
        scores = {}

        for row_idx, (x, y) in grid.items():
            roi = gray_img[int(y-14):int(y+14), int(x-14):int(x+14)]
            score = compute_fill_score(roi)
            scores[rows[row_idx]] = round(score, 3)

        selected, confidence, status = decide_selection(scores, threshold)

        if selected:
            decoded += selected

        results[0] = {
            "selected": selected,
            "confidence": round(confidence, 3),
            "status": status,
            "scores": scores
        }

        return decoded, results

    # -----------------
    # MULTI-COLUMN STYLE
    # -----------------
    for col_idx, col_dict in grid.items():
        scores = {}

        for row_idx, (x, y) in col_dict.items():
            roi = gray_img[int(y-14):int(y+14), int(x-14):int(x+14)]
            score = compute_fill_score(roi)
            scores[rows[row_idx]] = round(score, 3)

        selected, confidence, status = decide_selection(scores, threshold)

        if selected:
            decoded += selected

        results[col_idx] = {
            "selected": selected,
            "confidence": round(confidence, 3),
            "status": status,
            "scores": scores
        }

    return decoded, results


# =========================
# MAIN ENTRY
# =========================

def read_current_school_info(
    img
    # region_grid,
    # division_grid,
    # school_id_grid,
    # school_type_grid
):
    region_grid = build_region_grid()
    division_grid = build_division_grid()
    school_id_grid = build_school_id_grid()
    school_type_grid = build_school_type_grid()


    # image_path = Path(image_path)
    # image = cv2.imread(str(image_path))

    if img is None:
        raise ValueError("Unable to load image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    region_value, region_details = read_grid(gray, region_grid, REGION_ROWS, threshold=0.40)

    # Convert region letter to mapped region name
    if region_value:
        region_index = REGION_ROWS.index(region_value) + 1
        region_value = REGION_MAP.get(region_index, region_value)
    division_value, division_details = read_grid(gray, division_grid, DIGIT_ROWS, threshold=0.42)
    school_id_value, school_id_details = read_grid(gray, school_id_grid, DIGIT_ROWS, threshold=0.42)

    school_type_value, school_type_details = read_grid(
        gray,
        school_type_grid,
        SCHOOL_TYPE_ROWS,
        threshold=0.40
    )

    return {
        "region": region_value,
        "division": division_value,
        "school_id": school_id_value,
        "school_type": school_type_value,
        # "details": {
        #     "region": region_details,
        #     "division": division_details,
        #     "school_id": school_id_details,
        #     "school_type": school_type_details
        # }
    }


# =========================
# OPTIONAL STANDALONE TEST
# =========================

# if __name__ == "__main__":
#     from overlay_test import (
#         build_region_grid,
#         build_division_grid,
#         build_school_id_grid,
#         build_school_type_grid
#     )

#     img = cv2.imread(IMAGE_PATH)

#     if img is None:
#         print(f"Failed to load image: {IMAGE_PATH}")
#     else:
#         print("Image loaded successfully.")

#         region_grid = build_region_grid()
#         division_grid = build_division_grid()
#         school_id_grid = build_school_id_grid()
#         school_type_grid = build_school_type_grid()

#         result = read_current_school_info(
#             IMAGE_PATH,
#             region_grid,
#             division_grid,
#             school_id_grid,
#             school_type_grid
#         )

#         print("\nDetected Current School Info:")
#         print(result)