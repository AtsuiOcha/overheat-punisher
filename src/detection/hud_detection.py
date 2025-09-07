"""
HUD detection module for Valorant gameplay analysis.

This module provides computer vision and OCR functionality to extract game state
information from Valorant screenshots, including kill feed events, player death
status, round information, and agent compositions using template matching.

Constants:
    VARIANCE_THRESHOLD (int): Minimum variance for valid agent icon regions (800)
    MATCH_THRESHOLD (float): Template matching confidence threshold (0.9)
    KILL_FEED_TRIGGER (str): Text trigger for death detection ("KILLED BY")
"""

from enum import Enum
from importlib.resources import files
from typing import Any, TypedDict, cast

import cv2
import easyocr
import numpy as np
import torch
from cv2.typing import MatLike
from loguru import logger
from pydantic import BaseModel, ValidationError

import src.assets.agent_icons_clean as icons

VARIANCE_THRESHOLD = 800
MATCH_THRESHOLD = 0.9
KILL_FEED_TRIGGER = "KILLED BY"


class OcrResult(BaseModel):
    bbox: list[tuple[int, int]]
    text: str
    confidence: float


class KillFeedLine(TypedDict):
    killer: str
    victim: str
    was_team_death: bool


class RoundInfo(TypedDict):
    cur_round: int
    round_time_sec: int
    score: str


class RoundState(Enum):
    """Represents the current round state in Valorant."""

    PRE_ROUND = 1
    MID_ROUND = 2
    POST_ROUND = 3


MATCH_MAP = {
    # pre round matches
    "buy phase": RoundState.PRE_ROUND,
    # post round
    "lost": RoundState.POST_ROUND,
    "won": RoundState.POST_ROUND,
    "clutch": RoundState.POST_ROUND,
    "ace": RoundState.POST_ROUND,
}


def classify_team_death_event(patch: MatLike) -> bool:
    mean_color = patch.mean(axis=(0, 1))
    blue, green, red = mean_color

    # we force cast that fucky np.bool_ to python bool
    return bool(red <= max(blue, green) * 1.2)


def crop_patch(roi: MatLike, bbox: list[tuple[int, int]]) -> MatLike:
    xs = [p[0] for p in bbox]
    ys = [p[1] for p in bbox]
    return roi[int(min(ys)) : int(max(ys)), int(min(xs)) : int(max(xs))]


