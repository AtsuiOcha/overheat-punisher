from importlib.resources import files
from typing import Any, cast

import cv2
import easyocr
import numpy as np
from cv2.typing import MatLike
from loguru import logger

import src.assets.agent_icons_clean as icons

VARIANCE_THRESHOLD = 800
MATCH_THRESHOLD = 0.9
KILL_FEED_TRIGGER = "KILLED BY"


def detect_kill_feed(frame: MatLike) -> list[tuple[str, str]]:
    """detects kill feed events from the provided game frame"""
    # region of interest
    x1, y1 = 1420, 90  # top left
    x2, y2 = 1900, 400  # bottom right
    roi = frame[y1:y2, x1:x2]

    # OCR works better on grayscale
    gray_roi = cv2.cvtColor(src=roi, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(lang_list=["en"], gpu=False)

    # values are maybe it can help us split guns
    text_res = cast(list[str], reader.readtext(image=gray_roi, detail=0))

    # kill feed should have even length
    if len(text_res) % 2 != 0:
        text_res = text_res[:-1]

    # Group into tuples (killer, killed)
    kill_feed = [(text_res[i], text_res[i + 1]) for i in range(0, len(text_res), 2)]
    return kill_feed


def is_player_dead(frame: MatLike) -> bool:
    """detects if player is dead.

    Args:
        frame (MatLike) current frame capture of gameplay

    Returns:
        bool: True if player is dead, False otherwise
    """
    # region of interest
    x1, y1 = 1420, 220  # top left
    x2, y2 = 1900, 800  # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(src=roi, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(lang_list=["en"], gpu=False)

    text_res = cast(list[str], reader.readtext(image=gray_roi, detail=0))

    # check for existance of 'KILLED BY'
    return any(KILL_FEED_TRIGGER in text for text in text_res)


def detect_round_info(frame: MatLike) -> tuple[int, int, str] | None:
    """detects game state information from UI components

    Args:
        frame (MatLike): current frame capture of the gameplay

    Returns:
        tuple: (current_round, round_time, current_score) or None
    """

    def fix_ocr_time_format(time_str: str) -> int:
        """Converts a time string in 'minutes.seconds' format to total seconds"""
        # If the string contains a dot, try to treat it as a colon
        if "." in time_str:
            # Replace the dot with a colon to handle OCR misinterpretation
            time_str = time_str.replace(".", ":", 1)

        # split mins and secs
        mins, secs = time_str.split(":")
        mins = int(mins)
        secs = int(secs)

        return (mins * 60) + secs

    # region of interest
    x1, y1 = 800, 18  # top left
    x2, y2 = 1120, 80  # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(src=roi, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(lang_list=["en"], gpu=False)  # set gpu = True if have gpu

    text_res = cast(list[str], reader.readtext(gray_roi, detail=0))

    if len(text_res) == 3:
        round_time = fix_ocr_time_format(time_str=text_res[1])
        cur_round = int(text_res[0]) + int(text_res[2]) + 1
        score = f"{text_res[0]} - {text_res[2]}"

        return (cur_round, round_time, score)
    else:
        logger.error("round info reader detected invalid hud format: %s", text_res)
        return None


def detect_agent_icons(frame: MatLike) -> tuple[list[str], list[str]]:
    """given a frame during game will return a 2d array with the characters on each team

    output: [[agent_t1, agent2_t1, ...], [agent_t2, agent2_t2, ...]]
    """
    assets_folder = files(icons)

    # convert frame to grayscale
    gray_frame = cv2.cvtColor(src=frame, code=cv2.COLOR_BGR2GRAY)

    # team 1
    team1_agents: list[str] = []

    # intial ROI
    x1, y1 = 435, 30  # top left
    x2, y2 = 500, 80  # bottom right

    for _ in range(5):
        roi = cast(np.ndarray[Any, Any], gray_frame[y1:y2, x1:x2])
        # handle empty ROI (dead agents)
        if np.var(roi) < VARIANCE_THRESHOLD:
            roi_str = f"Top-left({x1}, {y1}) Bottom-right({x2}, {y2})"
            logger.info(f"variance: {np.var(roi)} is too low, empty ROI: {roi_str}")
            x1 += 65
            x2 += 65
            continue

        ret_agent = ""
        ret_threshold = 0
        for path in assets_folder.iterdir():
            if path.name.endswith(".png"):
                is_mirrored = path.name.startswith("Mirrored_")

                if is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = path.name.replace("Mirrored_", "").replace("_icon.png", "")
                try:
                    # load template using imdecode
                    with path.open("rb") as template_file:
                        agent_template = cv2.imdecode(
                            buf=np.frombuffer(template_file.read(), np.uint8),
                            flags=cv2.IMREAD_UNCHANGED,
                        )
                except Exception as error:
                    logger.error(f"Error loading {agent_name} template {error=}")
                    continue

                # random masking to avoid the background of template influencing match
                agent_template, alpha = (
                    agent_template[:, :, :3],
                    agent_template[:, :, 3],
                )
                agent_template = cv2.cvtColor(
                    src=agent_template, code=cv2.COLOR_BGR2GRAY
                )
                mask = alpha

                # template match
                result = cv2.matchTemplate(
                    image=roi,
                    templ=agent_template,
                    method=cv2.TM_CCORR_NORMED,
                    mask=mask,
                )
                loc = np.where(result >= MATCH_THRESHOLD)
                # update max match
                if loc[0].size > 0:
                    max_val = np.max(result)
                    if max_val >= MATCH_THRESHOLD:
                        if max_val > ret_threshold:
                            ret_threshold = max_val
                            ret_agent = agent_name
        logger.info(f"{ret_agent=} added to team1, with {ret_threshold=}")
        team1_agents.append(ret_agent.lower())
        x1 += 65
        x2 += 65

    # team 2
    team2_agents: list[str] = []

    # intial ROI
    x1, y1 = 1423, 30  # top left
    x2, y2 = 1488, 80  # bottom right

    for _ in range(5):
        roi = cast(np.ndarray[Any, Any], gray_frame[y1:y2, x1:x2])
        # handle empty ROI (dead agents)
        if np.var(roi) < VARIANCE_THRESHOLD:
            roi_str = f"Top-left({x1}, {y1}) Bottom-right({x2}, {y2})"
            logger.info(f"variance: {np.var(roi)} is too low, empty ROI: {roi_str}")
            x1 -= 65
            x2 -= 65
            continue

        ret_agent = ""
        ret_threshold = 0
        for path in assets_folder.iterdir():
            if path.name.endswith(".png"):
                is_mirrored = path.name.startswith("Mirrored_")

                if not is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = path.name.replace("Mirrored_", "").replace("_icon.png", "")
                try:
                    # load template using imdecode
                    with path.open("rb") as template_file:
                        agent_template = cv2.imdecode(
                            buf=np.frombuffer(template_file.read(), np.uint8),
                            flags=cv2.IMREAD_UNCHANGED,
                        )
                except Exception as error:
                    logger.error(f"Error loading {agent_name} template {error=}")
                    continue

                # random masking to avoid the background of template influencing match
                agent_template, alpha = (
                    agent_template[:, :, :3],
                    agent_template[:, :, 3],
                )
                agent_template = cv2.cvtColor(
                    src=agent_template, code=cv2.COLOR_BGR2GRAY
                )
                mask = alpha

                # template match
                result = cv2.matchTemplate(
                    image=roi,
                    templ=agent_template,
                    method=cv2.TM_CCORR_NORMED,
                    mask=mask,
                )
                loc = np.where(result >= MATCH_THRESHOLD)

                # update max match
                if loc[0].size > 0:
                    max_val = np.max(result)
                    if max_val >= MATCH_THRESHOLD:
                        if max_val > ret_threshold:
                            ret_threshold = max_val
                            ret_agent = agent_name

        logger.info(f"{ret_agent=} added to team2, with {ret_threshold=}")
        team2_agents.append(ret_agent.lower())
        x1 -= 65
        x2 -= 65

    # sort the agents for easier testing
    return (sorted(team1_agents), sorted(team2_agents))
