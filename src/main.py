"""
Main loop for real-time overheat detection.
Target: 20 FPS analysis with smart sampling.
"""

from cv2.typing import MatLike

from .analysis import FrameState, detect_overheat, team_diff_at_death
from .capture import capture_screen
from .detection import RoundState, detect_round_state, is_player_dead

PLAYER_NAME = "malding"


def get_death_frame_state(
    prev_frame: MatLike,
    frame: MatLike,
    prev_death_frame_state: FrameState | None,
) -> FrameState | None:
    if prev_death_frame_state:
        # do some stuff
        ...
    round_state = detect_round_state(frame=frame)
    true_team_death = team_diff_at_death(
        target_player=PLAYER_NAME,
        prev_frame=prev_frame,
        cur_frame=frame,
    )
    # TODO: there might be an issue here when we are mid round but looking at score
    if (
        round_state == RoundState.MID_ROUND
        and is_player_dead(frame=frame)
        and true_team_death >= -1
    ):
        return FrameState(
            frame=frame,
            team_diff=true_team_death,
        )
    return None


# TODO: get away from using a detection state we can use the existence of a death state
#   for determing weather we are to look for some overheat event or not


def main():
    death_frame_state: FrameState | None = None
    prev_frame: MatLike | None = None
    while True:
        # capture frame
        cur_frame = capture_screen()

        # ensure an intial frame has been read
        if prev_frame:
            curr_detection_state = get_death_frame_state(
                prev_frame=prev_frame,
                frame=cur_frame,
                prev_detection_state=detection_state,
            )

            # reset if we notice round change
            if (
                detection_state == DetectionState.ANALYZING
                and curr_detection_state == DetectionState.MONITORING
            ):
                death_frame_state = None

            detection_state = curr_detection_state
            if curr_detection_state == DetectionState.ANALYZING:
                # set death frame
                if not death_frame_state:
                    death_frame_state = FrameState(
                        frame=cur_frame, prev_frame=prev_frame
                    )
                    prev_frame = cur_frame
                    continue
                if detect_overheat(
                    death_frame_state=death_frame_state,
                    cur_frame_state=FrameState(frame=cur_frame),
                ):
                    # notify here
                    ...

        prev_frame = cur_frame


if __name__ == "__main__":
    main()
