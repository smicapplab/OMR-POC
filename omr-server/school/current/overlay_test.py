import cv2
import numpy as np

IMAGE_PATH = "template/template.png" 
OUTPUT_PATH = "current_school_overlay.png"

# =============================
# CALIBRATION POINTS (FROM PICKER)
# =============================

# REGION
REGION_TOP = (793, 2104)
REGION_BOTTOM = (793, 2879)
REGION_ROWS = 17  # adjust if needed

# DIVISION
DIV_COL1_TOP = (841, 2150)
DIV_COL1_BOTTOM = (841, 2588)
DIV_LAST_TOP = (890, 2150)
DIV_ROWS = 10  # digits 0–9
DIV_COLS = 2   # adjust if needed

# SCHOOL ID
SID_COL1_TOP = (939, 2150)
SID_COL1_BOTTOM = (938, 2589)
SID_COL_X = [939, 986, 1035, 1084, 1132, 1182]
SID_ROWS = 10  # digits 0–9

# SCHOOL TYPE (Grade 7) – manual anchors (no interpolation)
SCHOOL_TYPE_POINTS = [
    (159, 2734),  # National Barangay / Community HS
    (159, 2831),  # National Comprehensive HS
    (159, 2881),  # Integrated School
    (159, 2930),  # Public Science HS
    (159, 2976),  # Public Vocational HS
    (159, 3025),  # State College / University
    (159, 3122),  # Private Non-Sectarian HS
    (159, 3173),  # Private Sectarian HS
    (159, 3220),  # Private Vocational HS
    (159, 3267),  # Private Science HS
]

ROI_RADIUS = 14

# =============================
# GRID BUILDERS
# =============================

def build_region_grid():
    grid = {}
    vertical_spacing = (REGION_BOTTOM[1] - REGION_TOP[1]) / (REGION_ROWS - 1)

    for row in range(REGION_ROWS):
        y = int(REGION_TOP[1] + row * vertical_spacing)
        grid[row] = (REGION_TOP[0], y)

    return grid


def build_division_grid():
    grid = {}
    vertical_spacing = (DIV_COL1_BOTTOM[1] - DIV_COL1_TOP[1]) / (DIV_ROWS - 1)
    horizontal_spacing = (DIV_LAST_TOP[0] - DIV_COL1_TOP[0]) / (DIV_COLS - 1)

    for col in range(DIV_COLS):
        x = int(DIV_COL1_TOP[0] + col * horizontal_spacing)
        grid[col] = {}
        for row in range(DIV_ROWS):
            y = int(DIV_COL1_TOP[1] + row * vertical_spacing)
            grid[col][row] = (x, y)

    return grid


def build_school_id_grid():
    grid = {}
    vertical_spacing = (SID_COL1_BOTTOM[1] - SID_COL1_TOP[1]) / (SID_ROWS - 1)

    for col, x in enumerate(SID_COL_X):
        grid[col] = {}
        for row in range(SID_ROWS):
            y = int(SID_COL1_TOP[1] + row * vertical_spacing)
            grid[col][row] = (x, y)

    return grid


def build_school_type_grid():
    return {i: pt for i, pt in enumerate(SCHOOL_TYPE_POINTS)}


# =============================
# OVERLAY DRAWING
# =============================

def draw_overlay():
    img = cv2.imread(IMAGE_PATH)
    if img is None:
        print("Image failed to load.")
        return

    region_grid = build_region_grid()
    division_grid = build_division_grid()
    school_id_grid = build_school_id_grid()
    school_type_grid = build_school_type_grid()

    # Draw REGION
    for _, (x, y) in region_grid.items():
        cv2.circle(img, (x, y), ROI_RADIUS, (0, 255, 0), 2)

    # Draw DIVISION
    for col in division_grid:
        for row in division_grid[col]:
            x, y = division_grid[col][row]
            cv2.circle(img, (x, y), ROI_RADIUS, (255, 0, 0), 2)

    # Draw SCHOOL ID
    for col in school_id_grid:
        for row in school_id_grid[col]:
            x, y = school_id_grid[col][row]
            cv2.circle(img, (x, y), ROI_RADIUS, (0, 0, 255), 2)

    # Draw SCHOOL TYPE
    for _, (x, y) in school_type_grid.items():
        cv2.circle(img, (x, y), ROI_RADIUS, (255, 255, 0), 2)

    cv2.imwrite(OUTPUT_PATH, img)
    print(f"Overlay saved to {OUTPUT_PATH}")


if __name__ == "__main__":
    draw_overlay()