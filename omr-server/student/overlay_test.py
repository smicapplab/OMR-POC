import cv2
import numpy as np

ROWS = [
    "A","B","C","D","E","F","G","H","I","J",
    "K","L","M","N","O","P","Q","R","S","T",
    "U","V","W","X","Y","Z","Ñ","-"
]

ROW_COUNT = len(ROWS)

TEMPLATE_PATH = "template/template.png"
OUTPUT_PATH = "overlay_result.png"

# Provided calibration clicks (LAST NAME)
# 1: Column 1 - A
# 2: Column 1 - -
# 3: Column 2 - A
col1_A = (307, 597)
col1_dash = (307, 1908)
col2_A = (354, 595)

# Manually mapped Column-A positions (add more if needed)
# Currently using first two detected columns
COLUMN_A_POINTS = [
    (307, 597),
    (356, 596),
    (403, 595),
    (451, 597),
    (501, 595),
    (549, 597),
    (598, 596),
    (646, 598),
    (695, 596),
    (744, 596),
    (793, 595),
    (841, 597),
    (890, 596),
    (939, 597),
    (987, 596),
]

base_row_y = np.mean([pt[1] for pt in COLUMN_A_POINTS])

# FIRST NAME calibration
first_col1_A = (1085, 596)
first_col1_dash = (1083, 1907)

FIRST_COLUMN_A_POINTS = [
    (1085, 596),
    (1133, 596),
    (1181, 596),
    (1230, 596),
    (1279, 596),
    (1328, 596),
    (1376, 596),
    (1424, 596),
    (1474, 596),
    (1523, 596),
    (1571, 596),
    (1620, 596),
    (1668, 596),
    (1717, 598),
    (1764, 596),
    (1813, 596),
    (1862, 596),
    (1910, 596),
    (1959, 598),
]

first_base_row_y = np.mean([pt[1] for pt in FIRST_COLUMN_A_POINTS])
first_vertical_spacing = (first_col1_dash[1] - first_col1_A[1]) / (ROW_COUNT - 1)


vertical_spacing = (col1_dash[1] - col1_A[1]) / (ROW_COUNT - 1)

# MI calibration
mi_col1_A = (2057, 598)
mi_col1_dash = (2056, 1907)

MI_COLUMN_A_POINTS = [
    (2058, 596),
    (2106, 597),
]

# =============================
# BIRTH DATE CALIBRATION
# =============================

# MONTH (JAN–DEC)
MONTH_TOP = (1910, 2783)
MONTH_BOTTOM = (1910, 3318)
MONTH_COUNT = 12

# DAY (2 columns)
# Column 1 = 0–3
DAY_COL1_TOP = (2105, 2880)
DAY_COL1_BOTTOM = (2105, 3027)
DAY_COL1_ROWS = 4

# Column 2 = 0–9
DAY_COL2_TOP = (2154, 2879)
DAY_COL2_ROWS = 10

# YEAR (2 columns, 0–9 each)
YEAR_COL1_TOP = (2202, 2879)
YEAR_COL1_BOTTOM = (2202, 3319)
YEAR_COL2_TOP = (2251, 2880)
YEAR_ROWS = 10


# SSC
SSC_POINT = (1958, 3462)

# =============================
# 4Ps / SPECIAL CLASSES / GENDER
# =============================

# 4Ps (Yes, No, I don't know)
FOUR_PS_POINTS = [
    (178, 3951),   # Yes
    (373, 3950),   # No
    (568, 3952),   # I don't know
]

# Special Classes (left → right, top row first)
SPECIAL_CLASS_POINTS = [
    (859, 3949),   # Special science class
    (859, 3999),   # Special educational class
    (1297, 3950),  # Class under MISOSA
    (1296, 3998),  # Class in a BRAC
    (1685, 3950),  # ALIVE / Madrasah class
]

# Gender (Male, Female)
GENDER_POINTS = [
    (2172, 3951),  # Male
    (2173, 3999),  # Female
]

def build_last_name_grid():
    grid = {}

    for col_index, (col_x, _) in enumerate(COLUMN_A_POINTS):
        column_dict = {}

        for r in range(ROW_COUNT):
            y = base_row_y + r * vertical_spacing
            column_dict[ROWS[r]] = (int(round(col_x)), int(round(y)))

        grid[col_index] = column_dict

    return grid


# Build FIRST NAME grid
def build_first_name_grid():
    grid = {}

    for col_index, (col_x, _) in enumerate(FIRST_COLUMN_A_POINTS):
        column_dict = {}

        for r in range(ROW_COUNT):
            y = first_base_row_y + r * first_vertical_spacing
            column_dict[ROWS[r]] = (int(round(col_x)), int(round(y)))

        grid[col_index] = column_dict

    return grid


