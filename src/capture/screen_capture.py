import cv2
import mss
import numpy as np
from cv2.typing import MatLike
from loguru import logger


def capture_screen() -> MatLike:
    """Captures a single frame from the primary monitor.

    Uses MSS to grab a screenshot from the primary monitor and converts it
    from BGRA to BGR format for OpenCV compatibility.

    Returns:
        MatLike: Screenshot frame in BGR format as numpy array.

    Raises:
        Exception: If screen capture fails or monitor is not accessible.

    Example:
        >>> frame = capture_screen()
        >>> print(f"Frame shape: {frame.shape}")
        Frame shape: (1440, 2560, 3)
    """
    with mss.mss() as sct:
        monitor = sct.monitors[1]
        screenshot = sct.grab(
            monitor
        )  # implemented using C/C++ so only accepts positional arguments

        return cv2.cvtColor(src=np.array(screenshot), code=cv2.COLOR_BGRA2BGR)


def show_screen_capture() -> None:
    """Continuously captures and displays the screen until '~' is pressed.

    Creates a live preview window showing real-time screen capture.
    Useful for testing capture functionality and positioning detection regions.
    The window will close when the '~' key is pressed.

    Raises:
        Exception: If screen capture or window display fails.

    Example:
        >>> show_screen_capture()  # Opens live preview window
        # Press '~' to exit
    """
    window_name = "Screen Capture"
    try:
        while True:
            logger.info("Starting screen capture loop...")
            frame = capture_screen()

            # Display the frame in a window
            cv2.imshow(winname="Screen Capture", mat=frame)

            # exit on '~' key press for "leave"
            if cv2.waitKey(delay=1) & 0xFF == ord("~"):
                logger.info("Exit key pressed. Stopping capture.")
                break

        # release resources
        cv2.destroyAllWindows()
    except Exception as cv2_err:
        logger.error(f"Unexpected error in show_screen_capture {cv2_err}")