def detect_kill_feed(frame: MatLike) -> list[KillFeedLine]:
    # region of interest
    roi_x_min, roi_y_min = 1420, 90
    roi_x_max, roi_y_max = 1900, 400
    roi_color = frame[roi_y_min:roi_y_max, roi_x_min:roi_x_max]

    # OCR works better on grayscale
    gray_roi = cv2.cvtColor(src=roi_color, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(lang_list=["en"], gpu=torch.cuda.is_available())

    raw_ocr = reader.readtext(image=gray_roi, detail=1)

    try:
        ocr_res = [
            OcrResult(bbox=bbox, text=text, confidence=conf)
            for (bbox, text, conf) in raw_ocr
        ]
        if len(ocr_res) % 2 != 0:
            ocr_res = ocr_res[:-1]
    except ValidationError as val_err:
        logger.error(f"OCR validation failed: {val_err=}")
        raise

    return [
        KillFeedLine(
            killer=ocr_res[i].text,
            victim=ocr_res[i + 1].text,
            was_team_death=classify_team_death_event(
                patch=crop_patch(
                    roi_color,
                    ocr_res[i + 1].bbox,
                ),
            ),
        )
        for i in range(0, len(ocr_res), 2)
    ]


def is_player_dead(frame: MatLike) -> bool:
    """Detects if the player is currently dead.

    Scans the kill feed region for the "KILLED BY" trigger text which appears
    when the player has been eliminated. Uses OCR to analyze the text content
    in the designated region of interest.

    Args:
        frame (MatLike): Current frame capture of gameplay in BGR format.

    Returns:
        bool: True if player is dead (KILLED BY text found), False otherwise.

    Note:
        - Detection region: (1420, 220) to (1900, 800)
        - Uses grayscale conversion for improved OCR performance
        - Searches for KILL_FEED_TRIGGER constant in detected text
    """
    # region of interest
    x1, y1 = 1420, 220  # top left
    x2, y2 = 1900, 800  # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(src=roi, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(lang_list=["en"], gpu=torch.cuda.is_available())

    text_res = cast(list[str], reader.readtext(image=gray_roi, detail=0))
    logger.info(f"easyocr reader found {text_res=}")

    # check for existance of 'KILLED BY'
    return any(KILL_FEED_TRIGGER in text for text in text_res)


def detect_round_info(frame: MatLike) -> RoundInfo:
    """Detects game state information from UI components.

    Extracts round number, remaining time, and current score from the top HUD area.
    The function expects three OCR elements: team1_score, time, team2_score.

    Args:
        frame (MatLike): Current frame capture of the gameplay in BGR format.

    Returns:
        tuple[int, int, str] | None: (current_round, round_time_seconds, score_string)
        Returns None if detection fails or invalid HUD format detected.

    Note:
        - Detection region: (800, 18) to (1120, 80)
        - Time format is converted from MM:SS or MM.SS to total seconds
        - Current round calculated as: team1_score + team2_score + 1
        - Score format: "team1_score - team2_score"
    """

    def fix_ocr_time_format(time_str: str) -> int:
        """Converts a time string in 'minutes.seconds' format to total seconds.

        Handles OCR misinterpretation where colons may be detected as dots.

        Args:
            time_str (str): Time string in format "MM:SS" or "MM.SS"

        Returns:
            int: Total time in seconds
        """
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
    reader = easyocr.Reader(
        lang_list=["en"], gpu=torch.cuda.is_available()
    )  # set gpu = True if have gpu

    text_res = cast(list[str], reader.readtext(gray_roi, detail=0))
    logger.info(f"easyocr reader found {text_res=}")

    if len(text_res) != 3:
        # TODO: make custom exception for hud_detection
        raise ValueError(f"Error getting round_info information {len(text_res)}")

    round_time = fix_ocr_time_format(time_str=text_res[1])
    cur_round = int(text_res[0]) + int(text_res[2]) + 1
    score = f"{text_res[0]} - {text_res[2]}"

    return RoundInfo(
        cur_round=cur_round,
        round_time_sec=round_time,
        score=score,
    )


def detect_agent_icons(frame: MatLike) -> tuple[list[str], list[str]]:
    """Detects agent compositions for both teams using template matching.

    Analyzes the top HUD area to identify all 10 agent icons (5 per team) using
    template matching with pre-processed agent icon images. Team 1 uses normal
    icons while Team 2 uses horizontally mirrored versions.

    Args:
        frame (MatLike): Game screenshot frame in BGR format.

    Returns:
        tuple[list[str], list[str]]: (team1_agents, team2_agents) where each list
        contains sorted agent names in lowercase. Lists may be shorter than 5
        if agents are dead (empty regions detected).

    Note:
        - Team 1 region: starts at (435, 30), moves right by 65px per agent
        - Team 2 region: starts at (1423, 30), moves left by 65px per agent
        - Uses VARIANCE_THRESHOLD to skip empty regions (dead agents)
        - Template matching threshold: MATCH_THRESHOLD (0.9)
        - Agent names returned in lowercase and sorted alphabetically
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
            if path.name.endswith(".webp"):
                is_mirrored = path.name.startswith("Mirrored_")

                if is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = path.name.replace("Mirrored_", "").replace(
                    "_icon.webp", ""
                )
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
            if path.name.endswith(".webp"):
                is_mirrored = path.name.startswith("Mirrored_")

                if not is_mirrored:
                    continue

                # load agent icon and get agent name
                agent_name = path.name.replace("Mirrored_", "").replace(
                    "_icon.webp", ""
                )
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


def detect_round_state(frame: MatLike) -> RoundState:
    # region of interest
    x1, y1 = 800, 140  # top left
    x2, y2 = 1145, 275  # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(src=roi, code=cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(
        lang_list=["en"], gpu=torch.cuda.is_available()
    )  # set gpu = True if have gpu

    text_res = cast(list[str], reader.readtext(gray_roi, detail=0))
    logger.info(f"easyocr reader found {text_res=}")

    return next(
        (MATCH_MAP[word.lower()] for word in text_res if word.lower() in MATCH_MAP),
        RoundState.MID_ROUND,
    )