def build_mi_grid():
    grid = {}

    mi_base_row_y = np.mean([pt[1] for pt in MI_COLUMN_A_POINTS])
    mi_vertical_spacing = (mi_col1_dash[1] - mi_col1_A[1]) / (ROW_COUNT - 1)

    for col_index, (col_x, _) in enumerate(MI_COLUMN_A_POINTS):
        column_dict = {}

        for r in range(ROW_COUNT):
            y = mi_base_row_y + r * mi_vertical_spacing
            column_dict[ROWS[r]] = (int(round(col_x)), int(round(y)))

        grid[col_index] = column_dict

    return grid



# ----------------------------
# BIRTH GRID BUILDERS
# ----------------------------

def build_month_grid():
    grid = {}
    vertical_spacing = (MONTH_BOTTOM[1] - MONTH_TOP[1]) / (MONTH_COUNT - 1)

    for r in range(MONTH_COUNT):
        y = MONTH_TOP[1] + r * vertical_spacing
        grid[r] = (int(round(MONTH_TOP[0])), int(round(y)))

    return grid


def build_day_grid():
    grid = {}

    # Column 1 (0–3)
    col1_spacing = (DAY_COL1_BOTTOM[1] - DAY_COL1_TOP[1]) / (DAY_COL1_ROWS - 1)
    grid[0] = {}
    for r in range(DAY_COL1_ROWS):
        y = DAY_COL1_TOP[1] + r * col1_spacing
        grid[0][r] = (int(round(DAY_COL1_TOP[0])), int(round(y)))

    # Column 2 (0–9)
    grid[1] = {}
    for r in range(DAY_COL2_ROWS):
        y = DAY_COL1_TOP[1] + r * col1_spacing
        grid[1][r] = (int(round(DAY_COL2_TOP[0])), int(round(y)))

    return grid


def build_year_grid():
    grid = {}
    vertical_spacing = (YEAR_COL1_BOTTOM[1] - YEAR_COL1_TOP[1]) / (YEAR_ROWS - 1)

    col_x = [YEAR_COL1_TOP[0], YEAR_COL2_TOP[0]]

    for col in range(2):
        grid[col] = {}
        for r in range(YEAR_ROWS):
            y = YEAR_COL1_TOP[1] + r * vertical_spacing
            grid[col][r] = (int(round(col_x[col])), int(round(y)))

    return grid


def build_ssc_grid():
    return {0: SSC_POINT}


# 4Ps, Special Classes, Gender grid builders
def build_4ps_grid():
    return {i: pt for i, pt in enumerate(FOUR_PS_POINTS)}

def build_special_class_grid():
    return {i: pt for i, pt in enumerate(SPECIAL_CLASS_POINTS)}

def build_gender_grid():
    return {i: pt for i, pt in enumerate(GENDER_POINTS)}


def main():
    img = cv2.imread(TEMPLATE_PATH)
    if img is None:
        print("Failed to load template.")
        return

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

    # Draw LAST NAME overlay (red)
    for col in last_grid:
        for letter in last_grid[col]:
            x, y = last_grid[col][letter]
            cv2.circle(img, (x, y), 10, (0, 0, 255), 2)

    # Draw FIRST NAME overlay (blue)
    for col in first_grid:
        for letter in first_grid[col]:
            x, y = first_grid[col][letter]
            cv2.circle(img, (x, y), 10, (255, 0, 0), 2)

    # Draw MI overlay (green)
    for col in mi_grid:
        for letter in mi_grid[col]:
            x, y = mi_grid[col][letter]
            cv2.circle(img, (x, y), 10, (0, 255, 0), 2)

    # Draw MONTH overlay (yellow)
    for _, (x, y) in month_grid.items():
        cv2.circle(img, (x, y), 10, (0, 255, 255), 2)

    # Draw DAY overlay (purple)
    for col in day_grid:
        for r in day_grid[col]:
            x, y = day_grid[col][r]
            cv2.circle(img, (x, y), 10, (255, 0, 255), 2)

    # Draw YEAR overlay (black)
    for col in year_grid:
        for r in year_grid[col]:
            x, y = year_grid[col][r]
            cv2.circle(img, (x, y), 10, (0, 0, 0), 2)

    # Draw SSC overlay (orange)
    for _, (x, y) in ssc_grid.items():
        cv2.circle(img, (x, y), 10, (0, 128, 255), 2)

    # Draw 4Ps overlay (cyan)
    for _, (x, y) in four_ps_grid.items():
        cv2.circle(img, (x, y), 10, (255, 255, 0), 2)

    # Draw Special Classes overlay (pink)
    for _, (x, y) in special_class_grid.items():
        cv2.circle(img, (x, y), 10, (255, 0, 128), 2)

    # Draw Gender overlay (white)
    for _, (x, y) in gender_grid.items():
        cv2.circle(img, (x, y), 10, (255, 255, 255), 2)

    cv2.imwrite(OUTPUT_PATH, img)
    print(f"Overlay saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    main()