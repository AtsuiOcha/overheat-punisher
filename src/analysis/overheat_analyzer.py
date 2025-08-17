"""
Overheat analysis module.
Detects when monitored player takes unnecessary fights.
"""

from dataclasses import dataclass, field

from cv2.typing import MatLike

from src.detection import hud_detection


@dataclass
class FrameState:
    """Current game state."""

    frame: MatLike  
    prev_frame: MatLike | None = None

    is_mid_round: bool = field(init=False)          
    curr_seconds: int = field(init=False)
    score: str = field(init=False)
    team_diff: int = field(init=False)

    def __post_init__(self):
        # gather game state information
        round_info = hud_detection.detect_round_info(frame=self.frame)
        self.curr_seconds = round_info["round_time_sec"]
        self.score = round_info["score"]

        self.is_mid_round = (
            hud_detection.detect_round_state(frame=self.frame)
            == hud_detection.RoundState.MID_ROUND
        )

        team1, team2 = hud_detection.detect_agent_icons(frame=self.frame)

        self.team_diff = len(team1) - len(team2)

@dataclass
class OverheatEvent:
    """Detected overheat incident."""

    pass


def team_diff_at_death(prev_frame: MatLike, cur_frame: MatLike) -> int:
    # team diff at prev frame
    team1, team2 = hud_detection.detect_agent_icons(frame=prev_frame)
    prev_team_diff = len(team1) - len(team2)

    # team diff at current frame
    team1, team2 = hud_detection.detect_agent_icons(frame=cur_frame)
    curr_team_diff = len(team1) - len(team2)

    if curr_team_diff + 1 == prev_team_diff:
        # player was the only death that occured
        return curr_team_diff
    
    # reconstruct timeline from killfeed.

    



def has_team_advantage(frame: MatLike) -> bool:
    """Check if monitored player's team has numbers advantage."""
    hud_detection.detect_round_info(frame=frame)

    pass


def was_death_traded(old_state: FrameState, cur_state: FrameState) -> bool:
    """Check if death was traded within 3 seconds."""
    if old_state.team_diff 

def detect_overheat(death_frame_state: FrameState, cur_frame_state: FrameState) -> bool:
    if death_frame_state.team_diff 

