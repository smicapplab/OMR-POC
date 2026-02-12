import cv2
import numpy as np

IMAGE_PATH = "template/template.png"
OUTPUT_PATH = "previous_school_overlay.png"

# =============================
# CALIBRATION POINTS (FROM PICKER)
# =============================

# School ID (Grade 6) calibration
# Click order:
# 1. Col1 top (0)
# 2. Col1 bottom (9)
# 3. Col2 top (0)
# 4. Col3 top (0)
# 5. Col4 top (0)
# 6. Col5 top (0)
# 7. Col6 top (0)

COL1_TOP = (1327, 2151)
COL1_BOTTOM = (1326, 2589)

COL_X = [
    1327,  # col1
    1376,  # col2
    1426,  # col3
    1473,  # col4
    1522,  # col5
    1571   # col6
]

ROW_COUNT = 10  # digits 0–9
ROI_RADIUS = 14

# =============================
# FINAL GRADE (GRADE 6) CALIBRATION
# =============================

# Math reference
# 1. Math tens top (6)
# 2. Math tens bottom (9)
# 3. Math ones top (0)
# 4. Math ones bottom (9)

MATH_TENS_TOP = (938, 2879)
MATH_TENS_BOTTOM = (937, 3026)

MATH_ONES_TOP = (987, 2879)
MATH_ONES_BOTTOM = (985, 3318)

# Other subjects (top row only for X positions)
# Order: English, Science, Filipino, AP
FINAL_GRADE_COL_X = [
    938,   # Math tens
    987,   # Math ones
    1084,  # English tens
    1134,  # English ones
    1230,  # Science tens
    1279,  # Science ones
    1375,  # Filipino tens
    1425,  # Filipino ones
    1522,  # AP tens
    1570   # AP ones
]

TENS_ROW_COUNT = 4   # 6,7,8,9
ONES_ROW_COUNT = 10  # 0–9

# =============================
# SCHOOL YEAR (SY) CALIBRATION
# =============================

SY_2015 = (646, 3173)
SY_BEFORE = (646, 3221)

# =============================
# CLASS SIZE CALIBRATION
# =============================

# 1. Tens top (0)
# 2. Tens bottom (9)
# 3. Ones top (0)
# 4. Ones bottom (9)

CLASS_TENS_TOP = (1716, 2881)
CLASS_TENS_BOTTOM = (1715, 3319)

CLASS_ONES_TOP = (1764, 2880)
CLASS_ONES_BOTTOM = (1766, 3317)

CLASS_ROW_COUNT = 10


# =============================
# GRID BUILDER
# =============================

def build_prev_school_id_grid():
    vertical_spacing = (COL1_BOTTOM[1] - COL1_TOP[1]) / (ROW_COUNT - 1)

    row_y = [
        int(COL1_TOP[1] + i * vertical_spacing)
        for i in range(ROW_COUNT)
    ]

    return {
        "col_x": COL_X,
        "row_y": row_y
    }

def build_final_grade_grid():
    tens_spacing = (MATH_TENS_BOTTOM[1] - MATH_TENS_TOP[1]) / (TENS_ROW_COUNT - 1)
    ones_spacing = (MATH_ONES_BOTTOM[1] - MATH_ONES_TOP[1]) / (ONES_ROW_COUNT - 1)

    tens_row_y = [
        int(MATH_TENS_TOP[1] + i * tens_spacing)
        for i in range(TENS_ROW_COUNT)
    ]

    ones_row_y = [
        int(MATH_ONES_TOP[1] + i * ones_spacing)
        for i in range(ONES_ROW_COUNT)
    ]

    return {
        "col_x": FINAL_GRADE_COL_X,
        "tens_row_y": tens_row_y,
        "ones_row_y": ones_row_y
    }

def build_sy_grid():
    return {
        "options": [
            SY_2015,
            SY_BEFORE
        ]
    }

def build_class_size_grid():
    tens_spacing = (CLASS_TENS_BOTTOM[1] - CLASS_TENS_TOP[1]) / (CLASS_ROW_COUNT - 1)
    ones_spacing = (CLASS_ONES_BOTTOM[1] - CLASS_ONES_TOP[1]) / (CLASS_ROW_COUNT - 1)

    tens_row_y = [
        int(CLASS_TENS_TOP[1] + i * tens_spacing)
        for i in range(CLASS_ROW_COUNT)
    ]

    ones_row_y = [
        int(CLASS_ONES_TOP[1] + i * ones_spacing)
        for i in range(CLASS_ROW_COUNT)
    ]

    return {
        "tens_col_x": CLASS_TENS_TOP[0],
        "ones_col_x": CLASS_ONES_TOP[0],
        "tens_row_y": tens_row_y,
        "ones_row_y": ones_row_y
    }


# =============================
# OVERLAY DRAWING
# =============================

def draw_overlay():
    img = cv2.imread(IMAGE_PATH)

    if img is None:
        print(f"Failed to load image: {IMAGE_PATH}")
        return

    school_id_grid = build_prev_school_id_grid()
    final_grade_grid = build_final_grade_grid()
    sy_grid = build_sy_grid()
    class_grid = build_class_size_grid()

    # ---- Draw School ID grid (magenta)
    for col_x in school_id_grid["col_x"]:
        for row_y in school_id_grid["row_y"]:
            cv2.circle(
                img,
                (int(col_x), int(row_y)),
                ROI_RADIUS,
                (255, 0, 255),
                2
            )

    # ---- Draw Final Grade grid
    col_x_list = final_grade_grid["col_x"]

    for idx, col_x in enumerate(col_x_list):

        # Even index → tens column (4 rows)
        if idx % 2 == 0:
            for row_y in final_grade_grid["tens_row_y"]:
                cv2.circle(
                    img,
                    (int(col_x), int(row_y)),
                    ROI_RADIUS,
                    (0, 255, 255),
                    2
                )

        # Odd index → ones column (10 rows)
        else:
            for row_y in final_grade_grid["ones_row_y"]:
                cv2.circle(
                    img,
                    (int(col_x), int(row_y)),
                    ROI_RADIUS,
                    (0, 255, 0),
                    2
                )

    # ---- Draw SY bubbles (blue)
    for (x, y) in sy_grid["options"]:
        cv2.circle(
            img,
            (int(x), int(y)),
            ROI_RADIUS,
            (255, 0, 0),
            2
        )

    # ---- Draw Class Size grid
    # Tens column (cyan)
    for row_y in class_grid["tens_row_y"]:
        cv2.circle(
            img,
            (int(class_grid["tens_col_x"]), int(row_y)),
            ROI_RADIUS,
            (255, 255, 0),
            2
        )

    # Ones column (white)
    for row_y in class_grid["ones_row_y"]:
        cv2.circle(
            img,
            (int(class_grid["ones_col_x"]), int(row_y)),
            ROI_RADIUS,
            (255, 255, 255),
            2
        )

    cv2.imwrite(OUTPUT_PATH, img)
    print(f"Overlay saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    draw_overlay()