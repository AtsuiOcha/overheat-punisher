"""
Screen capture module for real-time gameplay monitoring.

This module provides functionality to capture screenshots from the primary monitor
for Valorant gameplay analysis. Uses MSS (Multiple Screenshot System) for fast,
cross-platform screen capture with OpenCV for image processing.
"""

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
        logger.info("Starting screen capture. Press '~' to exit...")

        while True:
            frame = capture_screen()

            # Display the frame in a window
            cv2.imshow(winname=window_name, mat=frame)

            # Check for key press - increased delay helps with responsiveness
            key = cv2.waitKey(delay=30) & 0xFF

            # exit on '~' key press
            if key == ord("~"):
                logger.info("Exit key pressed. Stopping capture.")
                break

            # Check if window was closed by user clicking X
            if (
                cv2.getWindowProperty(winname=window_name, prop_id=cv2.WND_PROP_VISIBLE)
                < 1
            ):
                logger.info("Window closed by user. Stopping capture.")
                break

    except KeyboardInterrupt:
        logger.info("Interrupted by user")
    except Exception as cv2_err:
        logger.error(f"Unexpected error in show_screen_capture {cv2_err}")
    finally:
        # More aggressive cleanup for macOS
        try:
            cv2.destroyWindow(winname=window_name)
            cv2.destroyAllWindows()
            # Force window system to update
            for i in range(4):
                cv2.waitKey(delay=1)
        except Exception:
            pass  # Ignore cleanup errors
        logger.info("Screen capture stopped and resources cleaned up")
