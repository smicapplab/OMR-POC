import cv2
import numpy as np

IMAGE_PATH = "../template/answer3.png"

# ---- ROI Config (must match calibration model) ----
ROI_WIDTH = 32
ROI_HEIGHT = 24
FILL_THRESHOLD = 0.20
DOMINANCE_GAP = 0.07  # minimum difference between top and second score
REVIEW_THRESHOLD = 0.60

# ---- Calibration clicks (6 per subject) ----
# Order per subject:
# Q1A, Q8A, Q9A, Q17A, Q25A, Q33A

clicks = [
    # ===== MATH =====
    (714,4391), (715,4731), (1055,4390), (1394,4391), (1736,4391), (2076,4390),

    # ===== ENGLISH =====
    (714,4830), (713,5169), (1054,4828), (1395,4829), (1735,4828), (2077,4828),

    # ===== SCIENCE =====
    (714,5265), (714,5607), (1056,5265), (1396,5265), (1736,5265), (2076,5265),

    # ===== FILIPINO =====
    (715,5703), (715,6044), (1056,5703), (1394,5703), (1735,5703), (2076,5703),

    # ===== AP =====
    (714,6140), (713,6481), (1055,6140), (1395,6141), (1736,6142), (2076,6141),
]

SUBJECTS = ["math", "english", "science", "filipino", "ap"]


def build_subject_grid(subject_clicks):
    q1A, q8A, q9A, q17A, q25A, q33A = subject_clicks

    base_y = q1A[1]
    row_spacing = (q8A[1] - q1A[1]) / 7.0
    col_spacing = 48  # stable from template geometry

    block_x_origins = [
        q1A[0],
        q9A[0],
        q17A[0],
        q25A[0],
        q33A[0],
    ]

    grid = {}

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


def detect_answers(
    img
):
    gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    gray = cv2.equalizeHist(gray)

    thresh = cv2.adaptiveThreshold(
        gray,
        255,
        cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        5
    )

    results = {}

    calibrated_subject_count = len(clicks) // 6

    for i in range(calibrated_subject_count):
        subject = SUBJECTS[i]
        subject_clicks = clicks[i*6:(i+1)*6]
        grid = build_subject_grid(subject_clicks)

        subject_result = {
            "answers": {},
        }

        for q in sorted(grid.keys()):
            scores = {}
            marked_choices = []

            for choice, (x, y) in grid[q].items():
                x1 = int(x - ROI_WIDTH // 2)
                x2 = int(x + ROI_WIDTH // 2)
                y1 = int(y - ROI_HEIGHT // 2)
                y2 = int(y + ROI_HEIGHT // 2)

                roi = thresh[y1:y2, x1:x2]
                if roi.size == 0:
                    scores[choice] = 0.0
                    continue

                dark_pixels = cv2.countNonZero(roi)
                fill_ratio = dark_pixels / float(roi.size)

                scores[choice] = round(float(fill_ratio), 2)

                if fill_ratio > FILL_THRESHOLD:
                    marked_choices.append((choice, fill_ratio))

            # Sort by raw (non-rounded) confidence for decision logic
            marked_choices.sort(key=lambda x: x[1], reverse=True)

            if len(marked_choices) == 0:
                answer = None
                confidence = 0.0
                review_required = True
            else:
                top_choice, top_conf = marked_choices[0]

                if len(marked_choices) > 1:
                    second_conf = marked_choices[1][1]
                    dominance = top_conf - second_conf
                    if dominance < DOMINANCE_GAP:
                        review_required = True
                    else:
                        review_required = top_conf < REVIEW_THRESHOLD
                else:
                    review_required = top_conf < REVIEW_THRESHOLD

                answer = top_choice
                confidence = round(float(top_conf), 2)

            subject_result["answers"][str(q)] = {
                "answer": answer,
                "confidence": round(float(confidence), 2),
                "review_required": review_required,
                "details": {
                    "scores": scores
                }
            }

        results[subject] = subject_result
    
    return results
