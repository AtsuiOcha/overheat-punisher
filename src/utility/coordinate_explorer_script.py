"""
Coordinate exploration utility for HUD region identification.

This interactive utility helps developers identify pixel coordinates for region
of interest (ROI) definitions used in HUD detection. Click on the displayed
screenshot to get coordinate information for defining detection regions.
"""

from importlib.resources import files

import cv2
import numpy as np

from src.assets import game_scenarios

# Global variables
start_x, start_y = None, None


def get_coords(event: int, x: int, y: int, _flags: int, _param: object) -> None:
    """Mouse callback function to capture click coordinates.
    
    Handles left mouse button clicks to record and print x, y coordinates.
    Used for identifying regions of interest in Valorant screenshots.
    
    Args:
        event (int): OpenCV mouse event type.
        x (int): X-coordinate of mouse click.
        y (int): Y-coordinate of mouse click.
        _flags (int): Additional flags (unused).
        _param (object): User data (unused).
        
    Note:
        Updates global variables start_x and start_y when left button is clicked.
    """
    global start_x, start_y
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
        print(f"Coords: ({start_x}, {start_y})")


def main() -> None:
    """Main function to run the coordinate explorer.
    
    Loads a test screenshot and displays it in an interactive window.
    Users can click anywhere on the image to get coordinates printed
    to the console. Useful for defining detection regions.
    
    Example:
        >>> main()  # Opens window with test screenshot
        # Click anywhere to see coordinates
        Coords: (1420, 90)  # Example output
    """
    # Load image from package resources
    resource = files(game_scenarios).joinpath("kill_feed_death.png")

    with resource.open("rb") as f:
        image = cv2.imdecode(
            buf=np.frombuffer(f.read(), np.uint8), flags=cv2.IMREAD_COLOR
        )

    # Setup window
    cv2.namedWindow("Screenshot")
    cv2.setMouseCallback("Screenshot", get_coords)
    cv2.imshow("Screenshot", image)
    _ = cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()
