import cv2
import logging
import mss
import numpy as np

# Check if a root logger is already configured
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

# Create a logger for this specific module
logger = logging.getLogger(__name__)

def capture_screen():
    """Captures a single frame from the primary monitor"""
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(monitor)

        # convert the image to a numpy array in OpenCV BGR format
        frame = np.array(screenshot)
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

        return frame

def show_screen_capture():
    """Continuously captures and displays the screen until '~' is pressed."""
    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while True:
            frame = capture_screen()

            # Display the frame in a window
            cv2.imshow('Screen Capture', frame)

            # exit on '~' key press for "leave"
            if cv2.waitKey(1) & 0xFF == ord('~'):
                break

        # release resources
        cv2.destroyAllWindows()