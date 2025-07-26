from importlib.resources import files
from typing import Any

import cv2
import numpy as np

from src.assets import game_scenarios

# Global variables
start_x, start_y = None, None


def get_coords(event: int, x: int, y: int, flags: int, param: Any) -> None:
    global start_x, start_y
    if event == cv2.EVENT_LBUTTONDOWN:
        start_x, start_y = x, y
        print(f"Coords: ({start_x}, {start_y})")


def main():
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
    cv2.waitKey(0)
    cv2.destroyAllWindows()


if __name__ == "__main__":
    main()

