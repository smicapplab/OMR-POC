import cv2
import numpy as np
import random
from scipy.ndimage import gaussian_filter
from pencil_shape import generate_pill_texture_layer

# ===== Simulation Controls =====
ANSWER_ALL = True
ALLOW_PARTIAL = True
ALLOW_DOUBLE = True
ALLOW_ERASE = False
PARTIAL_PROB = 0.15
DOUBLE_PROB = 0.08
ERASE_PROB = 0.05

TEMPLATE_PATH = "template/template.png"
OUTPUT_PATH = "template/simulated_answer.png"

# ---- Calibration clicks (6 per subject) ----
clicks = [
    # MATH
    (714,4391), (715,4731), (1055,4390), (1394,4391), (1736,4391), (2076,4390),
    # ENGLISH
    (714,4830), (713,5169), (1054,4828), (1395,4829), (1735,4828), (2077,4828),
    # SCIENCE
    (714,5265), (714,5607), (1056,5265), (1396,5265), (1736,5265), (2076,5265),
    # FILIPINO
    (715,5703), (715,6044), (1056,5703), (1394,5703), (1735,5703), (2076,5703),
    # AP
    (714,6140), (713,6481), (1055,6140), (1395,6141), (1736,6142), (2076,6141),
]

SUBJECTS = ["math", "english", "science", "filipino", "ap"]


def build_subject_grid(subject_clicks):
    q1A, q8A, q9A, q17A, q25A, q33A = subject_clicks

    base_y = q1A[1]
    row_spacing = (q8A[1] - q1A[1]) / 7.0
    col_spacing = 48

    block_x_origins = [q1A[0], q9A[0], q17A[0], q25A[0], q33A[0]]

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


# =========================
# Stroke-based pencil fill
# =========================
def simulate_pencil_fill(img, cx, cy, intensity=1.0, allow_bleed=True):
    h, w = img.shape[:2]

    pill_rx = 13
    pill_ry = 8

    # Slight off-center placement
    cx += random.uniform(-4, 4)
    cy += random.uniform(-3, 3)

    # ---------------------------------
    # 1. Generate standalone pill field
    # ---------------------------------
    base_w = 250
    base_h = 200

    base_cx = base_w // 2
    base_cy = base_h // 2

    stroke_layer = generate_pill_texture_layer(
        base_h,
        base_w,
        base_cx,
        base_cy,
        base_w * 0.28,
        base_h * 0.22
    )

    # Normalize to 0–1
    stroke_layer = np.clip(stroke_layer, 0, 1.8) / 1.8

    # ---------------------------------
    # 2. Resize to actual pill size (larger + slight randomness)
    # ---------------------------------
    # Make pill clearly fill the bubble
    scale_variation = random.uniform(6, 7)

    target_w = int(pill_rx * scale_variation)
    target_h = int(pill_ry * scale_variation)

    resized = cv2.resize(stroke_layer, (target_w, target_h), interpolation=cv2.INTER_AREA)

    # ---------------------------------
    # 3. Compute placement box
    # ---------------------------------
    x1 = int(cx - target_w // 2)
    y1 = int(cy - target_h // 2)
    x2 = x1 + target_w
    y2 = y1 + target_h

    # Clip to image bounds
    if x1 < 0 or y1 < 0 or x2 > w or y2 > h:
        return

    roi = img[y1:y2, x1:x2]

    # ---------------------------------
    # 4. Multiply blend into paper
    # ---------------------------------
    roi_float = roi.astype(np.float32) / 255.0

    #graphite_strength = resized * 0.85 * intensity
    graphite_strength = resized * 1.35 * intensity

    graphite_strength = np.clip(graphite_strength, 0, 1)

    blended = roi_float * (1.0 - graphite_strength[:, :, None])

    img[y1:y2, x1:x2] = (blended * 255).astype(np.uint8)


def simulate_erase(img, x, y, h, w, pill_rx=13, pill_ry=8):
    ex1 = max(0, x - pill_rx - 4)
    ex2 = min(w, x + pill_rx + 4)
    ey1 = max(0, y - pill_ry - 3)
    ey2 = min(h, y + pill_ry + 3)

    erase_region = img[ey1:ey2, ex1:ex2].astype(np.float32)
    if erase_region.size == 0:
        return

    erh, erw = erase_region.shape[:2]
    yg, xg = np.mgrid[0:erh, 0:erw].astype(np.float32)

    dist_from_center = np.sqrt(
        ((xg - erw / 2) / (erw / 2)) ** 2 +
        ((yg - erh / 2) / (erh / 2)) ** 2
    )
    erase_mask = np.clip(1.0 - dist_from_center * 0.5, 0.5, 1.0)[:, :, None]

    erase_strength = random.uniform(0.50, 0.72)
    paper_tone = random.uniform(228, 248)
    paper_color = np.full_like(erase_region, paper_tone)

    lightened = (erase_region * (1 - erase_mask * erase_strength) +
                 paper_color * (erase_mask * erase_strength))

    debris = np.random.normal(0, 5, (erh, erw, 3)).astype(np.float32)
    lightened = np.clip(lightened + debris, 0, 255)

    img[ey1:ey2, ex1:ex2] = lightened.astype(np.uint8)


def main():
    img = cv2.imread(TEMPLATE_PATH)
    if img is None:
        print("ERROR: Could not load template image.")
        return

    h, w = img.shape[:2]
    calibrated_subject_count = len(clicks) // 6

    for i in range(calibrated_subject_count):
        subject_clicks = clicks[i * 6:(i + 1) * 6]
        grid = build_subject_grid(subject_clicks)

        for q in grid:
            choices = ["A", "B", "C", "D"]
            primary = random.choice(choices)
            x, y = grid[q][primary]

            intensity = 1.0
            if ALLOW_PARTIAL and random.random() < PARTIAL_PROB:
                intensity = random.uniform(0.3, 0.62)

            simulate_pencil_fill(img, x, y, intensity=intensity)

            if ALLOW_DOUBLE and random.random() < DOUBLE_PROB:
                secondary = random.choice([c for c in choices if c != primary])
                x2, y2 = grid[q][secondary]
                simulate_pencil_fill(img, x2, y2, intensity=0.8)

            if ALLOW_ERASE and random.random() < ERASE_PROB:
                simulate_erase(img, x, y, h, w)

    cv2.imwrite(OUTPUT_PATH, img)
    print("Simulated answer sheet saved to", OUTPUT_PATH)


if __name__ == "__main__":
    main()