from importlib.resources import files
from pprint import pprint

import cv2
import numpy as np
import pytest

from src.assets import game_scenarios
from src.detection import hud_detection


# test detect kill feed when kill feed contains valid events
@pytest.mark.unit
def test_kill_feed_detection() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("kill_feed_death.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    kill_feed = hud_detection.detect_kill_feed(frame)
    pprint(kill_feed)

    # ASSERTIONS
    assert kill_feed is not None
    assert len(kill_feed) == 2
    assert kill_feed[0]["killer"] == "zlabobabil"
    assert kill_feed[0]["victim"] == "Iso"
    assert not kill_feed[0]["was_team_death"]
    assert kill_feed[1]["killer"] == "igneous rock fan"
    assert kill_feed[1]["victim"] == "zlabobabil"
    assert kill_feed[1]["was_team_death"]


# test check killed by exists positive test
@pytest.mark.unit
def test_check_killed_by_pos() -> None:
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
def test_check_killed_by_neg() -> None:
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
# test detect scores
def test_detect_round_info() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("mid_round.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)

    scores = hud_detection.detect_scores(frame)
    assert scores.team1 == 8
    assert scores.team2 == 6


@pytest.mark.unit
# test team agent detection with deaths
def test_agent_detection_with_deaths() -> None:
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
def test_agent_detection_no_deaths() -> None:
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


@pytest.mark.skip
def test_detect_round_state_buy_phase() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("pre_round_buy_phase.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)
    ret = hud_detection.detect_round_state(frame)
    assert ret == hud_detection.RoundState.PRE_ROUND


@pytest.mark.skip
def test_detect_round_state_post_round_loss() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("post_round_loss.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)
    ret = hud_detection.detect_round_state(frame)
    assert ret == hud_detection.RoundState.POST_ROUND


@pytest.mark.skip
def test_detect_round_state_post_round_won() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("post_round_win.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)
    ret = hud_detection.detect_round_state(frame)
    assert ret == hud_detection.RoundState.POST_ROUND


@pytest.mark.skip
def test_detect_round_state_post_round_ace() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("post_round_ace_won.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)
    ret = hud_detection.detect_round_state(frame)
    assert ret == hud_detection.RoundState.POST_ROUND


@pytest.mark.skip
def test_detect_round_state_mid_round() -> None:
    # load test image from assets folder
    test_img = files(game_scenarios).joinpath("mid_round.png")

    with test_img.open("rb") as img_file:
        frame = cv2.imdecode(
            np.frombuffer(img_file.read(), np.uint8), cv2.IMREAD_UNCHANGED
        )

    if frame.shape[2] == 4:
        frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGRA2BGR)
    ret = hud_detection.detect_round_state(frame)
    assert ret == hud_detection.RoundState.MID_ROUND
