"""
Main loop for real-time overheat detection.
Target: 20 FPS analysis with smart sampling.
"""

from cv2.typing import MatLike

from .analysis import FrameState, detect_overheat, team_diff_at_death
from .capture import capture_screen
from .detection import RoundState, detect_round_state, is_player_dead

PLAYER_NAME = "malding"


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
        if is_player_dead(frame=frame) and true_team_death >= -1
        else None
    )


def main():
    round_state: RoundState = RoundState.PRE_ROUND
    death_frame_state: FrameState | None = None
    prev_frame: MatLike | None = None
    while True:
        # capture frame
        cur_frame = capture_screen()

        # ensure an intial frame has been read
        if prev_frame:
            if not death_frame_state:
                death_frame_state = check_for_death_frame(
                    prev_frame=prev_frame,
                    frame=cur_frame,
                )
                round_state = RoundState.MID_ROUND
            else:
                if detect_overheat(
                    death_frame_state=death_frame_state,
                    cur_frame_state=FrameState(frame=cur_frame),
                ):
                    # notify here
                    ...

                # reset as we've moved to the next round
                if (
                    new_round_state := detect_round_state(frame=cur_frame)
                ) != round_state:
                    round_state = new_round_state
                    death_frame_state = None

        prev_frame = cur_frame


if __name__ == "__main__":
    main()
