import cv2
import numpy as np
import random

OUTPUT_PATH = "pencil_pill_test.png"


def generate_pill_texture_layer(height, width, cx, cy, pill_rx, pill_ry, return_image=False):
    """
    Unified graphite engine.

    If return_image=False:
        Returns float32 graphite strength layer (0–1.8).
    If return_image=True:
        Returns full uint8 rendered image (standalone test use).
    """

    stroke_layer = np.zeros((height, width), dtype=np.float32)

    stroke_total = random.randint(160, 260)

    for _ in range(stroke_total):
        angle = random.uniform(-60, 60)
        rad = np.radians(angle)

        length = random.uniform(pill_rx * 0.6, pill_rx * 1.6)
        thickness = random.randint(1, 3)
        offset_y = random.uniform(-pill_ry, pill_ry)

        x0 = int(cx - np.cos(rad) * length / 2)
        y0 = int(cy + offset_y - np.sin(rad) * length / 2)
        x1 = int(cx + np.cos(rad) * length / 2)
        y1 = int(cy + offset_y + np.sin(rad) * length / 2)

        temp = np.zeros_like(stroke_layer)
        cv2.line(temp, (x0, y0), (x1, y1), 1.0, thickness)

        blur_strength = random.uniform(0.6, 1.4)
        temp = cv2.GaussianBlur(temp, (0, 0), blur_strength)

        intensity = random.uniform(0.5, 1.3)
        stroke_layer += temp * intensity

    # Ellipse mask
    yg, xg = np.mgrid[0:height, 0:width]
    d = ((xg - cx) / pill_rx) ** 2 + ((yg - cy) / pill_ry) ** 2

    mask = np.clip(1.1 - d, 0, 1)
    mask = cv2.GaussianBlur(mask.astype(np.float32), (0, 0), 1.4)

    edge_noise = np.random.normal(0, 0.12, (height, width)).astype(np.float32)
    edge_noise = cv2.GaussianBlur(edge_noise, (0, 0), 1.2)
    mask *= (1.0 + edge_noise)
    mask = np.clip(mask, 0, 1)

    stroke_layer *= mask

    # Graphite grain
    grain = np.random.normal(0, 0.06, (height, width)).astype(np.float32)
    grain = cv2.GaussianBlur(grain, (0, 0), 0.7)
    stroke_layer *= (1.0 + grain)

    stroke_layer = np.clip(stroke_layer, 0, 1.8)

    if return_image:
        graphite = 255 - (stroke_layer * 170)
        graphite = np.clip(graphite, 35, 255).astype(np.uint8)
        return cv2.merge([graphite, graphite, graphite])

    return stroke_layer

if __name__ == "__main__":
    width = 220
    height = 140

    pill = generate_pill_texture_layer(
        height,
        width,
        width // 2,
        height // 2,
        width * 0.28,
        height * 0.22,
        return_image=True
    )

    cv2.imwrite(OUTPUT_PATH, pill)
    print(f"Saved simulated pill shade to {OUTPUT_PATH}")