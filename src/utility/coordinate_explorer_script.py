import cv2

# load image
image_path = "../assets/mid_round.png" # please change this asset path if you want to explore new image
image = cv2.imread(image_path)

# global variables
start_x, start_y = None, None

def get_coords(event, x, y, flags, param):
    global start_x, start_y
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
        print(f"Coords: ({start_x}, {start_y})")

cv2.namedWindow("Screenshot")
cv2.setMouseCallback("Screenshot", get_coords)

cv2.imshow("Screenshot",  image)
cv2.waitKey(0)
cv2.destroyAllWindows()