from importlib.resources import files

import cv2
import numpy as np
import pytest

from src.assets import game_scenarios
from src.detection import hud_detection


# test detect kill feed when kill feed contains valid events
@pytest.mark.unit
def test_detect_kill_feed1() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("kill_feed_death.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    kill_feed = hud_detection.detect_kill_feed(frame)

    # ASSERTIONS
    assert kill_feed is not None
    assert len(kill_feed) == 2
    assert kill_feed[0] == ("zlabobabil", "Iso")
    assert kill_feed[1] == ("igneous rock fan", "zlabobabil")


# test check killed by exists positive test
@pytest.mark.unit
def test_check_killed_by_pos():
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("kill_feed_death.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    assert hud_detection.is_player_dead(frame)


@pytest.mark.unit
# test check killed by exists negative test
def test_check_killed_by_neg():
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("mid_round.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    assert not hud_detection.is_player_dead(frame)


@pytest.mark.unit
# test round info detection
def test_detect_round_info():
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("mid_round.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    round_info = hud_detection.detect_round_info(frame)

    # assert round_info = (cur_round, round_time_sec, score)
    assert round_info, "round_info returned None"
    assert len(round_info) == 3
    assert round_info[0] == 15
    assert round_info[1] == 95
    assert round_info[2] == "8 - 6"


@pytest.mark.unit
# test team agent detection with deaths
def test_agent_detection_with_deaths():
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("kill_feed_death.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    ret = hud_detection.detect_agent_icons(frame)

    assert ret[0] == ["cypher", "skye"]
    assert ret[1] == ["chamber", "clove", "raze", "skye"]
    assert len(ret[0]) == 2
    assert len(ret[1]) == 4


@pytest.mark.unit
# test team agent detection no deaths
def test_agent_detection_no_deaths():
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("mid_round.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    ret = hud_detection.detect_agent_icons(frame)

    assert ret[0] == sorted(["clove", "neon", "killjoy", "reyna", "jett"])
    assert ret[1] == sorted(["clove", "jett", "sova", "cypher", "reyna"])
    assert len(ret[0]) == 5
    assert len(ret[1]) == 5
