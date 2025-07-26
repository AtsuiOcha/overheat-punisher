import os

import cv2
import easyocr
import numpy as np
from loguru import logger


VARIANCE_THRESHOLD = 800
MATCH_THRESHOLD = 0.9


def detect_kill_feed(frame: np.ndarray) -> list:
    """detects kill feed events from the provided game frame"""
    # region of interest
    x1, y1 = 1420, 90  # top left
    x2, y2 = 1900, 400  # bottom right
    roi = frame[y1:y2, x1:x2]

    # OCR works better on grayscale
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(["en"], gpu=False)  # set gpu = True if have gpu

    # values are maybe it can help us split guns
    text_res = reader.readtext(gray_roi, detail=0)  # detail=0 means only text

    # kill feed should have even length
    if len(text_res) % 2 != 0:
        text_res = text_res[:-1]

    # Group into tuples (killer, killed)
    kill_feed = [(text_res[i], text_res[i + 1]) for i in range(0, len(text_res), 2)]
    return kill_feed


def is_player_dead(frame: np.ndarray) -> bool:
    """detects if player is dead.

    Args:
        frame (np.ndarray) current frame capture of gameplay

    Returns:
        bool: True if player is dead, False otherwise
    """
    # region of interest
    x1, y1 = 1420, 220  # top left
    x2, y2 = 1900, 800  # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(["en"], gpu=False)  # set gpu = True if have gpu

    text_res = reader.readtext(gray_roi, detail=0)

    # check for existance of 'KILLED BY'
    for text in text_res:
        if "KILLED BY" in text:
            return True
    return False


def detect_round_info(frame: np.ndarray) -> tuple | None:
    """detects game state information from UI components

    Args:
        frame (np.ndarray): current frame capture of the gameplay

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

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(["en"], gpu=False)  # set gpu = True if have gpu

    text_res = reader.readtext(gray_roi, detail=0)
    logging.info("round info text_res= %s", text_res)

    if len(text_res) == 3:
        round_time = fix_ocr_time_format(str(text_res[1]))
        cur_round = int(text_res[0]) + int(text_res[2]) + 1  # type: ignore
        score = f"{text_res[0]} - {text_res[2]}"

        return (cur_round, round_time, score)
    else:
        logging.error("round info reader detected invalid hud format: %s", text_res)
        return None


def detect_agent_icons(frame: np.ndarray) -> tuple:
    """given a frame during game will return a 2d array with the characters on each team

    output: [[agent_t1, agent2_t1, ...], [agent_t2, agent2_t2, ...]]
    """
    # TODO(bayunco): will using os.path cause issue in packaging this up as application for other pcs?
    # Adjust the assets_folder path to go up from detection and then down to assets
    assets_folder = os.path.join(
        os.path.dirname(__file__), "../assets/agent_icons_clean"
    )
    # Normalize path to handle cross-platform issues
    assets_folder = os.path.abspath(assets_folder)

    # convert frame to grayscale
    gray_frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

    # team 1
    team1_agents = []

    # intial ROI
    x1, y1 = 435, 30  # top left
    x2, y2 = 500, 80  # bottom right

    for _ in range(5):
        roi = gray_frame[y1:y2, x1:x2]
        # handle empty ROI (dead agents)
        if np.var(roi) < VARIANCE_THRESHOLD:
            roi_str = f"Top-left({x1}, {y1}) Bottom-right({x2}, {y2})"
            logger.info(f"variance: {np.var(roi)} is too low, empty ROI: {roi_str}")
            x1 += 65
            x2 += 65
            continue

        ret_agent = ""
        ret_threshold = 0
        for filename in os.listdir(assets_folder):
            if filename.endswith(".png"):
                is_mirrored = filename.startswith("Mirrored_")

                if is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = filename.replace("Mirrored_", "").replace("_icon.png", "")
                agent_template = cv2.imread(
                    os.path.join(assets_folder, filename), cv2.IMREAD_UNCHANGED
                )

                # random masking to avoid the background of template influencing match
                agent_template, alpha = (
                    agent_template[:, :, :3],
                    agent_template[:, :, 3],
                )
                agent_template = cv2.cvtColor(agent_template, cv2.COLOR_BGR2GRAY)
                mask = alpha

                # template match
                result = cv2.matchTemplate(
                    roi, agent_template, cv2.TM_CCORR_NORMED, mask=mask
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
    team2_agents = []

    # intial ROI
    x1, y1 = 1423, 30  # top left
    x2, y2 = 1488, 80  # bottom right

    for _ in range(5):
        roi = gray_frame[y1:y2, x1:x2]
        # handle empty ROI (dead agents)
        if np.var(roi) < VARIANCE_THRESHOLD:
            roi_str = f"Top-left({x1}, {y1}) Bottom-right({x2}, {y2})"
            logger.info(f"variance: {np.var(roi)} is too low, empty ROI: {roi_str}")
            x1 -= 65
            x2 -= 65
            continue

        ret_agent = ""
        ret_threshold = 0
        for filename in os.listdir(assets_folder):
            if filename.endswith(".png"):
                is_mirrored = filename.startswith("Mirrored_")

                if not is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = filename.replace("Mirrored_", "").replace("_icon.png", "")
                agent_template = cv2.imread(
                    os.path.join(assets_folder, filename), cv2.IMREAD_UNCHANGED
                )

                # random masking to avoid the background of template influencing match
                agent_template, alpha = (
                    agent_template[:, :, :3],
                    agent_template[:, :, 3],
                )
                agent_template = cv2.cvtColor(agent_template, cv2.COLOR_BGR2GRAY)
                mask = alpha

                # template match
                result = cv2.matchTemplate(
                    roi, agent_template, cv2.TM_CCORR_NORMED, mask=mask
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

