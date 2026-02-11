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
DEBUG_DIR = "debug_pills"

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

# ================= IMAGE LOAD =================
img = cv2.imread("template/" + FILE)
if img is None:
    raise RuntimeError("Failed to load template/" + FILE)

# ================= DESKEW =================
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    _, dark = cv2.threshold(gray, 180, 255, cv2.THRESH_BINARY_INV)
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    dark = cv2.morphologyEx(dark, cv2.MORPH_CLOSE, kernel)
    coords = np.column_stack(np.where(dark > 0))
    if coords.size < 1000:
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

# ================= ORANGE SUPPRESSION =================
def suppress_orange(image):
    """Replace orange printed text/borders with white before thresholding."""
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    lower_orange = np.array([3,  80, 100])
    upper_orange = np.array([20, 255, 255])
    mask = cv2.inRange(hsv, lower_orange, upper_orange)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.dilate(mask, kernel, iterations=1)
    result = image.copy()
    result[mask > 0] = [255, 255, 255]
    return result

# ================= ADAPTIVE THRESHOLD =================
img_clean = suppress_orange(img)
gray = cv2.cvtColor(img_clean, cv2.COLOR_BGR2GRAY)
thresh = cv2.adaptiveThreshold(
    gray, 255,
    cv2.ADAPTIVE_THRESH_GAUSSIAN_C,
    cv2.THRESH_BINARY_INV,
    15, 8
)
kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (2, 2))
thresh = cv2.morphologyEx(thresh, cv2.MORPH_CLOSE, kernel)

# ================= FILL RATIO =================
BORDER_PAD   = 3
LETTER_STRIP = 0.30

