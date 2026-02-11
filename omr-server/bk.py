import cv2
import numpy as np
import json
import os

FILE = "gilvert-2.png"


# ================= CONSTANTS =================
QUESTIONS_PER_BLOCK = 8
BLOCKS = 5
CHOICES = 4
CHOICE_LABELS = ["A", "B", "C", "D"]

DEBUG_PILL_DUMP = True

# ================= SCORING TUNING =================
LETTER_MASK_RATIO = 0.35   # left side contains printed A/B/C/D
MIN_INK_RATIO = 0.04       # below = BLANK
DOMINANCE_RATIO = 1.6      # winner must beat runner-up by 60%
DEBUG_DIR = "debug_pills"

AUTO_CALIBRATE_MIN_INK = True
GLOBAL_MIN_INK_FLOOR = 0.010
CALIBRATION_PERCENTILE = 15  # percentile of filled answers

if DEBUG_PILL_DUMP and not os.path.exists(DEBUG_DIR):
    os.makedirs(DEBUG_DIR)

# ================= GEOMETRY (LOCKED) =================
from overlay_test import (
    ANCHOR_X,
    CHOICE_X_OFFSETS,
    BLOCK_X_OFFSETS,
    SUBJECT_Y,
    ROW_GAP,
    PILL_W,
    PILL_H,
)

# Inner padding to ignore printed letter and pill border
INNER_PAD_X = int(PILL_W * 0.45)   # aggressively remove printed A/B/C/D
INNER_PAD_Y = int(PILL_H * 0.35)   # avoid pill border/top bleed


# ================= IMAGE LOAD =================
img = cv2.imread("template/" + FILE)
if img is None:
    raise RuntimeError("Failed to load template/" + FILE)

# ================= DESKEW (ROTATION ONLY) =================
def deskew(image):
    # Convert to grayscale
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Suppress colored noise (orange outlines / letters)
    # Keep only dark pixels
    _, dark = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)

    # Morphological close to connect text/lines
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, kernel)

    # Get coordinates of dark pixels only
    coords = np.column_stack(np.where(dark > 0))
    if coords.size < 1000:
        # Not enough signal, skip deskew
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)

img = deskew(img)

# ================= ADAPTIVE THRESHOLD (PENCIL + SCAN SAFE) =================
gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

thresh = cv2.adaptiveThreshold(
    gray,
    255,
    cv2.ADAPTIVE_THRESH_MEAN_C,
    cv2.THRESH_BINARY_INV,
    21,
    10
)

# Strengthen thin pencil / digital strokes (close gaps instead of eroding)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# ================= HELPERS =================
def fill_ratio(thresh_img, x1, y1, x2, y2, debug_tag=None):
    roi = thresh_img[y1:y2, x1:x2]
    if roi.size == 0:
        return 0.0, 0.0

    h, w = roi.shape

    # Mask out printed letter (left) and pill border
    mask = np.zeros_like(roi, dtype=np.uint8)
    mask[
        int(h * 0.20):int(h * 0.85),
        int(w * 0.40):int(w * 0.95)
    ] = 255

    ink = cv2.bitwise_and(roi, roi, mask=mask)

    contours, _ = cv2.findContours(
        ink, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )

    weighted_area = 0.0
    max_area = 0.0

    cy, cx = h // 2, w // 2
    max_dist = np.hypot(cx, cy)

    for cnt in contours:
        area = cv2.contourArea(cnt)
        if area < 12:
            continue

        x,y,wc,hc = cv2.boundingRect(cnt)

        # reject border-touching or elongated contours (printed letter / border)
        if x <= 1 or y <= 1 or (x+wc) >= (w-1) or (y+hc) >= (h-1):
            continue
        if wc > w*0.6 or hc > h*0.6:
            continue

        M = cv2.moments(cnt)
        if M["m00"] == 0:
            continue

        px = int(M["m10"] / M["m00"])
        py = int(M["m01"] / M["m00"])

        dist = np.hypot(px - cx, py - cy)

        # hard center bias – pencil fills cluster near center
        if dist > max_dist * 0.55:
            continue

        weight = 1.0 - (dist / (max_dist * 0.55))
        weighted_area += area * weight

    valid_pixels = cv2.countNonZero(mask)
    weighted_score = weighted_area / valid_pixels if valid_pixels else 0.0
    max_score = max_area / valid_pixels if valid_pixels else 0.0

    if DEBUG_PILL_DUMP and debug_tag:
        cv2.imwrite(f"{DEBUG_DIR}/{debug_tag}_roi.png", roi)
        cv2.imwrite(f"{DEBUG_DIR}/{debug_tag}_masked.png", ink)
        heat = cv2.applyColorMap(
            cv2.normalize(ink, None, 0, 255, cv2.NORM_MINMAX),
            cv2.COLORMAP_JET
        )
        cv2.imwrite(f"{DEBUG_DIR}/{debug_tag}_heat.png", heat)
        print(
            f"[DEBUG] {debug_tag} contours={len(contours)} "
            f"max_area={max_area:.1f} weighted_area={weighted_area:.1f} "
            f"weighted_score={weighted_score:.3f} max_score={max_score:.3f}"
        )

    return round(weighted_score, 3), round(max_score, 3)

