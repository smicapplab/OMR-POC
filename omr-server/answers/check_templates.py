import cv2

img1 = cv2.imread("template/page1_identity.png")
img2 = cv2.imread("template/page2_answers.png")

if img1 is None:
    raise RuntimeError("page1_identity.png not found or unreadable")

if img2 is None:
    raise RuntimeError("page2_answers.png not found or unreadable")

print("Page 1 shape:", img1.shape)
print("Page 2 shape:", img2.shape)