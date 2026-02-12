import cv2
import numpy as np
from student.student_overlay_test import (
    build_last_name_grid,
    build_first_name_grid,
    build_mi_grid,
    build_month_grid,
    build_day_grid,
    build_year_grid,
    build_ssc_grid,
    build_4ps_grid,
    build_special_class_grid,
    build_gender_grid,
    build_lrn_grid
)

# ----------------------------
# TEXT FIELD AGGREGATION HELPER
# ----------------------------
def aggregate_text_field(answer, details):
    """
    Production-grade aggregation for text fields.

    Rules:
    - Confidence computed only from selected columns.
    - Trailing blank columns ignored.
    - review_required triggered if:
        * any column is "multi"
        * internal blank exists before last detected character
        * average confidence < 0.70
    """

    if not details:
        return {
            "answer": answer,
            "confidence": normalize_conf(0.00),
            "review_required": True,
            "details": {
                "digits": []
            }
        }

    # Determine last meaningful column (last with selected char)
    selected_columns = [col for col, data in details.items() if data.get("selected") is not None]

    if not selected_columns:
        return {
            "answer": answer,
            "confidence": normalize_conf(0.00),
            "review_required": True,
            "details": {
                "digits": []
            }
        }

    last_selected_col = max(selected_columns)

    confidences = []
    has_multi = False
    internal_blank = False

    for col in sorted(details.keys()):
        col_data = details[col]

        # Ignore trailing blanks after last selected character
        if col > last_selected_col:
            continue

        status = col_data.get("status")
        selected = col_data.get("selected")
        confidence = col_data.get("confidence", 0.0)

        if status == "multi":
            has_multi = True

        if selected is None:
            # Blank before last selected character = internal gap
            internal_blank = True
        else:
            confidences.append(confidence)

    # Compute field confidence
    if confidences:
        field_conf = normalize_conf(sum(confidences) / len(confidences))
    else:
        field_conf = 0.0

    # (field status computation removed)

    # Review logic (production tuned)
    review_required = (
        has_multi
        or internal_blank
        or field_conf < REVIEW_THRESHOLD
    )

    # Transform dict-based column details into deterministic digits array (ignore trailing blanks after last selected)
    digit_entries = []
    for col in sorted(details.keys()):
        # Ignore trailing blanks after last selected character
        if col > last_selected_col:
            continue

        col_data = details[col]

        digit_entries.append({
            "selected": col_data.get("selected"),
            "confidence": normalize_conf(col_data.get("confidence", 0.0)),
            "scores": {
                k: normalize_conf(v)
                for k, v in col_data.get("scores", {}).items()
            }
        })

    return {
        "answer": answer,
        "confidence": normalize_conf(field_conf),
        "review_required": review_required,
        "details": {
            "digits": digit_entries
        }
    }

# ----------------------------
# CONFIG
# ----------------------------
#IMAGE_PATH = "template/answer3.png" 
FILL_THRESHOLD = 0.55
REVIEW_THRESHOLD = 0.70
DOMINANCE_GAP = 0.07

# Helper for normalizing confidence values
def normalize_conf(value):
    return round(float(value), 2)

ROI_WIDTH = 14
ROI_HEIGHT = 14


MONTH_ROWS = [
    "JAN","FEB","MAR","APR","MAY","JUN",
    "JUL","AUG","SEP","OCT","NOV","DEC"
]

DIGITS_0_9 = [str(i) for i in range(10)]
DIGITS_0_3 = [str(i) for i in range(4)]


