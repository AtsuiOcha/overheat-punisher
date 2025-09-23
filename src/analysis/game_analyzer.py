"""
Overheat analysis module.
Detects when monitored player takes unnecessary fights.
"""

import time
from dataclasses import dataclass, field
from enum import Enum, auto

from cv2.typing import MatLike
from loguru import logger

from src.detection import hud_detection

PLAYER_NAME = "malding"


class AnalysisResult(Enum):
    OVERHEAT = auto()
    SAFE_CONTINUE = auto()
    SAFE_RESET = auto()


@dataclass
class FrameState:
    """Current game state."""

    frame: MatLike
    team_diff: int | None = None
    timestamp_ms: int = field(default_factory=lambda: int(time.time() * 1000))

    def __post_init__(self):
        if self.team_diff is None:
            team1, team2 = hud_detection.detect_agent_icons(frame=self.frame)
            self.team_diff = len(team1) - len(team2)


def team_diff_at_death(
    target_player: str, prev_frame: MatLike, cur_frame: MatLike
) -> int:
    # team diff at prev frame
    team1, team2 = hud_detection.detect_agent_icons(frame=prev_frame)
    prev_team_diff = len(team1) - len(team2)

    # team diff at current frame
    team1, team2 = hud_detection.detect_agent_icons(frame=cur_frame)
    curr_team_diff = len(team1) - len(team2)

    if curr_team_diff + 1 == prev_team_diff:
        # player was the only death that occured
        return curr_team_diff

    # death event reconstruction until we find score at player death
    kill_feed = hud_detection.detect_kill_feed(frame=cur_frame)
    team_diff_at_event = prev_team_diff

    for feed_event in kill_feed:
        team_diff_at_event = (
            team_diff_at_event - 1
            if feed_event["was_team_death"]
            else team_diff_at_event + 1
        )
        if feed_event["victim"].lower() == target_player.lower():
            return team_diff_at_event

    return team_diff_at_event


def check_for_death_frame(
    prev_frame: MatLike,
    frame: MatLike,
) -> FrameState | None:
    true_team_death = team_diff_at_death(
        target_player=PLAYER_NAME,
        prev_frame=prev_frame,
        cur_frame=frame,
    )

    return (
        FrameState(frame=frame, team_diff=true_team_death)
        if hud_detection.is_player_dead(frame=frame) and true_team_death >= -1
        else None
    )


def check_overheat(
    death_frame_state: FrameState, cur_frame_state: FrameState
) -> AnalysisResult:
    if not (cur_frame_state.team_diff and death_frame_state.team_diff):
        logger.error(
            f"team_diffs found to be None {cur_frame_state=} {death_frame_state=}"
        )
        raise ValueError("team diffs not set properly")

    death_traded = cur_frame_state.team_diff > death_frame_state.team_diff
    trade_window_expired = (
        cur_frame_state.timestamp_ms - death_frame_state.timestamp_ms > 3000
    )

    if trade_window_expired:
        return AnalysisResult.OVERHEAT

    return AnalysisResult.SAFE_RESET if death_traded else AnalysisResult.SAFE_CONTINUE
