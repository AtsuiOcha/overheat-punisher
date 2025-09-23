import threading

from cv2.typing import MatLike
from loguru import logger
from rich import print

from src.analysis import FrameState, check_for_death_frame, check_overheat
from src.analysis.game_analyzer import AnalysisResult
from src.capture import capture_screen

running = False
player_name = ""


def loop():
    global running, player_name
    death_frame_state: FrameState | None = None
    prev_frame: MatLike | None = None
    while running:
        # capture frame
        cur_frame = capture_screen()

        # ensure an intial frame has been read
        if prev_frame is not None:
            if not death_frame_state:
                death_frame_state = check_for_death_frame(
                    prev_frame=prev_frame,
                    frame=cur_frame,
                    player_name=player_name,
                )
                if death_frame_state is not None:
                    print("[red]DEATH FRAME FOUND[/red]")
            else:
                anal_res = check_overheat(
                    death_frame_state=death_frame_state,
                    cur_frame_state=FrameState(cur_frame),
                )

                if anal_res == AnalysisResult.OVERHEAT:
                    print("[red]OVERHEAT MOTHAFUCKAAAAAA![/red]")
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
    global running, player_name

    # Get player name from user
    print("Welcome to Overheat Punisher!")
    player_name = input("Enter your player name: ").strip()
    if not player_name:
        print("Player name cannot be empty. Exiting.")
        return

    print(f"Monitoring player: {player_name}")
    print("Commands: 'start' to begin monitoring, 'stop' to pause, 'quit' to exit")

    while True:
        try:
            command = input("> ").strip().lower()
            if command in ["start", "s"]:
                if not running:
                    toggle_loop()
                else:
                    print("Already running")
            elif command in ["stop", "p"]:
                if running:
                    toggle_loop()
                else:
                    print("Already stopped")
            elif command in ["quit", "q", "exit"]:
                break
            else:
                print("Commands: start, stop, quit")
        except KeyboardInterrupt:
            break

    # cleanly exit if loop is running
    if running:
        logger.info("Exiting, stopping loop")
        running = False


if __name__ == "__main__":
    main()
