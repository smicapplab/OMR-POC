import cv2
import numpy as np
from school.current.curr_overlay_test import (
    build_region_grid,
    build_division_grid,
    build_school_id_grid,
    build_school_type_grid
)


# =========================
# CONFIG
# =========================

FILL_THRESHOLD = 0.45
DOMINANCE_GAP = 0.10

REGION_ROWS = [
    "REGION I",
    "REGION II",
    "REGION III",
    "REGION IV-A",
    "REGION V",
    "REGION VI",
    "REGION VII",
    "REGION VIII",
    "REGION IX",
    "REGION X",
    "REGION XI",
    "REGION XII",
    "NCR",
    "CAR",
    "BARMM",
    "CARAGA",
    "NIR"
]
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
        return None, top_score

    if (top_score - second_score) < DOMINANCE_GAP:
        return None, top_score

    return top_val, top_score


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
            scores[rows[row_idx]] = round(score, 2)

        selected, confidence = decide_selection(scores, threshold)

        if selected:
            decoded += selected

        results[0] = {
            "selected": selected,
            "confidence": round(confidence, 2),
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
            scores[rows[row_idx]] = round(score, 2)

        selected, confidence = decide_selection(scores, threshold)

        if selected:
            decoded += selected

        results[col_idx] = {
            "selected": selected,
            "confidence": round(confidence, 2),
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


    if img is None:
        raise ValueError("Unable to load image.")

    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    region_value, region_details = read_grid(gray, region_grid, REGION_ROWS, threshold=0.38)

    division_value, division_details = read_grid(gray, division_grid, DIGIT_ROWS, threshold=0.42)
    school_id_value, school_id_details = read_grid(gray, school_id_grid, DIGIT_ROWS, threshold=0.42)

    school_type_value, school_type_details = read_grid(
        gray,
        school_type_grid,
        SCHOOL_TYPE_ROWS,
        threshold=0.40
    )

    def wrap_field(answer, details_dict):
        """
        Convert raw grid output into deterministic schema:
        ✔ answer
        ✔ confidence (2 decimals, averaged if multi-column)
        ✔ review_required (confidence < 0.50)
        ✔ details with standardized keys
        """
        if not details_dict:
            return {
                "answer": answer,
                "confidence": 0.00,
                "review_required": True,
                "details": {"scores": {}}
            }

        confidences = []
        digits = []

        # multi-column style (true multi-column = more than 1 column)
        if len(details_dict) > 1:
            for idx in sorted(details_dict.keys()):
                col = details_dict[idx]
                conf = round(float(col.get("confidence", 0)), 2)
                confidences.append(conf)

                digits.append({
                    "selected": col.get("selected"),
                    "confidence": conf,
                    "scores": col.get("scores", {})
                })

            final_conf = round(sum(confidences) / len(confidences), 2) if confidences else 0.00

            return {
                "answer": answer,
                "confidence": final_conf,
                "review_required": final_conf < 0.50,
                "details": {"digits": digits}
            }

        # single-column style (e.g., region / school_type)
        col = list(details_dict.values())[0]
        conf = round(float(col.get("confidence", 0)), 2)

        return {
            "answer": answer,
            "confidence": conf,
            "review_required": conf < 0.50,
            "details": {"scores": col.get("scores", {})}
        }

    return {
        "region": wrap_field(region_value, region_details),
        "division": wrap_field(division_value, division_details),
        "school_id": wrap_field(school_id_value, school_id_details),
        "school_type": wrap_field(school_type_value, school_type_details),
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