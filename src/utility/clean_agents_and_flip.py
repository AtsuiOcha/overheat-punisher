import cv2
import os

def process_and_mirror_images(input_folder, output_folder):
    for filename in os.listdir(input_folder):
        if filename.endswith(".webp"):
            filepath = os.path.join(input_folder, filename)

            # Read and convert to grayscale
            img = cv2.imread(filepath, cv2.IMREAD_UNCHANGED)

            if img.shape[2] == 4:
                # split the image into BGR and alpha channels
                bgr = img[:, :, :3]
                alpha = img[:, :, 3]
                gray_bgr = cv2.cvtColor(bgr, cv2.COLOR_BGR2GRAY)
                gray_img = cv2.merge([gray_bgr, gray_bgr, gray_bgr, alpha])
            else:
                gray_img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # resize to (40 x 40 px) how big they show up on screen
            resized_gray_img = cv2.resize(gray_img, (40, 40), interpolation=cv2.INTER_AREA)

            # convert to png format
            png_filename = filename.replace('.webp', '.png')

            # Save the resized grayscale image as png
            cleaned_filepath = os.path.join(output_folder, png_filename)
            cv2.imwrite(cleaned_filepath, resized_gray_img)

            # Mirror the cleaned image along the Y-axis
            mirrored_img = cv2.flip(resized_gray_img, 1)

            # Save the mirrored image
            mirrored_filename = f"Mirrored_{png_filename}"
            mirrored_filepath = os.path.join(output_folder, mirrored_filename)
            cv2.imwrite(mirrored_filepath, mirrored_img)

            # Remove the original input image
            os.remove(filepath)

# Define your input and output paths
input_folder = "../assets/agent_icons"
output_folder = "../assets/agent_icons_clean"

process_and_mirror_images(input_folder, output_folder)