def fill_ratio(thresh_img, cx, cy, debug_tag=None):
    h_img, w_img = thresh_img.shape
    x1 = max(int(cx - PILL_W // 2) + BORDER_PAD, 0)
    y1 = max(int(cy - PILL_H // 2) + BORDER_PAD, 0)
    x2 = min(int(cx + PILL_W // 2) - BORDER_PAD, w_img - 1)
    y2 = min(int(cy + PILL_H // 2) - BORDER_PAD, h_img - 1)
    roi = thresh_img[y1:y2, x1:x2]
    if roi.size == 0:
        return 0.0
    rh, rw = roi.shape
    letter_cols = int(rw * LETTER_STRIP)
    roi_clean = roi[:, letter_cols:]
    if roi_clean.size == 0:
        return 0.0
    ratio = round(cv2.countNonZero(roi_clean) / roi_clean.size, 4)
    if DEBUG_PILL_DUMP and debug_tag:
        pad = np.zeros((rh, 4), dtype=np.uint8)
        combined = np.hstack([roi, pad, roi_clean])
        cv2.imwrite(f"{DEBUG_DIR}/{debug_tag}.png", combined)
    return ratio

# ================= GEOMETRY DIAGNOSTICS =================
# Print row cy values per subject so you can cross-check against overlay_debug.png.
# NOISE on Q6-8 of math  = those cy values land on English section header.
# NOISE on Q1-N of other subjects = anchor_y is too high, landing on prev section.
# Fix: adjust SUBJECT_Y values in overlay_test.py until NOISE questions disappear.
print("\n[GEOMETRY] Row center-Y values (cy) per subject:")
for subject, anchor_y in SUBJECT_Y.items():
    cys = [anchor_y + q * ROW_GAP for q in range(QUESTIONS_PER_BLOCK)]
    print(f"  {subject:12s} anchor={anchor_y}  Q1-Q8 cy: {cys}")
print()

# ================= SINGLE PASS =================
pill_scores = {}
raw_ratios  = {subj: [] for subj in SUBJECT_Y}

for subject, anchor_y in SUBJECT_Y.items():
    for block in range(BLOCKS):
        block_x = ANCHOR_X + BLOCK_X_OFFSETS[block]
        for q in range(QUESTIONS_PER_BLOCK):
            qnum = block * QUESTIONS_PER_BLOCK + q + 1
            if qnum > 40:
                continue
            cy = anchor_y + q * ROW_GAP
            for c in range(CHOICES):
                cx = block_x + CHOICE_X_OFFSETS[c]
                debug_tag = f"{subject}_Q{qnum:02d}_{CHOICE_LABELS[c]}"
                ratio = fill_ratio(thresh, cx, cy, debug_tag)
                pill_scores[(subject, qnum, CHOICE_LABELS[c])] = ratio
                raw_ratios[subject].append(ratio)

# ================= CALIBRATE =================
GLOBAL_MIN_INK_FLOOR   = 0.04
CALIBRATION_PERCENTILE = 20

subject_min_ink = {}
for subj, ratios in raw_ratios.items():
    # Exclude NOISE rows from calibration (values > 0.15 are likely printed content)
    valid = [r for r in ratios if 0 < r < 0.15]
    if len(valid) > 5:
        dynamic = np.percentile(valid, CALIBRATION_PERCENTILE)
        subject_min_ink[subj] = max(dynamic, GLOBAL_MIN_INK_FLOOR)
    else:
        subject_min_ink[subj] = GLOBAL_MIN_INK_FLOOR
    print(f"[AUTO-CAL] {subj:12s}  min_ink={subject_min_ink[subj]:.4f}  valid_samples={len(valid)}")

# ================= SCORE =================
# BLANK    : best < min_ink
# NOISE    : all 4 choices uniformly high (ROI reading printed content)
# OK       : clear dominant winner — ratio >= 1.6 AND gap >= 0.03
# REVIEW   : two choices both genuinely marked, or borderline

DOMINANCE_RATIO = 1.5   # winner must be 1.5x runner-up  [tuned: resolves 30 more vs ratio=2.0]
MIN_GAP         = 0.04  # absolute gap must be >= 4pp    [tuned: filters noise, allows faint marks]
UNIFORM_FACTOR  = 3.0   # all 4 above min_ink*this = noise

results = {}

for subject, anchor_y in SUBJECT_Y.items():
    results[subject] = {}
    min_ink = subject_min_ink[subject]

    for block in range(BLOCKS):
        for q in range(QUESTIONS_PER_BLOCK):
            qnum = block * QUESTIONS_PER_BLOCK + q + 1
            if qnum > 40:
                continue

            scores = {
                label: pill_scores[(subject, qnum, label)]
                for label in CHOICE_LABELS
            }

            sorted_scores = sorted(scores.items(), key=lambda x: x[1], reverse=True)
            best_c, best_v   = sorted_scores[0]
            _,      second_v = sorted_scores[1]
            min_v            = sorted_scores[3][1]

            confidence = round(best_v - second_v, 4)
            uniform_noise = (min_v > min_ink * UNIFORM_FACTOR)

            if uniform_noise and best_v >= min_ink:
                answer = None
                status = "NOISE"
            elif best_v < min_ink:
                answer = None
                status = "BLANK"
            elif best_v >= second_v * DOMINANCE_RATIO and confidence >= MIN_GAP:
                answer = best_c
                status = "OK"
            else:
                answer = "MULTIPLE"
                status = "REVIEW"

            print(
                f"[{subject:12s} Q{qnum:02d}]  "
                f"best={best_c}({best_v:.4f})  "
                f"2nd={second_v:.4f}  "
                f"min4={min_v:.4f}  "
                f"conf={confidence:.4f}  "
                f"noise={uniform_noise}  → {status}"
            )

            results[subject][qnum] = {
                "answer":     answer,
                "status":     status,
                "confidence": confidence,
                "scores":     scores,
            }

# ================= SUMMARY =================
print("\n[SUMMARY]")
for subject in results:
    counts = {"OK": 0, "BLANK": 0, "REVIEW": 0, "NOISE": 0}
    for v in results[subject].values():
        counts[v["status"]] = counts.get(v["status"], 0) + 1
    print(f"  {subject:12s}  OK={counts['OK']:2d}  BLANK={counts['BLANK']:2d}  "
          f"REVIEW={counts['REVIEW']:2d}  NOISE={counts['NOISE']:2d}")
print()
print("[ACTION REQUIRED]")
print("  NOISE  → fix SUBJECT_Y anchors in overlay_test.py")
print("  REVIEW → check debug_pills/ images for those question numbers")

# ================= OUTPUT =================
with open("results.json", "w") as f:
    json.dump(results, f, indent=2)

print("\nDone. Results written to results.json")

if os.name == "posix":
    os.system("open results.json")