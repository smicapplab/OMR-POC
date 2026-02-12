import cv2
import numpy as np
from school.previous.prev_overlay_test import (
    build_sy_grid,
    build_class_size_grid,
    build_final_grade_grid,
    build_prev_school_id_grid
)

# =========================
# CONFIG
# =========================
ROI_RADIUS = 18
FILL_THRESHOLD = 0.25

REVIEW_THRESHOLD = 0.25

def normalize_conf(val):
    return round(float(val), 2)


# =========================
# HELPERS
# =========================

def extract_roi(gray, center):
    x, y = center
    return gray[
        int(y - ROI_RADIUS):int(y + ROI_RADIUS),
        int(x - ROI_RADIUS):int(x + ROI_RADIUS)
    ]


def compute_fill_score(gray, center):
    roi = extract_roi(gray, center)

    if roi.size == 0:
        return 0.0

    _, thresh = cv2.threshold(
        roi,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    filled = np.count_nonzero(thresh)
    total = thresh.size

    return filled / float(total)


def read_column(gray, col_x, row_y_list, values):
    scores = {}

    for idx, y in enumerate(row_y_list):
        score = compute_fill_score(gray, (col_x, y))
        scores[values[idx]] = score

    best_value = max(scores, key=scores.get)
    best_score = scores[best_value]

    if best_score >= FILL_THRESHOLD:
        return best_value, best_score, scores
    else:
        return None, best_score, scores


# =========================
# READ PREVIOUS SCHOOL INFO
# =========================

def read_previous_school_info(
    img
):
    school_id_grid = build_prev_school_id_grid()
    final_grade_grid = build_final_grade_grid()
    class_grid = build_class_size_grid()
    sy_grid = build_sy_grid()
    
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

    result = {}

    # -------------------------
    # SCHOOL ID (6 digits)
    # -------------------------
    school_id_digits = []
    school_id_details = []
    confidences = []

    for col_idx, col_x in enumerate(school_id_grid["col_x"]):
        digit, confidence, scores = read_column(
            gray,
            col_x,
            school_id_grid["row_y"],
            list("0123456789")
        )

        digit_struct = {
            "selected": digit,
            "confidence": normalize_conf(confidence),
            "scores": {k: normalize_conf(v) for k, v in scores.items()}
        }

        school_id_details.append(digit_struct)

        if digit:
            school_id_digits.append(digit)
            confidences.append(confidence)
        else:
            school_id_digits.append("")

    school_id_value = "".join(school_id_digits)
    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    result["school_id"] = {
        "answer": school_id_value if school_id_value else None,
        "confidence": normalize_conf(avg_conf),
        "review_required": normalize_conf(avg_conf) < REVIEW_THRESHOLD,
        "details": {
            "digits": school_id_details
        }
    }

    # -------------------------
    # FINAL GRADE (per subject)
    # -------------------------
    final_grade_struct = {}

    col_x_list = final_grade_grid["col_x"]
    tens_rows = final_grade_grid["tens_row_y"]
    ones_rows = final_grade_grid["ones_row_y"]

    subject_names = ["Math", "English", "Science", "Filipino", "AP"]

    for i in range(0, len(col_x_list), 2):
        subject_index = i // 2
        subject_name = subject_names[subject_index]

        tens_x = col_x_list[i]
        ones_x = col_x_list[i + 1]

        tens_val, tens_conf, tens_scores = read_column(
            gray,
            tens_x,
            tens_rows,
            ["6", "7", "8", "9"]
        )

        ones_val, ones_conf, ones_scores = read_column(
            gray,
            ones_x,
            ones_rows,
            list("0123456789")
        )

        grade_value = None
        confidences = []

        if tens_val:
            confidences.append(tens_conf)
        if ones_val:
            confidences.append(ones_conf)

        if tens_val and ones_val:
            grade_value = tens_val + ones_val

        avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

        final_grade_struct[subject_name] = {
            "answer": grade_value,
            "confidence": normalize_conf(avg_conf),
            "review_required": normalize_conf(avg_conf) < REVIEW_THRESHOLD,
            "details": {
                "tens": {
                    "selected": tens_val,
                    "confidence": normalize_conf(tens_conf),
                    "scores": {k: normalize_conf(v) for k, v in tens_scores.items()}
                },
                "ones": {
                    "selected": ones_val,
                    "confidence": normalize_conf(ones_conf),
                    "scores": {k: normalize_conf(v) for k, v in ones_scores.items()}
                }
            }
        }

    result["final_grade"] = final_grade_struct

    # -------------------------
    # CLASS SIZE
    # -------------------------
    tens_val, tens_conf, tens_scores = read_column(
        gray,
        class_grid["tens_col_x"],
        class_grid["tens_row_y"],
        list("0123456789")
    )

    ones_val, ones_conf, ones_scores = read_column(
        gray,
        class_grid["ones_col_x"],
        class_grid["ones_row_y"],
        list("0123456789")
    )

    class_size = None
    confidences = []

    if tens_val:
        confidences.append(tens_conf)
    if ones_val:
        confidences.append(ones_conf)

    if tens_val and ones_val:
        class_size = tens_val + ones_val

    avg_conf = sum(confidences) / len(confidences) if confidences else 0.0

    result["class_size"] = {
        "answer": class_size,
        "confidence": normalize_conf(avg_conf),
        "review_required": normalize_conf(avg_conf) < REVIEW_THRESHOLD,
        "details": {
            "tens": {
                "selected": tens_val,
                "confidence": normalize_conf(tens_conf),
                "scores": {k: normalize_conf(v) for k, v in tens_scores.items()}
            },
            "ones": {
                "selected": ones_val,
                "confidence": normalize_conf(ones_conf),
                "scores": {k: normalize_conf(v) for k, v in ones_scores.items()}
            }
        }
    }

    # -------------------------
    # SCHOOL YEAR (SY)
    # -------------------------
    sy_scores = {}
    sy_selected = None
    best_score = 0

    for idx, center in enumerate(sy_grid["options"]):
        score = compute_fill_score(gray, center)
        label = "SY 2015-2016" if idx == 0 else "Before SY 2015-2016"
        sy_scores[label] = score

        if score > best_score:
            best_score = score
            sy_selected = label

    if best_score < FILL_THRESHOLD:
        sy_selected = None

    result["school_year"] = {
        "answer": sy_selected,
        "confidence": normalize_conf(best_score),
        "review_required": normalize_conf(best_score) < REVIEW_THRESHOLD,
        "details": {
            "scores": {k: normalize_conf(v) for k, v in sy_scores.items()}
        }
    }

    return result
