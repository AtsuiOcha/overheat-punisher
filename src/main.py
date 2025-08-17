"""
Main loop for real-time overheat detection.
Target: 20 FPS analysis with smart sampling.
"""

from enum import Enum

from cv2.typing import MatLike

from .analysis import FrameState, detect_overheat, team_diff_at_death
from .capture import capture_screen
from .detection import RoundState, detect_round_state, is_player_dead


class DetectionState(Enum):
    MONITORING = 1
    ANALYZING = 2


def determine_detection_state(
    prev_frame: MatLike,
    frame: MatLike,
    prev_detection_state: DetectionState,
) -> DetectionState:
    round_state = detect_round_state(frame=frame)
    # TODO: there might be an issue here when we are mid round but looking at score
    if (
        prev_detection_state == DetectionState.MONITORING
        and round_state == RoundState.MID_ROUND
        and is_player_dead(frame=frame)
        and team_diff_at_death(prev_frame=prev_frame, cur_frame=frame) >= -1
    ):
        return DetectionState.ANALYZING

    return DetectionState.MONITORING


# might be best to use actual current round to determine round determine when to reset.


def main():
    detection_state = DetectionState.MONITORING
    death_frame_state: FrameState | None = None
    prev_frame: MatLike | None = None
    while True:
        # capture frame
        cur_frame = capture_screen()

        # ensure an intial frame has been read
        if prev_frame:
            curr_detection_state = determine_detection_state(
                prev_frame=prev_frame,
                frame=cur_frame,
                prev_detection_state=detection_state,
            )

            # reset if we notice round change
            if (
                detection_state == DetectionState.ANALYZING
                and curr_detection_state == DetectionState.MONITORING
            ):
                frame_state = None
                death_frame_state = None
                detection_state = curr_detection_state

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
