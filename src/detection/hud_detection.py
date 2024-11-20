import cv2
import easyocr
import numpy as np

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

    # TODO(bayunco): determine what the other detail
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