# ----------------------------
# CORE DETECTION
# ----------------------------
def detect_name_from_grid(img, grid):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    # Reduce micro-noise from paper texture and print
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    # Use OTSU to separate graphite from light orange print
    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    detected_name = ""
    detailed = {}

    for col in sorted(grid.keys()):
        scores = {}

        for letter, (x, y) in grid[col].items():
            x1 = int(x - ROI_WIDTH // 2)
            x2 = int(x + ROI_WIDTH // 2)
            y1 = int(y - ROI_HEIGHT // 2)
            y2 = int(y + ROI_HEIGHT // 2)

            roi = thresh[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            # Apply circular mask to avoid counting outside-bubble noise
            h, w = roi.shape
            mask = np.zeros((h, w), dtype=np.uint8)
            center = (w // 2, h // 2)
            radius = min(w, h) // 2
            cv2.circle(mask, center, radius, 255, -1)
            roi = cv2.bitwise_and(roi, mask)

            dark_pixels = cv2.countNonZero(roi)
            fill_ratio = dark_pixels / float(roi.size)
            scores[letter] = round(fill_ratio, 2)

        # Sort by fill strength
        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        if not sorted_scores:
            detected_name += " "
            continue

        top_letter, top_score = sorted_scores[0]

        # Get second score for dominance rule
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

        if top_score < FILL_THRESHOLD:
            detected_name += " "
            status = "blank"
        elif (top_score - second_score) >= DOMINANCE_GAP:
            detected_name += top_letter
            status = "single"
        else:
            # If dominance gap is too small, treat as ambiguous and do NOT accept
            detected_name += " "
            status = "multi"

        detailed[col] = {
            "selected": top_letter if top_score >= FILL_THRESHOLD else None,
            "confidence": round(top_score, 2),
            "status": status,
            "scores": scores
        }

    return detected_name.strip(), detailed


# ----------------------------
# WRAPPER
# ----------------------------
def read_student_info(
    img
):
    # Build grids from calibration
    last_grid = build_last_name_grid()
    first_grid = build_first_name_grid()
    mi_grid = build_mi_grid()
    month_grid = build_month_grid()
    day_grid = build_day_grid()
    year_grid = build_year_grid()
    ssc_grid = build_ssc_grid()
    four_ps_grid = build_4ps_grid()
    special_class_grid = build_special_class_grid()
    gender_grid = build_gender_grid()
    lrn_grid = build_lrn_grid()     


    # --- NAME ---
    last_name, last_detail = detect_name_from_grid(img, last_grid)
    first_name, first_detail = detect_name_from_grid(img, first_grid)
    mi, mi_detail = detect_name_from_grid(img, mi_grid)

    # # --- BIRTH + SSC ---
    birth_info = read_birth_and_ssc(
        img,
        month_grid,
        day_grid,
        year_grid,
        ssc_grid
    )

    # # --- 4Ps / Special Classes / Gender ---
    flags_info = read_student_flags(
        img,
        four_ps_grid,
        special_class_grid,
        gender_grid
    )

    # # --- LRN (12-digit numeric) ---
    lrn = read_lrn(img, lrn_grid)

    return {
        "last_name": aggregate_text_field(last_name, last_detail),
        "first_name": aggregate_text_field(first_name, first_detail),
        "middle_initial": aggregate_text_field(mi, mi_detail),
        "birth_month": birth_info["birth_month"],
        "birth_day": birth_info["birth_day"],
        "birth_year": birth_info["birth_year"],
        "ssc": birth_info["ssc"],
        "four_ps": flags_info["four_ps"],
        "special_classes": flags_info["special_classes"],
        "gender": flags_info["gender"],
        "lrn": lrn,
    }


# ----------------------------
# BIRTHDATE & SSC READER
# ----------------------------
def read_birth_and_ssc(img, month_grid, day_grid, year_grid, ssc_grid):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    def read_single_column(grid, labels):
        scores = {}
        for label, (x, y) in grid.items():
            x1 = int(x - ROI_WIDTH // 2)
            x2 = int(x + ROI_WIDTH // 2)
            y1 = int(y - ROI_HEIGHT // 2)
            y2 = int(y + ROI_HEIGHT // 2)

            roi = thresh[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            dark_pixels = cv2.countNonZero(roi)
            fill_ratio = dark_pixels / float(roi.size)
            scores[label] = round(fill_ratio, 2)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if not sorted_scores:
            return None

        top_label, top_score = sorted_scores[0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

        if top_score >= FILL_THRESHOLD and (top_score - second_score) >= DOMINANCE_GAP:
            return top_label
        return None

    # MONTH (categorical with full option scoring)
    month_scores = {}
    for label, (x, y) in month_grid.items():
        x1 = int(x - ROI_WIDTH // 2)
        x2 = int(x + ROI_WIDTH // 2)
        y1 = int(y - ROI_HEIGHT // 2)
        y2 = int(y + ROI_HEIGHT // 2)

        roi = thresh[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        dark_pixels = cv2.countNonZero(roi)
        fill_ratio = dark_pixels / float(roi.size)
        month_scores[label] = round(fill_ratio, 2)

    month = None
    month_confidence = 0.0

    if month_scores:
        sorted_month = sorted(month_scores.items(), key=lambda x: x[1], reverse=True)
        top_label, top_score = sorted_month[0]
        second_score = sorted_month[1][1] if len(sorted_month) > 1 else 0

        if top_score >= FILL_THRESHOLD:
            month = MONTH_ROWS[int(top_label)]
            month_confidence = top_score

    # Replace return month in dict later
    month_confidence = round(month_confidence, 2)

    month_result = {
        "answer": month,
        "confidence": normalize_conf(month_confidence),
        "review_required": (month is None) or (normalize_conf(month_confidence) < REVIEW_THRESHOLD),
        "details": {
            "scores": {
                MONTH_ROWS[int(k)]: normalize_conf(v) for k, v in month_scores.items()
            }
        }
    }

    # DAY (2 columns: first = tens 0–3, second = ones 0–9)
    day = None
    tens = None
    ones = None

    day_cols = sorted(day_grid.keys())

    if len(day_cols) >= 2:
        tens = read_single_column(day_grid[day_cols[0]], DIGITS_0_3)
        ones = read_single_column(day_grid[day_cols[1]], DIGITS_0_9)

    if tens is not None and ones is not None:
        day_val = int(tens) * 10 + int(ones)
        if 1 <= day_val <= 31:
            day = f"{day_val:02d}"

    # YEAR (2 columns 0–9 each) — use dominance gap and return confidence
    year = None
    year_cols = sorted(year_grid.keys())

    y1 = y2 = None
    y1_conf = y2_conf = 0.0

    def read_year_column(grid):
        scores = {}

        # Use explicit digit labels from calibration grid
        for digit_label, (x, y) in grid.items():
            x1 = int(x - ROI_WIDTH // 2)
            x2 = int(x + ROI_WIDTH // 2)
            y1 = int(y - ROI_HEIGHT // 2)
            y2 = int(y + ROI_HEIGHT // 2)

            roi = thresh[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            dark_pixels = cv2.countNonZero(roi)
            fill_ratio = dark_pixels / float(roi.size)

            scores[str(digit_label)] = round(fill_ratio, 2)

        if not scores:
            return None, 0.0

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)

        top_label, top_score = sorted_scores[0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0.0

        if top_score >= FILL_THRESHOLD and (top_score - second_score) >= DOMINANCE_GAP:
            return top_label, top_score

        return None, 0.0

    if len(year_cols) >= 2:
        y1, y1_conf = read_year_column(year_grid[year_cols[0]])
        y2, y2_conf = read_year_column(year_grid[year_cols[1]])

        if y1 is not None and y2 is not None:
            year = y1 + y2

    # SSC (single bubble, no dominance rule)
    ssc = False
    for _, (x, y) in ssc_grid.items():
        ssc_x1 = int(x - ROI_WIDTH // 2)
        ssc_x2 = int(x + ROI_WIDTH // 2)
        ssc_y1 = int(y - ROI_HEIGHT // 2)
        ssc_y2 = int(y + ROI_HEIGHT // 2)

        roi = thresh[ssc_y1:ssc_y2, ssc_x1:ssc_x2]
        if roi.size == 0:
            continue

        dark_pixels = cv2.countNonZero(roi)
        fill_ratio = dark_pixels / float(roi.size)

        if fill_ratio >= FILL_THRESHOLD:
            ssc = True
            break

    # Conservative confidence: weakest digit governs the field
    day_confidence = min(
        1.00 if tens is not None else 0.00,
        1.00 if ones is not None else 0.00
    ) if day else 0.00

    birth_day_result = {
        "answer": day,
        "confidence": normalize_conf(day_confidence),
        "review_required": (day is None) or (normalize_conf(day_confidence) < REVIEW_THRESHOLD),
        "details": {
            "tens": {
                "selected": str(tens) if tens is not None else None,
                "confidence": normalize_conf(1.00 if tens is not None else 0.00),
                "scores": {
                    d: normalize_conf(1.00 if str(d) == str(tens) else 0.00)
                    for d in DIGITS_0_3
                }
            },
            "ones": {
                "selected": str(ones) if ones is not None else None,
                "confidence": normalize_conf(1.00 if ones is not None else 0.00),
                "scores": {
                    d: normalize_conf(1.00 if str(d) == str(ones) else 0.00)
                    for d in DIGITS_0_9
                }
            }
        }
    }

    # Conservative confidence: weakest digit governs the field
    year_confidence = min(y1_conf, y2_conf) if year else 0.0

    birth_year_result = {
        "answer": year,
        "confidence": normalize_conf(year_confidence),
        "review_required": (year is None) or (normalize_conf(year_confidence) < REVIEW_THRESHOLD),
        "details": {
            "digits": [
                {
                    "selected": y1,
                    "confidence": normalize_conf(y1_conf),
                    "scores": {
                        d: normalize_conf(1.00 if str(d) == str(y1) else 0.00)
                        for d in DIGITS_0_9
                    }
                },
                {
                    "selected": y2,
                    "confidence": normalize_conf(y2_conf),
                    "scores": {
                        d: normalize_conf(1.00 if str(d) == str(y2) else 0.00)
                        for d in DIGITS_0_9
                    }
                }
            ] if len(year_cols) >= 2 else []
        }
    }

    # Wrap SSC (structured)
    ssc_conf = round(1.00 if ssc else 0.00, 2)

    ssc_result = {
        "answer": "Yes" if ssc else "No",
        "confidence": normalize_conf(ssc_conf),
        "review_required": normalize_conf(ssc_conf) < REVIEW_THRESHOLD,
        "details": {
            "scores": {
                "Yes": normalize_conf(ssc_conf),
                "No": normalize_conf(1.00 - ssc_conf)
            }
        }
    }

    return {
        "birth_month": month_result,
        "birth_day": birth_day_result,
        "birth_year": birth_year_result,
        "ssc": ssc_result
    }


# ----------------------------
# 4Ps / SPECIAL CLASSES / GENDER READER
# ----------------------------
def read_student_flags(img, four_ps_grid, special_class_grid, gender_grid):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    def bubble_filled(x, y):
        x1 = int(x - ROI_WIDTH // 2)
        x2 = int(x + ROI_WIDTH // 2)
        y1 = int(y - ROI_HEIGHT // 2)
        y2 = int(y + ROI_HEIGHT // 2)

        roi = thresh[y1:y2, x1:x2]
        if roi.size == 0:
            return False

        dark_pixels = cv2.countNonZero(roi)
        fill_ratio = dark_pixels / float(roi.size)
        return fill_ratio >= FILL_THRESHOLD

    # ---- 4Ps (single select, 3 options)
    four_ps_options = ["Yes", "No", "I don't know"]
    four_ps = None

    for idx, (x, y) in four_ps_grid.items():
        if bubble_filled(x, y):
            four_ps = four_ps_options[idx]
            break

    # ---- Special Classes (multi-select)
    special_labels = [
        "Special science class",
        "Special educational class",
        "Class under MISOSA",
        "Class in a BRAC",
        "ALIVE / Madrasah class"
    ]

    selected_special = []
    for idx, (x, y) in special_class_grid.items():
        if bubble_filled(x, y):
            selected_special.append(special_labels[idx])

    # ---- Gender (single select)
    gender_labels = ["Male", "Female"]
    gender_scores = {}

    for idx, (x, y) in gender_grid.items():
        x1 = int(x - ROI_WIDTH // 2)
        x2 = int(x + ROI_WIDTH // 2)
        y1 = int(y - ROI_HEIGHT // 2)
        y2 = int(y + ROI_HEIGHT // 2)

        roi = thresh[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        dark_pixels = cv2.countNonZero(roi)
        fill_ratio = dark_pixels / float(roi.size)
        gender_scores[gender_labels[idx]] = round(fill_ratio, 2)

    gender = None
    gender_confidence = 0.0

    if gender_scores:
        sorted_gender = sorted(gender_scores.items(), key=lambda x: x[1], reverse=True)
        top_label, top_score = sorted_gender[0]
        second_score = sorted_gender[1][1] if len(sorted_gender) > 1 else 0

        if top_score >= FILL_THRESHOLD:
            gender = top_label
            gender_confidence = top_score

    gender_confidence = round(gender_confidence, 2)

    gender_result = {
        "answer": gender,
        "confidence": normalize_conf(gender_confidence),
        "review_required": (gender is None) or (normalize_conf(gender_confidence) < REVIEW_THRESHOLD),
        "details": {
            "scores": {k: normalize_conf(v) for k, v in gender_scores.items()}
        }
    }

    four_ps_conf = round(1.00 if four_ps else 0.00, 2)

    four_ps_result = {
        "answer": four_ps,
        "confidence": normalize_conf(four_ps_conf),
        "review_required": (four_ps is None) or (normalize_conf(four_ps_conf) < REVIEW_THRESHOLD),
        "details": {
            "scores": {
                opt: (normalize_conf(four_ps_conf) if opt == four_ps else normalize_conf(1.00 - four_ps_conf))
                for opt in ["Yes", "No", "I don't know"]
            }
        }
    }

    special_conf = round(1.00 if selected_special else 0.00, 2)

    special_class_result = {
        "answer": selected_special,
        "confidence": normalize_conf(special_conf),
        "review_required": normalize_conf(special_conf) < REVIEW_THRESHOLD,
        "details": {
            "scores": {
                label: normalize_conf(1.00 if label in selected_special else 0.00)
                for label in [
                    "Special science class",
                    "Special educational class",
                    "Class under MISOSA",
                    "Class in a BRAC",
                    "ALIVE / Madrasah class"
                ]
            }
        }
    }

    return {
        "four_ps": four_ps_result,
        "special_classes": special_class_result,
        "gender": gender_result
    }


# ----------------------------
# LRN READER
# ----------------------------
def read_lrn(img, lrn_grid):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.GaussianBlur(gray, (5, 5), 0)

    _, thresh = cv2.threshold(
        gray,
        0,
        255,
        cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
    )

    lrn_digits = []

    for col in sorted(lrn_grid.keys()):
        scores = {}

        for digit, (x, y) in lrn_grid[col].items():
            x1 = int(x - ROI_WIDTH // 2)
            x2 = int(x + ROI_WIDTH // 2)
            y1 = int(y - ROI_HEIGHT // 2)
            y2 = int(y + ROI_HEIGHT // 2)

            roi = thresh[y1:y2, x1:x2]
            if roi.size == 0:
                continue

            dark_pixels = cv2.countNonZero(roi)
            fill_ratio = dark_pixels / float(roi.size)
            scores[digit] = round(fill_ratio, 2)

        if not scores:
            lrn_digits.append("")
            continue

        top_digit, top_score = max(scores.items(), key=lambda x: x[1])
        top_score = round(top_score, 2)

        if top_score >= FILL_THRESHOLD:
            lrn_digits.append(str(top_digit))
        else:
            lrn_digits.append("")

    digit_details = []
    digit_confidences = []

    for d in lrn_digits:
        conf = normalize_conf(1.00 if d else 0.00)
        digit_confidences.append(conf)
        digit_details.append({
            "selected": d if d else None,
            "confidence": conf,
            "scores": {
                str(i): normalize_conf(1.00 if d == str(i) else 0.00)
                for i in range(10)
            }
        })

    lrn_value = "".join([d for d in lrn_digits if d]).strip() or None
    lrn_conf = normalize_conf(min(digit_confidences) if digit_confidences else 0.00)

    lrn_result = {
        "answer": lrn_value,
        "confidence": normalize_conf(lrn_conf),
        "review_required": (lrn_value is None) or (normalize_conf(lrn_conf) < REVIEW_THRESHOLD),
        "details": {
            "digits": digit_details
        }
    }

    return lrn_result
