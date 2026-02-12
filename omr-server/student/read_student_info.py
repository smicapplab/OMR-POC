import cv2
import numpy as np

from overlay_test import (
    build_last_name_grid,
    build_first_name_grid,
    build_mi_grid,
    build_month_grid,
    build_day_grid,
    build_year_grid,
    build_ssc_grid,
    build_4ps_grid,
    build_special_class_grid,
    build_gender_grid
)


# ----------------------------
# CONFIG
# ----------------------------
IMAGE_PATH = "template/answer3.png" 
FILL_THRESHOLD = 0.55
DOMINANCE_GAP = 0.07
ROI_WIDTH = 14
ROI_HEIGHT = 14

ROWS = [
    "A","B","C","D","E","F","G","H","I","J",
    "K","L","M","N","O","P","Q","R","S","T",
    "U","V","W","X","Y","Z","Ñ","-"
]

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
            scores[letter] = round(fill_ratio, 3)

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
            "confidence": round(top_score, 3),
            "status": status,
            "scores": scores
        }

    return detected_name.strip(), detailed


# ----------------------------
# WRAPPER
# ----------------------------
def read_student_info(
    img,
    last_grid,
    first_grid,
    mi_grid,
    month_grid,
    day_grid,
    year_grid,
    ssc_grid,
    four_ps_grid,
    special_class_grid,
    gender_grid
):
    # --- NAME ---
    last_name, last_detail = detect_name_from_grid(img, last_grid)
    first_name, first_detail = detect_name_from_grid(img, first_grid)
    mi, mi_detail = detect_name_from_grid(img, mi_grid)

    # --- BIRTH + SSC ---
    birth_info = read_birth_and_ssc(
        img,
        month_grid,
        day_grid,
        year_grid,
        ssc_grid
    )

    # --- 4Ps / Special Classes / Gender ---
    flags_info = read_student_flags(
        img,
        four_ps_grid,
        special_class_grid,
        gender_grid
    )

    return {
        "last_name": last_name,
        "first_name": first_name,
        "middle_initial": mi,
        "birth_month": birth_info["birth_month"],
        "birth_day": birth_info["birth_day"],
        "birth_year": birth_info["birth_year"],
        "ssc": birth_info["ssc"],
        "four_ps": flags_info["four_ps"],
        "special_classes": flags_info["special_classes"],
        "gender": flags_info["gender"],
        "details": {
            "last": last_detail,
            "first": first_detail,
            "mi": mi_detail
        }
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
            scores[label] = round(fill_ratio, 3)

        sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
        if not sorted_scores:
            return None

        top_label, top_score = sorted_scores[0]
        second_score = sorted_scores[1][1] if len(sorted_scores) > 1 else 0

        if top_score >= FILL_THRESHOLD and (top_score - second_score) >= DOMINANCE_GAP:
            return top_label
        return None

    # MONTH
    month_index = read_single_column(month_grid, MONTH_ROWS)
    month = None
    if month_index is not None:
        month = MONTH_ROWS[int(month_index)]

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

    # YEAR (2 columns 0–9 each) — relaxed dominance rule
    year = None
    year_cols = sorted(year_grid.keys())

    def read_year_column(grid):
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
            scores[label] = fill_ratio

        if not scores:
            return None

        top_label, top_score = max(scores.items(), key=lambda x: x[1])

        # Only require threshold, not dominance gap
        if top_score >= FILL_THRESHOLD:
            return str(top_label)

        return None

    if len(year_cols) >= 2:
        y1 = read_year_column(year_grid[year_cols[0]])
        y2 = read_year_column(year_grid[year_cols[1]])

        if y1 is not None and y2 is not None:
            year = y1 + y2

    # SSC (single bubble, no dominance rule)
    ssc = False
    for _, (x, y) in ssc_grid.items():
        x1 = int(x - ROI_WIDTH // 2)
        x2 = int(x + ROI_WIDTH // 2)
        y1 = int(y - ROI_HEIGHT // 2)
        y2 = int(y + ROI_HEIGHT // 2)

        roi = thresh[y1:y2, x1:x2]
        if roi.size == 0:
            continue

        dark_pixels = cv2.countNonZero(roi)
        fill_ratio = dark_pixels / float(roi.size)

        if fill_ratio >= FILL_THRESHOLD:
            ssc = True
            break

    return {
        "birth_month": month,
        "birth_day": day,
        "birth_year": year,
        "ssc": ssc
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
    gender = None

    for idx, (x, y) in gender_grid.items():
        if bubble_filled(x, y):
            gender = gender_labels[idx]
            break

    return {
        "four_ps": four_ps,
        "special_classes": selected_special,
        "gender": gender
    }


# ----------------------------
# OPTIONAL STANDALONE TEST
# ----------------------------
if __name__ == "__main__":
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print(f"Failed to load image: {IMAGE_PATH}")
    else:
        print("Image loaded successfully.")

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

        result = read_student_info(
            img,
            last_grid,
            first_grid,
            mi_grid,
            month_grid,
            day_grid,
            year_grid,
            ssc_grid,
            four_ps_grid,
            special_class_grid,
            gender_grid
        )

        print("\nDetected Student Info:")
        print(result)