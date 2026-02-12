import cv2
import numpy as np

IMAGE_PATH = "template/template.png"

# ----- CONFIG -----
VIEWPORT_WIDTH = 1200
VIEWPORT_HEIGHT = 900
SCROLL_STEP = 200
ZOOM_STEP = 0.1
MIN_ZOOM = 0.2
MAX_ZOOM = 3.0
# -------------------

class CoordinatePicker:
    def __init__(self, image_path):
        self.original = cv2.imread(image_path)
        if self.original is None:
            raise Exception("Image not found")

        self.zoom = 1.0
        self.scroll_y = 0
        self.scroll_x = 0

        self.points = []  # store selected points

        cv2.namedWindow("Picker", cv2.WINDOW_NORMAL)
        cv2.resizeWindow("Picker", VIEWPORT_WIDTH, VIEWPORT_HEIGHT)
        cv2.setMouseCallback("Picker", self.mouse_callback)

    def get_scaled_image(self):
        h, w = self.original.shape[:2]
        new_w = int(w * self.zoom)
        new_h = int(h * self.zoom)
        return cv2.resize(self.original, (new_w, new_h))

    def mouse_callback(self, event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            # Convert viewport coordinates to original image coordinates
            actual_x = int((x + self.scroll_x) / self.zoom)
            actual_y = int((y + self.scroll_y) / self.zoom)

            self.points.append((actual_x, actual_y))
            print(f"Clicked: {actual_x}, {actual_y}")

    def draw_points(self, frame):
        for (px, py) in self.points:
            sx = int(px * self.zoom) - self.scroll_x
            sy = int(py * self.zoom) - self.scroll_y
            cv2.circle(frame, (sx, sy), 8, (0, 0, 255), 2)
        return frame

    def run(self):
        while True:
            scaled = self.get_scaled_image()
            h, w = scaled.shape[:2]

            # Ensure scroll bounds
            self.scroll_y = max(0, min(self.scroll_y, h - VIEWPORT_HEIGHT))
            self.scroll_x = max(0, min(self.scroll_x, w - VIEWPORT_WIDTH))

            frame = scaled[
                self.scroll_y:self.scroll_y + VIEWPORT_HEIGHT,
                self.scroll_x:self.scroll_x + VIEWPORT_WIDTH
            ].copy()

            frame = self.draw_points(frame)

            cv2.imshow("Picker", frame)

            key = cv2.waitKey(30)

            if key == 27:  # ESC
                break
            elif key == ord('w'):  # scroll up
                self.scroll_y -= SCROLL_STEP
            elif key == ord('s'):  # scroll down
                self.scroll_y += SCROLL_STEP
            elif key == ord('a'):  # scroll left
                self.scroll_x -= SCROLL_STEP
            elif key == ord('d'):  # scroll right
                self.scroll_x += SCROLL_STEP
            elif key == ord('+') or key == ord('='):  # zoom in
                self.zoom = min(MAX_ZOOM, self.zoom + ZOOM_STEP)
            elif key == ord('-'):  # zoom out
                self.zoom = max(MIN_ZOOM, self.zoom - ZOOM_STEP)
            elif key == ord('c'):  # clear points
                self.points = []
                print("Cleared points")

        cv2.destroyAllWindows()

        print("\nFinal coordinates:")
        for p in self.points:
            print(p)


if __name__ == "__main__":
    picker = CoordinatePicker(IMAGE_PATH)
    picker.run()