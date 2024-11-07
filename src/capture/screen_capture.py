import mss
import cv2
import numpy as np

def main():
    with mss.mss() as sct:
        monitor = sct.monitors[1]

        while True:
            # capture a frame
            screenshot = sct.grab(monitor)

            # convert the image to a numpy array
            frame = np.array(screenshot)

            # convert to OpenCV BGR format
            frame = cv2.cvtColor(frame, cv2.COLOR_BGRA2BGR)

            # Display the frame in a window 
            cv2.imshow('Screen Capture', frame)

            # exit on 'l' key press for "leave"
            if cv2.waitKey(1) & 0xFF == ord('~'):
                break

        # release resources
        cv2.destroyAllWindows()

if __name__ == "__main__":
    main()