# ================= OMR EXTRACTION =================
results = {}
page_max_scores = { }

for subject, anchor_y in SUBJECT_Y.items():
    results[subject] = {}

    for block in range(BLOCKS):
        block_x = ANCHOR_X + BLOCK_X_OFFSETS[block]

        for q in range(QUESTIONS_PER_BLOCK):
            qnum = block * QUESTIONS_PER_BLOCK + q + 1
            if qnum > 40:
                continue

            cy = anchor_y + q * ROW_GAP
            scores = {}

            for c in range(CHOICES):
                cx = block_x + CHOICE_X_OFFSETS[c]

                x1 = int(cx - PILL_W // 2) + INNER_PAD_X
                y1 = int(cy - PILL_H // 2) + INNER_PAD_Y
                x2 = int(cx + PILL_W // 2) - INNER_PAD_X
                y2 = int(cy + PILL_H // 2) - INNER_PAD_Y

                debug_tag = f"{subject}_Q{qnum}_{CHOICE_LABELS[c]}"
                weighted, max_area = fill_ratio(thresh, x1, y1, x2, y2, debug_tag)
                page_max_scores.setdefault(subject, []).append(max_area)
                scores[CHOICE_LABELS[c]] = {
                    "weighted": weighted,
                    "max": max_area
                }

subject_min_ink = {}

if AUTO_CALIBRATE_MIN_INK:
    for subj, values in page_max_scores.items():
        nonzero = [v for v in values if v > 0]
        if len(nonzero) > 5:
            dynamic_min = np.percentile(nonzero, CALIBRATION_PERCENTILE)
            subject_min_ink[subj] = max(dynamic_min, GLOBAL_MIN_INK_FLOOR)
        else:
            subject_min_ink[subj] = GLOBAL_MIN_INK_FLOOR

        print(
            f"[AUTO-CAL] {subj} MIN_INK_RATIO={subject_min_ink[subj]:.4f} "
            f"(samples={len(nonzero)})"
        )

for subject, anchor_y in SUBJECT_Y.items():
    for block in range(BLOCKS):
        block_x = ANCHOR_X + BLOCK_X_OFFSETS[block]

        for q in range(QUESTIONS_PER_BLOCK):
            qnum = block * QUESTIONS_PER_BLOCK + q + 1
            if qnum > 40:
                continue

            cy = anchor_y + q * ROW_GAP
            scores = {}

            for c in range(CHOICES):
                cx = block_x + CHOICE_X_OFFSETS[c]

                x1 = int(cx - PILL_W // 2) + INNER_PAD_X
                y1 = int(cy - PILL_H // 2) + INNER_PAD_Y
                x2 = int(cx + PILL_W // 2) - INNER_PAD_X
                y2 = int(cy + PILL_H // 2) - INNER_PAD_Y

                debug_tag = f"{subject}_Q{qnum}_{CHOICE_LABELS[c]}"
                weighted, max_area = fill_ratio(thresh, x1, y1, x2, y2, debug_tag)
                scores[CHOICE_LABELS[c]] = {
                    "weighted": weighted,
                    "max": max_area
                }

            # Use max-area first (strong pencil mark), fallback to weighted
            by_max = sorted(scores.items(), key=lambda x: x[1]["max"], reverse=True)
            (best_c, best_v), (_, second_v) = by_max[:2]

            best_max = best_v["max"]
            second_max = second_v["max"]

            confidence = round(best_max - second_max, 3)

            min_ink = subject_min_ink.get(subject, MIN_INK_RATIO)
            if best_max < min_ink:
                answer = None
                status = "BLANK"

            elif best_max < (second_max * 1.15):
                answer = "MULTIPLE"
                status = "REVIEW"

            else:
                answer = best_c
                status = "OK"

            print(f"[Q{qnum}] {subject} best={best_c} best_max={best_max:.3f} second={second_max:.3f} min={min_ink:.3f}")

            results[subject][qnum] = {
                "answer": answer,
                "status": status,
                "confidence": confidence,
                "min_ink": min_ink,
                "scores": {k: v for k, v in scores.items()}
            }

# ================= OUTPUT =================
# Write full results to file to avoid terminal truncation
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

# Also emit to stdout for quick inspection
print(json.dumps(results, indent=2))

# Open results on macOS
if os.name == "posix":
    os.system("open results.json")