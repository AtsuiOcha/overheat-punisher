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
    team_diff: int | None
    round_time_sec: int = field(init=False)
    killer: str = field(init=False)

    def __post_init__(self):
        round_info = hud_detection.detect_round_info(frame=self.frame) 
        
        self.round_time_sec = round_info["round_time_sec"]
        if self.team_diff is None:
            team1, team2 = hud_detection.detect_agent_icons(frame=self.frame)  
            self.team_diff = len(team1) - len(team2)



@dataclass
class OverheatEvent:
    """Detected overheat incident."""

    pass


def team_diff_at_death(target_player: str, prev_frame: MatLike, cur_frame: MatLike) -> int:
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
        team_diff_at_event = team_diff_at_event - 1 if feed_event["was_team_death"] else team_diff_at_event + 1
        if feed_event["victim"].lower() == target_player.lower():
            return team_diff_at_event

    return team_diff_at_event



def has_team_advantage(frame: MatLike) -> bool:
    """Check if monitored player's team has numbers advantage."""
    hud_detection.detect_round_info(frame=frame)

    pass


def was_death_traded(old_state: FrameState, cur_state: FrameState) -> bool:
    """Check if death was traded within 3 seconds."""
    if old_state.team_diff 

def detect_overheat(death_frame_state: FrameState, cur_frame_state: FrameState) -> bool:
    if death_frame_state.team_diff 

