import logging
import cv2
import easyocr
import numpy as np

# Check if a root logger is already configured
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    )

# Create a logger for this specific module
logger = logging.getLogger(__name__)

def detect_kill_feed(frame: np.ndarray) -> list:
    """ detects kill feed events from the provided game frame
    """
    # region of interest
    x1, y1 = 1420, 90 # top left
    x2, y2 = 1900, 400 # bottom right
    roi = frame[y1:y2, x1:x2]

    # OCR works better on grayscale
    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(['en'], gpu=False) # set gpu = True if have gpu

    # values are maybe it can help us split guns
    text_res = reader.readtext(gray_roi, detail=0) # detail=0 means only text

    # kill feed should have even length
    if len(text_res) % 2 != 0:
        text_res = text_res[:-1]

    # Group into tuples (killer, killed)
    kill_feed = [(text_res[i], text_res[i+1]) for i in range(0, len(text_res), 2)]
    return kill_feed

def check_killed_by(frame: np.ndarray) -> bool:
    """ detects if the right side of screen contains 'KILLED BY' which indicates
        player has died during this round.
    """
    # region of interest
    x1, y1 = 1420, 220 # top left
    x2, y2 = 1900, 800 # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(['en'], gpu=False) # set gpu = True if have gpu

    text_res = reader.readtext(gray_roi, detail=0)

    # check for existance of 'KILLED BY'
    for text in text_res:
        if "KILLED BY" in text:
            return True
    return False

def detect_round_info(frame: np.ndarray) -> bool:
    """ detects if the right side of screen contains 'KILLED BY' which indicates
        player has died during this round.
    """
    def fix_ocr_time_format(time_str: str) -> str:
        """Converts a time string in 'minutes.seconds' format to total seconds"""
        # If the string contains a dot, try to treat it as a colon
        if '.' in time_str:
            # Replace the dot with a colon to handle OCR misinterpretation
            time_str = time_str.replace('.', ':', 1)

        # split mins and secs
        mins, secs = time_str.split(":")
        mins = int(mins)
        secs = int(secs)

        return (mins * 60) + secs

    # region of interest
    x1, y1 = 800, 18 # top left
    x2, y2 = 1120, 80 # bottom right
    roi = frame[y1:y2, x1:x2]

    gray_roi = cv2.cvtColor(roi, cv2.COLOR_BGR2GRAY)

    # intialize easyOCR reader
    reader = easyocr.Reader(['en'], gpu=False) # set gpu = True if have gpu

    text_res = reader.readtext(gray_roi, detail=0)
    logging.info("round info text_res= ", text_res)

    if len(text_res) == 3:
        round_time = fix_ocr_time_format(text_res[1])
        cur_round = int(text_res[0]) + int(text_res[2]) + 1
        score = f"{text_res[0]} - {text_res[2]}"

        return (cur_round, round_time, score)
    else:
        logging.error("round info reader detected invalid hud format: ", text_res)
        return None
