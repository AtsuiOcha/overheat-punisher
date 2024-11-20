from unittest import mock
import numpy as np
from src.capture import screen_capture

# test capture screen function
def test_capture_screen():
    # mock the mss.mss() context manager and the grab method
    with mock.patch('mss.mss') as mock_mss:
        # create a mock instance of the mss.mss() object
        mock_instance = mock.Mock()
        mock_mss.return_value = mock_instance

        # Mock the context manager methods for mss instance
        mock_instance.__enter__ = mock.Mock(return_value = mock_instance)
        mock_instance.__exit__ = mock.Mock(return_value = None) # no exception handling

        # Mock the 'monitors' attribute (indexing it like an array)
        mock_instance.monitors = {1: {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}}

        # mocking the screenshot to return a NumPy array with fake data
        fake_sct = np.zeros((1080, 1920, 4), dtype=np.uint8) # fake black image in BGRA format (4 channels)
        mock_instance.grab.return_value = fake_sct

        # call the capture_screen function
        result = screen_capture.capture_screen()

        # ensure conversion to np.array in openCV BGR format (3 channels)
        assert isinstance(result, np.ndarray)
        assert result.shape == (1080, 1920, 3)

        #  ensure that the grab was called once
        mock_instance.grab.assert_called_once()
        mock_mss.assert_called_once()

        # Assert that __enter__ and __exit__ were called
        mock_instance.__enter__.assert_called_once()
        mock_instance.__exit__.assert_called_once()

def test_show_screen_capture():
    # mock the necessary parts to test show_screen_capture without opening windows
    with mock.patch('mss.mss') as mock_mss, mock.patch('cv2.imshow') as mock_imshow,\
         mock.patch('cv2.waitKey') as mock_waitkey, mock.patch('cv2.destroyAllWindows') as mock_destroy:

        # create a mock instance of the mss.mss() object
        mock_instance = mock.Mock()
        mock_mss.return_value = mock_instance

        # mock the context manager methods for the mss instance
        mock_instance.__enter__ = mock.Mock(return_value = mock_instance)
        mock_instance.__exit__ = mock.Mock(return_value = None) # no exception handling

        # Mock the 'monitors' attribute (indexing it like an array)
        mock_instance.monitors = {1: {'left': 0, 'top': 0, 'width': 1920, 'height': 1080}}

        # mocking the screenshot to return a NumPy array with fake data
        fake_sct = np.zeros((1080, 1920, 4), dtype=np.uint8) # fake black image in BGRA format (4 channels)
        mock_instance.grab.return_value = fake_sct

        # mock the behaviour of the cv2.waitKey() to simulate pressing '~' to exit the loop
        mock_waitkey.return_value = ord('~')

        # call the show_screen_capture function
        screen_capture.show_screen_capture()

        # check that imshow was called to show frame
        mock_imshow.assert_called_once_with('Screen Capture', mock.ANY)

        # check that the frame show is in the correct format (BGR)
        frame_shown = mock_imshow.call_args[0][1]
        assert frame_shown.shape == (1080, 1920, 3)

        # ensure that cv2.destroyAll windows was called
        mock_destroy.assert_called_once()

        # ensure loop exited
        mock_waitkey.assert_called_once()

