import cv2
import numpy as np
import os

# ============================================================
# Canonical page & geometry constants (SINGLE SOURCE OF TRUTH)
# ============================================================

FILE = "gilvert-2.png"

CANON_W = 2550
CANON_H = 3500

# ---- Horizontal geometry ----
ANCHOR_X = 733  # Math Q1, Choice A center X (canonical)
CHOICE_X_OFFSETS = [0, 48, 97, 145]   # A, B, C, D
BLOCK_X_OFFSETS = [0, 341, 681, 1025, 1364] # 1, 9, 17, 25, 33

# ---- Pill (answer bubble) geometry ----
PILL_W = 30
PILL_H = 28

# ---- Question / block layout ----
QUESTIONS_PER_BLOCK = 8
BLOCKS = 5
CHOICES = 4

# ---- Vertical row geometry ----
ROW_GAP = 49                  # measured Q1→Q2 distance
ROW_ADJUST = [0, 0, 0, 0, 0, 0, 0, 0]   # per-row micro adjustment (Math)

# ---- Subject anchors (Q1 A center Y) ----
SUBJECT_Y = {
    "math": 837,
    "english": 1274,
    "science": 1712,
    "filipino": 2146,
    "ap": 2586
}


img = cv2.imread("template/" + FILE )
if img is None:
    raise RuntimeError("Failed to load template/" + FILE )

def normalize_page(image, out_w=2550, out_h=3500):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

    # Edge detection works better than color for page boundary
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    edges = cv2.Canny(blur, 50, 150)

    contours, _ = cv2.findContours(edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
    if not contours:
        return cv2.resize(image, (out_w, out_h))

    # Largest contour assumed to be the page
    page_contour = max(contours, key=cv2.contourArea)

    peri = cv2.arcLength(page_contour, True)
    approx = cv2.approxPolyDP(page_contour, 0.02 * peri, True)

    if len(approx) != 4:
        # Fallback: force resize to canonical size
        return cv2.resize(image, (out_w, out_h))

    pts = approx.reshape(4, 2)

    # Order points: top-left, top-right, bottom-right, bottom-left
    rect = np.zeros((4, 2), dtype="float32")
    s = pts.sum(axis=1)
    diff = np.diff(pts, axis=1)

    rect[0] = pts[np.argmin(s)]
    rect[2] = pts[np.argmax(s)]
    rect[1] = pts[np.argmin(diff)]
    rect[3] = pts[np.argmax(diff)]

    dst = np.array([
        [0, 0],
        [out_w - 1, 0],
        [out_w - 1, out_h - 1],
        [0, out_h - 1]
    ], dtype="float32")

    M = cv2.getPerspectiveTransform(rect, dst)
    warped = cv2.warpPerspective(image, M, (out_w, out_h))
    return warped

# ================= DESKEW (ROTATION ONLY) =================
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    thresh = cv2.adaptiveThreshold(
        blur,
        255,
        cv2.ADAPTIVE_THRESH_MEAN_C,
        cv2.THRESH_BINARY_INV,
        31,
        10
    )

    coords = np.column_stack(np.where(thresh > 0))
    if coords.size == 0:
        return image

    angle = cv2.minAreaRect(coords)[-1]
    if angle < -45:
        angle = -(90 + angle)
    else:
        angle = -angle

    (h, w) = image.shape[:2]
    center = (w // 2, h // 2)
    M = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated = cv2.warpAffine(image, M, (w, h), flags=cv2.INTER_CUBIC, borderMode=cv2.BORDER_REPLICATE)
    return rotated

# Normalize page (perspective) then deskew (rotation)
img = normalize_page(img)
img = deskew(img)

def draw_subject(img, anchor_y):
    for block in range(BLOCKS):
        block_x = ANCHOR_X + BLOCK_X_OFFSETS[block]

        for q in range(QUESTIONS_PER_BLOCK):
            question_number = block * QUESTIONS_PER_BLOCK + q + 1
            if question_number > 40:
                continue

            adj = ROW_ADJUST[q] if q < len(ROW_ADJUST) else 0
            cy = anchor_y + q * ROW_GAP + adj

            for c in range(CHOICES):
                cx = block_x + CHOICE_X_OFFSETS[c]

                if c == 0:
                    cv2.putText(
                        img,
                        str(question_number),
                        (int(cx - 45), int(cy + 5)),
                        cv2.FONT_HERSHEY_SIMPLEX,
                        0.35,
                        (255, 0, 255),
                        1,
                        cv2.LINE_AA
                    )

                pw = PILL_W
                ph = PILL_H
                x1 = int(cx - pw // 2)
                y1 = int(cy - ph // 2)
                x2 = int(cx + pw // 2)
                y2 = int(cy + ph // 2)

                # ROI rectangle
                cv2.rectangle(img, (x1, y1), (x2, y2), (0, 255, 0), 1)

                # Pill center
                cv2.circle(img, (int(cx), int(cy)), 2, (0, 0, 255), -1)

                # Row baseline (helps detect vertical drift)
                if c == 0:
                    cv2.line(
                        img,
                        (int(cx - 20), int(cy)),
                        (int(cx + 20), int(cy)),
                        (255, 0, 0),
                        1
                    )

for _, anchor_y in SUBJECT_Y.items():
    draw_subject(img, anchor_y)

output_path = "overlay_debug.png"
cv2.imwrite(output_path, img)
print(f"Overlay image written to {output_path}")

# Force open on macOS for reliable viewing
try:
    os.system(f"open {output_path}")
except Exception:
    pass