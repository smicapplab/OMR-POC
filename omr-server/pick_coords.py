import cv2
import numpy as np

FILE = "gilvert-2.png"   # raw scan (5096×7000)
CANON_W = 2550
CANON_H = 3500

# -------------------------
# Normalization (SIMPLE + SAFE)
# -------------------------
def normalize_page(image, out_w=2550, out_h=3500):
    """
    For coordinate picking:
    - We do NOT need contour detection
    - We force resize to canonical size
    """
    return cv2.resize(image, (out_w, out_h), interpolation=cv2.INTER_AREA)

# -------------------------
# Deskew (rotation only)
# -------------------------
def deskew(image):
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    blur = cv2.GaussianBlur(gray, (5, 5), 0)
    _, thresh = cv2.threshold(
        blur, 0, 255, cv2.THRESH_BINARY_INV + cv2.THRESH_OTSU
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
    M = cv2.getRotationMatrix2D((w // 2, h // 2), angle, 1.0)
    return cv2.warpAffine(
        image, M, (w, h),
        flags=cv2.INTER_CUBIC,
        borderMode=cv2.BORDER_REPLICATE
    )

# -------------------------
# Mouse callback
# -------------------------
def click_event(event, x, y, flags, param):
    if event == cv2.EVENT_LBUTTONDOWN:
        print(f"x={x}, y={y}")
        cv2.circle(img, (x, y), 4, (0, 0, 255), -1)
        cv2.imshow("CANONICAL_PICK", img)

# -------------------------
# Load → normalize → deskew
# -------------------------
raw = cv2.imread("template/" + FILE)
if raw is None:
    raise RuntimeError("Failed to load image")

img = normalize_page(raw, CANON_W, CANON_H)
img = deskew(img)

print("Image shape (must be 2550×3500):", img.shape)

cv2.imshow("CANONICAL_PICK", img)
cv2.setMouseCallback("CANONICAL_PICK", click_event)
cv2.waitKey(0)
cv2.destroyAllWindows()