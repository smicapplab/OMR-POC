import cv2
import numpy as np

IMAGE_PATH = "template/template.png"
OUTPUT_PATH = "overlay_result.png"

BUBBLE_RADIUS = 16
SUBJECTS = ["math", "english", "science", "filipino", "ap"]

# 20 clicks per subject:
# Q1  A-D  (vertical anchor top)
# Q8  A-D  (vertical anchor bottom within same block)
# Q1  A-D across 5 horizontal blocks (same visual row)

clicks = [
    # ===== MATH (6-point calibration) =====
    (714,4391),  # Q1 A
    (714,4731),  # Q8 A
    (1055,4390), # Q9 A
    (1394,4391), # Q17 A
    (1736,4391), # Q25 A
    (2076,4390), # Q33 A

    # ===== ENGLISH (6-point calibration) =====
    (714,4830),  # Q1 A
    (714,5169),  # Q8 A
    (1054,4828), # Q9 A
    (1395,4829), # Q17 A
    (1735,4828), # Q25 A
    (2077,4828), # Q33 A

    # ===== SCIENCE (6-point calibration) =====
    (714,5265),  # Q1 A
    (714,5607),  # Q8 A
    (1056,5265), # Q9 A
    (1396,5265), # Q17 A
    (1736,5265), # Q25 A
    (2076,5265), # Q33 A

    # ===== FILIPINO (6-point calibration) =====
    (715,5703),  # Q1 A
    (715,6044),  # Q8 A
    (1056,5703), # Q9 A
    (1394,5703), # Q17 A
    (1735,5703), # Q25 A
    (2076,5703), # Q33 A

    # ===== AP (6-point calibration) =====
    (714,6140),  # Q1 A
    (713,6481),  # Q8 A
    (1055,6140), # Q9 A
    (1395,6141), # Q17 A
    (1736,6142), # Q25 A
    (2076,6141), # Q33 A
]



def build_subject_grid(subject_clicks):
    """
    6-point calibration per subject:
    0: Q1 A
    1: Q8 A
    2: Q9 A
    3: Q17 A
    4: Q25 A
    5: Q33 A
    """

    q1A  = subject_clicks[0]
    q8A  = subject_clicks[1]
    q9A  = subject_clicks[2]
    q17A = subject_clicks[3]
    q25A = subject_clicks[4]
    q33A = subject_clicks[5]

    # ---- Vertical Spacing ----
    base_y = q1A[1]
    row_spacing = (q8A[1] - q1A[1]) / 7.0

    # ---- Column Spacing (temporary fixed value until B click provided) ----
    col_spacing = 48

    # ---- Block X Origins ----
    block_x_origins = [
        q1A[0],   # Q1–Q8
        q9A[0],   # Q9–Q16
        q17A[0],  # Q17–Q24
        q25A[0],  # Q25–Q32
        q33A[0],  # Q33–Q40
    ]

    grid = {}

    # 5 blocks × 8 rows
    for block_index in range(5):
        start_q = block_index * 8 + 1
        x_origin = block_x_origins[block_index]

        for i in range(8):
            q_num = start_q + i
            y = int(base_y + i * row_spacing)

            row = {}
            for j in range(4):
                x = int(x_origin + j * col_spacing)
                row[chr(ord('A') + j)] = (x, y)

            grid[q_num] = row

    return grid


def main():
    img = cv2.imread(IMAGE_PATH)
    overlay = img.copy()

    full_grid = {}

    # Determine how many subjects actually have calibration data
    calibrated_subject_count = len(clicks) // 6

    for i in range(calibrated_subject_count):
        subject = SUBJECTS[i]
        subject_clicks = clicks[i*6:(i+1)*6]
        full_grid[subject] = build_subject_grid(subject_clicks)

    for subject in full_grid:
        for q in full_grid[subject]:
            for choice in full_grid[subject][q]:
                x, y = full_grid[subject][q][choice]
                cv2.circle(overlay, (x, y), BUBBLE_RADIUS, (0,255,0), 2)

    cv2.imwrite(OUTPUT_PATH, overlay)
    print("Overlay saved to", OUTPUT_PATH)


if __name__ == "__main__":
    main()