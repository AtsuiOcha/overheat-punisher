import os
import cv2
from src.detection import hud_detection

# asset base path
BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'assets')

# test detect kill feed when kill feed contains valid events
def test_detect_kill_feed1():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'bind2.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    kill_feed = hud_detection.detect_kill_feed(frame)

    # ASSERTIONS
    assert kill_feed is not None
    assert len(kill_feed) == 2
    assert kill_feed[0] == ('zlabobabil', 'Iso')
    assert kill_feed[1] == ('igneous rock fan', 'zlabobabil')
