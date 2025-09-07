import threading

import keyboard
from cv2.typing import MatLike
from loguru import logger

from src.analysis.game_analyzer import AnalysisResult

from .analysis import FrameState, check_for_death_frame, check_overheat
from .capture import capture_screen

running = False


def loop():
    global running
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
            else:
                anal_res = check_overheat(
                    death_frame_state=death_frame_state,
                    cur_frame_state=FrameState(cur_frame),
                )

                if anal_res == AnalysisResult.OVERHEAT:
                    ...  # notify
                elif anal_res == AnalysisResult.SAFE_RESET:
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
