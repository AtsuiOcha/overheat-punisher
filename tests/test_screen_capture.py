from typing import Dict, List, Optional
from unittest import mock

import numpy as np
import pytest
from numpy.typing import NDArray

from src.capture import screen_capture


class MockScreenshot:
    """Mock MSS screenshot object that behaves like the real one."""

    def __init__(self, width: int = 1920, height: int = 1080) -> None:
        self.width: int = width
        self.height: int = height
        # Create BGRA fake data that np.array() can convert
        self._data: NDArray[np.uint8] = np.zeros((height, width, 4), dtype=np.uint8)

    def __array__(
        self, dtype: Optional[type] = None, copy: Optional[bool] = None
    ) -> NDArray[np.uint8]:
        """Called when np.array(screenshot) is used."""
        return self._data


@pytest.fixture
def mock_screenshot() -> MockScreenshot:
    """Pytest fixture that provides a mock screenshot for testing.

    Returns:
        MockScreenshot: A mock screenshot object with default 1920x1080 dimensions.
    """
    return MockScreenshot(1920, 1080)


@pytest.fixture
def mock_mss_context():
    """Pytest fixture that provides a mock MSS context manager.

    Yields:
        tuple: (mock_mss, mock_instance) for use in tests.
    """
    with mock.patch("mss.mss") as mock_mss:
        # create a mock instance of the mss.mss() object
        mock_instance = mock.Mock()
        mock_mss.return_value = mock_instance

        # Mock the context manager methods for mss instance
        mock_instance.__enter__ = mock.Mock(return_value=mock_instance)
        mock_instance.__exit__ = mock.Mock(return_value=None)

        # Mock the 'monitors' attribute as a list (MSS uses list-like access)
        mock_instance.monitors = [
            None,  # index 0 is not used
            {
                "left": 0,
                "top": 0,
                "width": 1920,
                "height": 1080,
            },  # primary monitor at index 1
        ]

        yield mock_mss, mock_instance


@pytest.mark.unit
def test_capture_screen(
    mock_mss_context: tuple[mock.Mock, mock.Mock], mock_screenshot: MockScreenshot
) -> None:
    mock_mss, mock_instance = mock_mss_context
    mock_instance.grab.return_value = mock_screenshot

    # call the capture_screen function
    result: NDArray[np.uint8] = screen_capture.capture_screen()

    # ensure conversion to np.array in openCV BGR format (3 channels)
    assert isinstance(result, np.ndarray)
    assert result.shape == (1080, 1920, 3)

    #  ensure that the grab was called once
    mock_instance.grab.assert_called_once()
    mock_mss.assert_called_once()

    # Assert that __enter__ and __exit__ were called
    mock_instance.__enter__.assert_called_once()
    mock_instance.__exit__.assert_called_once()


@pytest.mark.unit
def test_show_screen_capture(mock_screenshot: MockScreenshot) -> None:
    # mock the necessary parts to test show_screen_capture without opening windows
    with (
        mock.patch("mss.mss") as mock_mss,
        mock.patch("cv2.imshow") as mock_imshow,
        mock.patch("cv2.waitKey") as mock_waitkey,
        mock.patch("cv2.destroyAllWindows") as mock_destroy,
    ):
        # create a mock instance of the mss.mss() object
        mock_instance = mock.Mock()
        mock_mss.return_value = mock_instance

        # mock the context manager methods for the mss instance
        mock_instance.__enter__ = mock.Mock(return_value=mock_instance)
        mock_instance.__exit__ = mock.Mock(return_value=None)

        # Mock the 'monitors' attribute as a list (MSS uses list-like access)
        mock_instance.monitors: List[Optional[Dict[str, int]]] = [
            None,  # index 0 is not used
            {
                "left": 0,
                "top": 0,
                "width": 1920,
                "height": 1080,
            },  # primary monitor at index 1
        ]

        mock_instance.grab.return_value = mock_screenshot

        # mock the behaviour of the cv2.waitKey() to simulate pressing '~' to exit the loop
        mock_waitkey.return_value = ord("~")

        # call the show_screen_capture function
        screen_capture.show_screen_capture()

        # check that imshow was called to show frame (with keyword arguments)
        mock_imshow.assert_called_once_with(winname="Screen Capture", mat=mock.ANY)

        # check that the frame show is in the correct format (BGR)
        frame_shown: NDArray[np.uint8] = mock_imshow.call_args.kwargs["mat"]
        assert frame_shown.shape == (1080, 1920, 3)

        # ensure that cv2.destroyAll windows was called
        mock_destroy.assert_called_once()

        # ensure loop exited
        mock_waitkey.assert_called
