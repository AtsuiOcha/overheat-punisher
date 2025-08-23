import threading

import keyboard
from cv2.typing import MatLike
from loguru import logger

from .analysis import FrameState, check_overheat, team_diff_at_death
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


running = False


def loop():
    global running
    round_state: RoundState = RoundState.PRE_ROUND
    death_frame_state: FrameState | None = None
    prev_frame: MatLike | None = None
    while running:
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
                if check_overheat(
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


def toggle_loop():
    global running
    if running:
        logger.info("Stopping loop")
        running = False
    else:
        logger.info("Starting loop")
        running = True
        threading.Thread(target=loop, daemon=True).start()


def main():
    global running
    print("Press F9 to toggle the loop on/off. Press press F10 to quit the program.")
    _ = keyboard.add_hotkey("F9", toggle_loop)
    keyboard.wait("F10")

    # cleanly exit if loop is running
    if running:
        logger.info("Exiting, stopping loop")
        running = False


if __name__ == "__main__":
    main()
