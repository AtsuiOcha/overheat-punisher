import os
import cv2
from src.detection import hud_detection

# asset base path
BASE_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), 'src', 'assets', 'game_scenarios')

# test detect kill feed when kill feed contains valid events
def test_detect_kill_feed1():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'kill_feed_death.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    kill_feed = hud_detection.detect_kill_feed(frame)

    # ASSERTIONS
    assert kill_feed is not None
    assert len(kill_feed) == 2
    assert kill_feed[0] == ('zlabobabil', 'Iso')
    assert kill_feed[1] == ('igneous rock fan', 'zlabobabil')

# test check killed by exists positive test
def test_check_killed_by_pos():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'kill_feed_death.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    res = hud_detection.is_player_dead(frame)
    assert res == True

# test check killed by exists negative test
def test_check_killed_by_neg():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'mid_round.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    res = hud_detection.is_player_dead(frame)
    assert res == False

# test round info detection
def test_detect_round_info():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'mid_round.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    round_info = hud_detection.detect_round_info(frame)

    # assert round_info = (cur_round, round_time_sec, score)
    assert len(round_info) == 3
    assert round_info[0] == 15
    assert round_info[1] == 95
    assert round_info[2] == '8 - 6'

# test team agent detection with deaths
def test_agent_detection_with_deaths():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'kill_feed_death.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    ret = hud_detection.detect_agent_icons(frame)

    assert ret[0] == ['cypher', 'skye']
    assert ret[1] == ['chamber', 'clove', 'raze', 'skye']
    assert len(ret[0]) == 2
    assert len(ret[1]) == 4

# test team agent detection no deaths
def test_agent_detection_no_deaths():
    # load test image from assets folder
    test_image_path = os.path.join(BASE_PATH, 'mid_round.png')

    frame = cv2.imread(test_image_path, cv2.IMREAD_UNCHANGED)

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

    ret = hud_detection.detect_agent_icons(frame)

    assert ret[0] == sorted(['clove', 'neon', 'killjoy', 'reyna', 'jett'])
    assert ret[1] == sorted(['clove', 'jett', 'sova', 'cypher', 'reyna'])
    assert len(ret[0]) == 5
    assert len(ret[1]) == 5
